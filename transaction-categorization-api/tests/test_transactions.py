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

    assert client.get("/transactions/").json() == []


def test_list_transactions_filters_dates_and_orders_newest_first(client):
    add_transaction(client, "10.00", "Older Shop", "2026-06-01")
    add_transaction(client, "20.00", "Newer Shop", "2026-07-15")
    add_transaction(client, "30.00", "Middle Shop", "2026-07-05")

    response = client.get(
        "/transactions/",
        params={"start": "2026-07-01", "end": "2026-07-31"},
    )

    assert response.status_code == 200
    assert [item["merchant"] for item in response.json()] == [
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


def test_monthly_summary_rejects_invalid_month(client):
    for month in ("2026-13", "July", "2026-7"):
        response = client.get("/transactions/summary", params={"month": month})
        assert response.status_code == 422
