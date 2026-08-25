"""Exercise staging, validation, deduplication, commit, and reconciliation."""


def stage(client, csv_content, mapping=None):
    payload = {"filename": "bank.csv", "source": "test-bank", "csv_content": csv_content}
    if mapping:
        payload["mapping"] = mapping
    return client.post("/imports/", json=payload)


def test_stage_preserves_every_row_and_explains_invalid_data(client):
    response = stage(client, "date,merchant,amount,currency\n2026-08-01,  Coffee Shop  ,4.25,cad\nbad-date,Store,10.00,CAD\n")
    assert response.status_code == 201
    body = response.json()
    assert body["state"] == "ready"
    assert body["input_count"] == 2
    assert body["invalid_count"] == 1
    assert body["rows"][0]["merchant"] == "Coffee Shop"
    assert body["rows"][0]["currency"] == "CAD"
    assert body["rows"][1]["status"] == "invalid"
    assert "supported format" in body["rows"][1]["error_reason"]


def test_custom_mapping_and_debit_column_commit_reconciles(client):
    staged = stage(client, "Posted,Description,Debit\n08/01/2026,Starbucks,8.50\n08/02/2026,Uber,12.25\n", {"date": "Posted", "merchant": "Description", "amount": None, "debit": "Debit"}).json()
    result = client.post(f"/imports/{staged['id']}/commit", json={})
    assert result.status_code == 200
    assert result.json() == {"import_id": staged["id"], "state": "committed", "input_count": 2, "imported_count": 2, "duplicate_count": 0, "invalid_count": 0, "rejected_count": 0, "accounted_count": 2, "reconciled": True, "accepted_total": "20.75", "saved_total": "20.75"}
    assert client.get("/transactions/").json()["total"] == 2


def test_retrying_same_file_is_idempotent(client):
    content = "date,merchant,amount\n2026-08-01,Store,10.00\n"
    first = stage(client, content).json()
    client.post(f"/imports/{first['id']}/commit", json={})
    second = stage(client, content).json()
    assert second["rows"][0]["status"] == "exact_duplicate"
    report = client.post(f"/imports/{second['id']}/commit", json={}).json()
    assert report["duplicate_count"] == 1
    assert report["reconciled"] is True
    assert client.get("/transactions/").json()["total"] == 1


def test_possible_duplicate_requires_explicit_decision(client):
    first = stage(client, "date,merchant,amount\n2026-08-01,Store A,10.00\n").json()
    client.post(f"/imports/{first['id']}/commit", json={})
    second = stage(client, "date,merchant,amount\n2026-08-01,Store B,10.00\n").json()
    assert second["rows"][0]["status"] == "possible_duplicate"
    report = client.post(f"/imports/{second['id']}/commit", json={}).json()
    assert report["rejected_count"] == 1
    assert report["reconciled"] is True


def test_empty_or_unmapped_csv_is_rejected(client):
    assert stage(client, "date,merchant,amount\n").status_code == 422
    response = stage(client, "when,who,value\n2026-01-01,Store,1.00\n")
    assert response.status_code == 422
    assert "mapped columns not found" in response.json()["detail"]


def test_imports_are_private(client):
    imported = stage(client, "date,merchant,amount\n2026-08-01,Store,10.00\n").json()
    client.post("/auth/register", json={"email": "other@example.com", "password": "StrongPass123"})
    token = client.post("/auth/login", json={"email": "other@example.com", "password": "StrongPass123"}).json()["access_token"]
    assert client.get(f"/imports/{imported['id']}", headers={"Authorization": f"Bearer {token}"}).status_code == 404


def test_streamed_upload_is_paginated_and_records_metrics(client):
    content = "date,merchant,amount\n" + "\n".join(f"2026-08-{(n % 28) + 1:02d},Store {n},{n + 1}.00" for n in range(125))
    response = client.post("/imports/upload", files={"file": ("bank.csv", content, "text/csv")}, data={"source": "test", "mapping": '{"date":"date","merchant":"merchant","amount":"amount"}'})
    assert response.status_code == 201
    body = response.json()
    assert body["input_count"] == 125
    assert len(body["rows"]) == 100
    assert body["row_total"] == 125
    assert float(body["rows_per_second"]) > 0
    second = client.get(f"/imports/{body['id']}", params={"page": 2, "page_size": 100}).json()
    assert len(second["rows"]) == 25


def test_presets_and_explicit_possible_duplicate_review(client):
    assert len(client.get("/imports/presets").json()) >= 3
    first = stage(client, "date,merchant,amount\n2026-08-01,Store A,10.00\n").json()
    client.post(f"/imports/{first['id']}/commit", json={})
    second = stage(client, "date,merchant,amount\n2026-08-01,Store B,10.00\n").json()
    row = second["rows"][0]
    reviewed = client.patch(f"/imports/{second['id']}/rows/{row['id']}", json={"decision": "approve"})
    assert reviewed.status_code == 200
    assert reviewed.json()["rows"][0]["review_decision"] == "approve"
    report = client.post(f"/imports/{second['id']}/commit", json={}).json()
    assert report["imported_count"] == 1
    assert report["reconciled"] is True


def test_conflicting_staged_commits_roll_back_without_partial_rows(client):
    content = "date,merchant,amount\n2026-08-01,Store,10.00\n2026-08-02,Other,20.00\n"
    first = stage(client, content).json()
    competing = stage(client, content).json()
    assert client.post(f"/imports/{first['id']}/commit", json={}).status_code == 200
    conflict = client.post(f"/imports/{competing['id']}/commit", json={})
    assert conflict.status_code == 409
    inspected = client.get(f"/imports/{competing['id']}").json()
    assert inspected["state"] == "ready"
    assert all(row["transaction_id"] is None for row in inspected["rows"])
    assert client.get("/transactions/").json()["total"] == 2


def test_repeated_commit_is_idempotent(client):
    imported = stage(client, "date,merchant,amount\n2026-08-01,Store,10.00\n").json()
    first = client.post(f"/imports/{imported['id']}/commit", json={})
    second = client.post(f"/imports/{imported['id']}/commit", json={})
    assert first.json() == second.json()
    assert client.get("/transactions/").json()["total"] == 1
