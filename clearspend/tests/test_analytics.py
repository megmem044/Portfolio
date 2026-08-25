"""Verify focused analytics totals and window calculations."""


def add(client, amount, merchant, date):
    assert client.post("/transactions/", json={"amount": amount, "merchant": merchant, "date": date}).status_code == 200


def test_monthly_trends_use_lag_and_three_month_window(client):
    add(client, "10.00", "Store", "2026-01-01")
    add(client, "20.00", "Store", "2026-02-01")
    add(client, "30.00", "Other", "2026-03-01")
    add(client, "60.00", "Other", "2026-04-01")
    response = client.get("/analytics/monthly-trends")
    assert response.status_code == 200
    rows = response.json()
    assert rows[0] == {"month": "2026-01", "transaction_count": 1, "total": "10.00", "previous_total": None, "absolute_change": None, "percentage_change": None, "three_month_rolling_average": "10.00"}
    assert rows[2]["three_month_rolling_average"] == "20.00"
    assert rows[3]["three_month_rolling_average"] == "36.67"
    assert rows[3]["absolute_change"] == "30.00"
    assert rows[3]["percentage_change"] == "100.00"


def test_merchant_and_category_aggregates_are_sorted_and_exact(client):
    add(client, "10.00", "Starbucks", "2026-01-01")
    add(client, "20.00", "Starbucks", "2026-01-02")
    add(client, "70.00", "Uber", "2026-01-03")
    merchants = client.get("/analytics/merchants").json()
    assert merchants[0] == {"merchant": "Uber", "transaction_count": 1, "total": "70.00", "average_transaction": "70.00"}
    assert merchants[1]["average_transaction"] == "15.00"
    categories = client.get("/analytics/categories").json()
    assert categories == [{"category": "Transportation", "transaction_count": 1, "total": "70.00", "share_percent": "70.00"}, {"category": "Food & Dining", "transaction_count": 2, "total": "30.00", "share_percent": "30.00"}]


def test_analytics_are_private_and_empty_safe(client):
    assert client.get("/analytics/monthly-trends").json() == []
    assert client.get("/analytics/categories").json() == []
    assert client.get("/analytics/merchants", headers={"Authorization": ""}).status_code == 401


def test_largest_quality_and_filtered_csv_export(client):
    add(client, "10.00", "Unknown Shop", "2026-01-01")
    add(client, "70.00", "Uber", "2026-02-01")
    assert client.get("/analytics/largest-transactions", params={"limit": 1}).json()[0]["merchant"] == "Uber"
    quality = client.get("/analytics/data-quality").json()
    assert quality == {"transaction_count": 2, "uncategorized_count": 1, "uncategorized_rate": "50.00"}
    exported = client.get("/transactions/export.csv", params={"start": "2026-02-01"})
    assert exported.status_code == 200
    assert exported.headers["content-type"].startswith("text/csv")
    assert "Uber" in exported.text and "Unknown Shop" not in exported.text
