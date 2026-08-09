"""Test safe creation, editing, listing, and deletion of categories."""

def create_category(client, name="Entertainment", description="Movies and events"):
    return client.post(
        "/categories/",
        json={"name": name, "description": description},
    )


def test_list_categories_returns_defaults(client):
    response = client.get("/categories/")

    assert response.status_code == 200
    assert {category["name"] for category in response.json()} == {
        "Food & Dining",
        "Transportation",
        "Groceries",
        "Uncategorized",
    }
    assert all(category["is_default"] for category in response.json())


def test_create_and_get_custom_category(client):
    response = create_category(client, "  Entertainment  ", "  Movies  ")

    assert response.status_code == 201
    assert response.json()["name"] == "Entertainment"
    assert response.json()["description"] == "Movies"
    assert response.json()["is_default"] is False

    saved = client.get(f"/categories/{response.json()['id']}")
    assert saved.status_code == 200
    assert saved.json() == response.json()


def test_duplicate_category_name_is_rejected(client):
    assert create_category(client).status_code == 201

    response = create_category(client)

    assert response.status_code == 409
    assert response.json()["detail"] == "category name already exists"


def test_update_custom_category(client):
    category = create_category(client).json()

    response = client.patch(
        f"/categories/{category['id']}",
        json={"name": "Subscriptions", "description": None},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Subscriptions"
    assert response.json()["description"] is None


def test_default_category_cannot_be_changed_or_deleted(client):
    default_category = client.get("/categories/").json()[0]

    update = client.patch(
        f"/categories/{default_category['id']}",
        json={"name": "Changed"},
    )
    delete = client.delete(f"/categories/{default_category['id']}")

    assert update.status_code == 409
    assert delete.status_code == 409


def test_delete_unused_custom_category(client):
    category = create_category(client).json()

    response = client.delete(f"/categories/{category['id']}")

    assert response.status_code == 204
    assert client.get(f"/categories/{category['id']}").status_code == 404


def test_category_used_by_transaction_cannot_be_deleted(client):
    category = create_category(client).json()
    transaction = client.post(
        "/transactions/",
        json={"amount": "10.00", "merchant": "Shop", "date": "2026-07-10"},
    ).json()
    update = client.patch(
        f"/transactions/{transaction['id']}",
        json={"category": category["name"]},
    )

    response = client.delete(f"/categories/{category['id']}")

    assert update.status_code == 200
    assert response.status_code == 409
    assert response.json()["detail"] == "category is used by transactions"


def test_missing_category_returns_not_found(client):
    assert client.get("/categories/999").status_code == 404
    assert client.patch("/categories/999", json={"name": "Missing"}).status_code == 404
    assert client.delete("/categories/999").status_code == 404
