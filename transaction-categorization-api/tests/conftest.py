"""Create a fresh temporary database and API client for every test."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.db.base import Base
from app.main import create_app
from app.models.category import Category
from app.models.category_rule import CategoryRule


DEFAULT_CATEGORIES = (
    "Food & Dining",
    "Transportation",
    "Groceries",
    "Uncategorized",
)

DEFAULT_RULES = (
    ("starbucks", "Food & Dining", 10),
    ("restaurant", "Food & Dining", 20),
    ("uber", "Transportation", 30),
    ("lyft", "Transportation", 40),
    ("walmart", "Groceries", 50),
    ("grocery", "Groceries", 60),
)


@pytest.fixture
def client():
    postgres_test_url = os.getenv("TEST_DATABASE_URL")
    if postgres_test_url:
        engine = create_engine(postgres_test_url)
    else:
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with testing_session() as seed_session:
        categories = {
            name: Category(name=name, is_default=True)
            for name in DEFAULT_CATEGORIES
        }
        seed_session.add_all(categories.values())
        seed_session.flush()
        seed_session.add_all(
            CategoryRule(
                keyword=keyword,
                category=categories[category_name],
                priority=priority,
                is_active=True,
            )
            for keyword, category_name, priority in DEFAULT_RULES
        )
        seed_session.commit()

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
