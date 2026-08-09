"""Test creation, priority, activation, and deletion of merchant rules."""


def create_category(client, name="Entertainment"):
    return client.post(
        "/categories/",
        json={"name": name, "description": "Custom category"},
    ).json()


def create_rule(client, keyword, category_id, priority=100):
    return client.post(
        "/rules/",
        json={
            "keyword": keyword,
            "category_id": category_id,
            "priority": priority,
            "is_active": True,
        },
    )


def add_transaction(client, merchant):
    return client.post(
        "/transactions/",
        json={"amount": "10.00", "merchant": merchant, "date": "2026-08-08"},
    )


def test_list_rules_returns_starter_rules_in_priority_order(client):
    response = client.get("/rules/")

    assert response.status_code == 200
    assert [rule["keyword"] for rule in response.json()] == [
        "starbucks",
        "restaurant",
        "uber",
        "lyft",
        "walmart",
        "grocery",
    ]


def test_create_and_get_rule(client):
    category = create_category(client)

    response = create_rule(client, "  NETFLIX  ", category["id"], priority=5)

    assert response.status_code == 201
    assert response.json()["keyword"] == "netflix"
    assert response.json()["category_name"] == "Entertainment"
    saved = client.get(f"/rules/{response.json()['id']}")
    assert saved.json() == response.json()


def test_duplicate_rule_keyword_is_rejected(client):
    category = create_category(client)
    assert create_rule(client, "netflix", category["id"]).status_code == 201

    response = create_rule(client, "NETFLIX", category["id"])

    assert response.status_code == 409


def test_rule_priority_controls_first_match(client):
    category = create_category(client)
    create_rule(client, "starbucks downtown", category["id"], priority=1)

    response = add_transaction(client, "Starbucks Downtown Store")

    assert response.status_code == 200
    assert response.json()["category"] == "Entertainment"


def test_inactive_rule_is_not_used(client):
    category = create_category(client)
    rule = create_rule(client, "netflix", category["id"]).json()

    update = client.patch(f"/rules/{rule['id']}", json={"is_active": False})
    transaction = add_transaction(client, "Netflix Monthly")

    assert update.status_code == 200
    assert update.json()["is_active"] is False
    assert transaction.json()["category"] == "Uncategorized"


def test_rule_rejects_missing_category(client):
    response = create_rule(client, "netflix", category_id=999)

    assert response.status_code == 422
    assert response.json()["detail"] == "category does not exist"


def test_category_used_by_rule_cannot_be_deleted(client):
    category = create_category(client)
    create_rule(client, "netflix", category["id"])

    response = client.delete(f"/categories/{category['id']}")

    assert response.status_code == 409
    assert response.json()["detail"] == "category is used by rules"


def test_delete_and_missing_rule_behavior(client):
    category = create_category(client)
    rule = create_rule(client, "netflix", category["id"]).json()

    assert client.delete(f"/rules/{rule['id']}").status_code == 204
    assert client.get(f"/rules/{rule['id']}").status_code == 404
    assert client.patch("/rules/999", json={"priority": 1}).status_code == 404
    assert client.delete("/rules/999").status_code == 404
