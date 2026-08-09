"""Test transaction API behavior using realistic user actions and errors."""

def add_transaction(client, amount, merchant, transaction_date):
    return client.post(
        "/transactions/",
        json={"amount": amount, "merchant": merchant, "date": transaction_date},
    )


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_transaction_cleans_and_categorizes_merchant(client):
    response = add_transaction(client, "8.50", "  Starbucks  ", "2026-07-10")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "amount": "8.50",
        "merchant": "Starbucks",
        "category": "Food & Dining",
        "date": "2026-07-10",
    }


def test_create_transaction_rejects_invalid_input(client):
    invalid_transactions = [
        {"amount": "0", "merchant": "Cafe", "date": "2026-07-10"},
        {"amount": "1.999", "merchant": "Cafe", "date": "2026-07-10"},
        {"amount": "5.00", "merchant": "   ", "date": "2026-07-10"},
        {"amount": "5.00", "merchant": "Cafe", "date": "not-a-date"},
    ]

    for transaction in invalid_transactions:
        response = client.post("/transactions/", json=transaction)
        assert response.status_code == 422

    assert client.get("/transactions/").json()["items"] == []


def test_list_transactions_filters_dates_and_orders_newest_first(client):
    add_transaction(client, "10.00", "Older Shop", "2026-06-01")
    add_transaction(client, "20.00", "Newer Shop", "2026-07-15")
    add_transaction(client, "30.00", "Middle Shop", "2026-07-05")

    response = client.get(
        "/transactions/",
        params={"start": "2026-07-01", "end": "2026-07-31"},
    )

    assert response.status_code == 200
    assert [item["merchant"] for item in response.json()["items"]] == [
        "Newer Shop",
        "Middle Shop",
    ]


def test_list_transactions_rejects_reversed_date_range(client):
    response = client.get(
        "/transactions/",
        params={"start": "2026-08-01", "end": "2026-07-01"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "start date must be on or before end date"


def test_monthly_summary_groups_decimal_totals(client):
    add_transaction(client, "8.50", "Starbucks", "2026-07-10")
    add_transaction(client, "11.25", "Restaurant", "2026-07-12")
    add_transaction(client, "20.00", "Uber", "2026-07-13")
    add_transaction(client, "100.00", "Walmart", "2026-08-01")

    response = client.get("/transactions/summary", params={"month": "2026-07"})

    assert response.status_code == 200
    assert response.json() == {
        "month": "2026-07",
        "transaction_count": 3,
        "overall_total": "39.75",
        "totals_by_category": {
            "Food & Dining": "19.75",
            "Transportation": "20.00",
        },
    }


def test_monthly_summary_handles_empty_month(client):
    response = client.get("/transactions/summary", params={"month": "2026-07"})

    assert response.status_code == 200
    assert response.json() == {
        "month": "2026-07",
        "transaction_count": 0,
        "overall_total": "0.00",
        "totals_by_category": {},
    }


def test_monthly_summary_handles_year_boundary(client):
    add_transaction(client, "12.00", "December Shop", "2026-12-31")
    add_transaction(client, "20.00", "January Shop", "2027-01-01")

    response = client.get("/transactions/summary", params={"month": "2026-12"})

    assert response.status_code == 200
    assert response.json()["transaction_count"] == 1
    assert response.json()["overall_total"] == "12.00"


def test_monthly_summary_rejects_invalid_month(client):
    for month in ("2026-13", "July", "2026-7"):
        response = client.get("/transactions/summary", params={"month": month})
        assert response.status_code == 422


def test_get_one_transaction(client):
    created = add_transaction(client, "8.50", "Starbucks", "2026-07-10").json()

    response = client.get(f"/transactions/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_update_transaction_and_recalculate_category(client):
    created = add_transaction(client, "8.50", "Starbucks", "2026-07-10").json()

    response = client.patch(
        f"/transactions/{created['id']}",
        json={"amount": "14.25", "merchant": "Uber Trip"},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "14.25"
    assert response.json()["merchant"] == "Uber Trip"
    assert response.json()["category"] == "Transportation"


def test_update_transaction_allows_manual_category(client):
    created = add_transaction(client, "8.50", "Starbucks", "2026-07-10").json()

    response = client.patch(
        f"/transactions/{created['id']}",
        json={"merchant": "Uber Trip", "category": "Groceries"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Groceries"


def test_update_transaction_rejects_unknown_category(client):
    created = add_transaction(client, "8.50", "Starbucks", "2026-07-10").json()

    response = client.patch(
        f"/transactions/{created['id']}",
        json={"category": "Does Not Exist"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "category does not exist"


def test_update_transaction_rejects_empty_or_null_changes(client):
    created = add_transaction(client, "8.50", "Starbucks", "2026-07-10").json()

    assert client.patch(f"/transactions/{created['id']}", json={}).status_code == 422
    assert (
        client.patch(
            f"/transactions/{created['id']}",
            json={"merchant": None},
        ).status_code
        == 422
    )


def test_delete_transaction_updates_summary(client):
    created = add_transaction(client, "8.50", "Starbucks", "2026-07-10").json()

    response = client.delete(f"/transactions/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/transactions/{created['id']}").status_code == 404
    summary = client.get(
        "/transactions/summary",
        params={"month": "2026-07"},
    ).json()
    assert summary["transaction_count"] == 0
    assert summary["overall_total"] == "0.00"


def test_missing_transaction_returns_not_found(client):
    assert client.get("/transactions/999").status_code == 404
    assert client.patch("/transactions/999", json={"amount": "1.00"}).status_code == 404
    assert client.delete("/transactions/999").status_code == 404


def test_list_transactions_returns_page_metadata(client):
    for number in range(3):
        add_transaction(
            client,
            "10.00",
            f"Shop {number}",
            f"2026-07-0{number + 1}",
        )

    response = client.get(
        "/transactions/",
        params={"page": 2, "page_size": 2},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert response.json()["page"] == 2
    assert response.json()["page_size"] == 2
    assert len(response.json()["items"]) == 1


def test_list_transactions_searches_and_filters_category(client):
    add_transaction(client, "8.50", "Starbucks Downtown", "2026-07-10")
    add_transaction(client, "15.00", "Starbucks Airport", "2026-07-11")
    add_transaction(client, "20.00", "Uber Trip", "2026-07-12")

    response = client.get(
        "/transactions/",
        params={"search": "STARBUCKS", "category": "Food & Dining"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert {item["merchant"] for item in response.json()["items"]} == {
        "Starbucks Downtown",
        "Starbucks Airport",
    }


def test_list_transactions_sorts_by_amount(client):
    add_transaction(client, "8.50", "Small Purchase", "2026-07-10")
    add_transaction(client, "20.00", "Large Purchase", "2026-07-11")

    response = client.get(
        "/transactions/",
        params={"sort_by": "amount", "sort_direction": "asc"},
    )

    assert response.status_code == 200
    assert [item["amount"] for item in response.json()["items"]] == [
        "8.50",
        "20.00",
    ]


def test_list_transactions_rejects_invalid_page_or_sort(client):
    assert client.get("/transactions/", params={"page": 0}).status_code == 422
    assert client.get("/transactions/", params={"page_size": 101}).status_code == 422
    assert client.get("/transactions/", params={"sort_by": "id"}).status_code == 422
