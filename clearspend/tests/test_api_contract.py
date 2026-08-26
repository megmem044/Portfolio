"""Assert ClearSpend's deliberate HTTP status, body, and media-type contract."""


def csv_upload(client, content: str, filename: str = "bank.csv"):
    return client.post(
        "/imports/upload",
        files={"file": (filename, content, "text/csv")},
        data={
            "source": "contract-test",
            "mapping": '{"date":"date","merchant":"merchant","amount":"amount"}',
        },
    )


def second_user_headers(client):
    client.post(
        "/auth/register",
        json={"email": "contract-user@example.com", "password": "StrongPass123"},
    )
    token = client.post(
        "/auth/login",
        json={"email": "contract-user@example.com", "password": "StrongPass123"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_successful_import_contract_uses_json_and_expected_2xx_codes(client):
    staged = csv_upload(
        client,
        "date,merchant,amount\n2026-08-01,Contract Store,10.00\n",
    )
    assert staged.status_code == 201
    assert staged.headers["content-type"].startswith("application/json")
    assert staged.json()["state"] == "ready"

    committed = client.post(f"/imports/{staged.json()['id']}/commit", json={})
    assert committed.status_code == 200
    assert committed.headers["content-type"].startswith("application/json")
    assert committed.json()["reconciled"] is True


def test_malformed_upload_contract_returns_validation_detail(client):
    empty = csv_upload(client, "date,merchant,amount\n")
    wrong_extension = csv_upload(
        client,
        "date,merchant,amount\n2026-08-01,Store,1.00\n",
        filename="bank.txt",
    )
    missing_multipart = client.post(
        "/imports/upload",
        json={"csv_content": "not multipart"},
    )

    for response in (empty, wrong_extension, missing_multipart):
        assert response.status_code == 422
        assert response.headers["content-type"].startswith("application/json")
        assert "detail" in response.json()


def test_oversized_upload_returns_payload_too_large(client):
    content = "date,merchant,amount\n" + ("2026-08-01,Store,1.00\n" * 240_000)
    response = csv_upload(client, content)

    assert response.status_code == 413
    assert response.json() == {"detail": "file exceeds the 5 MiB limit"}


def test_authentication_and_owner_hiding_contract(client):
    staged = csv_upload(
        client,
        "date,merchant,amount\n2026-08-01,Private Store,10.00\n",
    ).json()

    unauthorized = client.get(
        f"/imports/{staged['id']}",
        headers={"Authorization": ""},
    )
    hidden = client.get(
        f"/imports/{staged['id']}",
        headers=second_user_headers(client),
    )

    assert unauthorized.status_code == 401
    assert unauthorized.json()["detail"] == "valid authentication is required"
    assert unauthorized.headers["www-authenticate"] == "Bearer"
    assert hidden.status_code == 404
    assert hidden.json() == {"detail": "import not found"}


def test_conflict_idempotency_and_invalid_state_contract(client):
    content = "date,merchant,amount\n2026-08-01,Store,10.00\n"
    first = csv_upload(client, content).json()
    competing = csv_upload(client, content).json()
    first_commit = client.post(f"/imports/{first['id']}/commit", json={})
    repeated = client.post(f"/imports/{first['id']}/commit", json={})
    conflict = client.post(f"/imports/{competing['id']}/commit", json={})
    row_id = first["rows"][0]["id"]
    invalid_state = client.patch(
        f"/imports/{first['id']}/rows/{row_id}",
        json={"decision": "approve"},
    )

    assert first_commit.status_code == repeated.status_code == 200
    assert first_commit.json() == repeated.json()
    assert conflict.status_code == 409
    assert "detail" in conflict.json()
    assert invalid_state.status_code == 409
    assert invalid_state.json() == {"detail": "only ready imports can be reviewed"}


def test_pagination_and_method_contract(client):
    staged = csv_upload(
        client,
        "date,merchant,amount\n2026-08-01,Store,10.00\n",
    ).json()

    invalid_page = client.get(f"/imports/{staged['id']}", params={"page": 0})
    invalid_size = client.get(
        f"/imports/{staged['id']}",
        params={"page_size": 501},
    )
    wrong_method = client.delete(f"/imports/{staged['id']}")

    assert invalid_page.status_code == invalid_size.status_code == 422
    assert wrong_method.status_code == 405
    assert wrong_method.json() == {"detail": "Method Not Allowed"}


def test_csv_export_contract(client):
    client.post(
        "/transactions/",
        json={"date": "2026-08-01", "merchant": "Export Store", "amount": "4.25"},
    )
    response = client.get("/transactions/export.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == (
        "attachment; filename=clearspend-transactions.csv"
    )
    assert response.text.startswith("date,merchant,category,amount\n")
