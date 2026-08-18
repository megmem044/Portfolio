"""Optional integration checks that run against a configured PostgreSQL database."""

import os

import pytest
from sqlalchemy import inspect, text

from src.db import create_database_engine


@pytest.mark.postgres
def test_postgresql_connection_and_migrated_tables():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests.")
    engine = create_database_engine(url)

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT 1")) == 1

    tables = set(inspect(engine).get_table_names())
    assert {"papers", "evaluations_v2", "claims", "review_tasks"} <= tables
    assert {"benchmark_runs", "benchmark_results"} <= tables
