"""Validate the local SQLite schema without creating a persistent database."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "sql" / "02_create_local_validation_schema.sql"

EXPECTED_TABLES = {
    "charging_location",
    "charging_port",
    "charging_session",
    "ev_market_registration",
    "fleet",
    "fleet_operator",
    "operating_cost",
    "telemetry_reading",
    "trip",
    "vehicle",
    "vehicle_model",
}


class ValidationFailure(Exception):
    """Raised when a schema validation does not produce the expected result."""


def require(condition: bool, message: str) -> None:
    """Raising a readable validation error when a condition is false."""
    if not condition:
        raise ValidationFailure(message)


def expect_integrity_error(action: Callable[[], None], rule_name: str) -> None:
    """Confirming that SQLite rejects data violating a schema rule."""
    try:
        action()
    except sqlite3.IntegrityError:
        return
    raise ValidationFailure(f"SQLite accepted invalid data for: {rule_name}")


def create_database() -> sqlite3.Connection:
    """Creating an in-memory database from the local validation schema."""
    require(SCHEMA_PATH.is_file(), f"Schema file not found: {SCHEMA_PATH}")

    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return connection


def validate_structure(connection: sqlite3.Connection) -> None:
    """Checking table creation and foreign-key configuration."""
    actual_tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    require(
        actual_tables == EXPECTED_TABLES,
        "Table mismatch. "
        f"Missing: {sorted(EXPECTED_TABLES - actual_tables)}; "
        f"Unexpected: {sorted(actual_tables - EXPECTED_TABLES)}",
    )

    foreign_keys_enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
    require(foreign_keys_enabled == 1, "SQLite foreign-key enforcement is disabled")


def insert_valid_records(connection: sqlite3.Connection) -> None:
    """Inserting one valid record through the complete relationship chain."""
    connection.execute(
        "INSERT INTO fleet_operator VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, "Prairie EV Logistics", "Logistics", "Regina", "Saskatchewan", "Prairies", "Active"),
    )
    connection.execute(
        "INSERT INTO vehicle_model VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, "Example Motors", "E-Van", 2026, "Cargo van", 150, 82.5, 350, 23.5, 8.0),
    )
    connection.execute(
        "INSERT INTO charging_location VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, "Regina Depot", "100 Fleet Street", "Regina", "Saskatchewan", "S4P 0A1", 50.4452, -104.6189, "Fleet Network", "Private", "Active"),
    )
    connection.execute(
        "INSERT INTO ev_market_registration VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, 2026, 1, "Province", "Saskatchewan", "Saskatchewan", "Light-duty vehicle", "Battery electric", 500, 10000),
    )
    connection.execute(
        "INSERT INTO fleet VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (1, 1, "Regina Delivery Fleet", "Delivery", "Regina", "Saskatchewan", "Regina region", "Active"),
    )
    connection.execute(
        "INSERT INTO charging_port VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, 1, "PORT-01", "CCS", "DC fast", 150, "Available"),
    )
    connection.execute(
        "INSERT INTO vehicle VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, 1, 1, "VEH-001", "1ABCDEFGH12345678", "EV001", "2026-01-05", "2026-01-10", 25.0, "Active"),
    )
    connection.execute(
        "INSERT INTO trip VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, 1, "2026-02-01 08:00:00", "2026-02-01 09:00:00", 50.4452, -104.6189, 50.4547, -104.6067, 45.0, 10.5, 45.0, "Completed"),
    )
    connection.execute(
        "INSERT INTO charging_session VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, 1, 1, "2026-02-01 10:00:00", "2026-02-01 11:00:00", 35.0, 85.0, 42.0, 0.18, 1.50, "Completed"),
    )
    connection.execute(
        "INSERT INTO telemetry_reading VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, 1, 1, "2026-02-01 08:30:00", 50.4500, -104.6120, 48.0, 72.0, 27.5, -10.0, 18.2, 70.0, "Driving"),
    )
    connection.execute(
        "INSERT INTO operating_cost VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (1, 1, 1, "2026-02-01", "Charging", "Depot charging session", 42.0, 0.18, 9.06, "CAD", "Fleet Network", "INV-001"),
    )

    violations = list(connection.execute("PRAGMA foreign_key_check"))
    require(not violations, f"Valid records produced foreign-key violations: {violations}")


def validate_rejections(connection: sqlite3.Connection) -> None:
    """Checking that representative invalid records are rejected."""
    expect_integrity_error(
        lambda: connection.execute(
            "INSERT INTO fleet VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (2, 999, "Invalid Fleet", "Delivery", "Regina", "Saskatchewan", "Prairies", "Active"),
        ),
        "fleet foreign key",
    )
    expect_integrity_error(
        lambda: connection.execute(
            "INSERT INTO vehicle_model VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (2, "Example Motors", "E-Van", 2026, None, None, None, None, None, None),
        ),
        "vehicle-model uniqueness",
    )
    expect_integrity_error(
        lambda: connection.execute(
            "INSERT INTO ev_market_registration VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (2, 2026, 5, "Province", "Alberta", "Alberta", "Light-duty vehicle", "Battery electric", 10, 100),
        ),
        "market quarter range",
    )
    expect_integrity_error(
        lambda: connection.execute(
            "INSERT INTO vehicle VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (2, 1, 1, "VEH-002", "SHORTVIN", "EV002", "2026-01-05", "2026-01-10", 0, "Active"),
        ),
        "VIN length",
    )
    expect_integrity_error(
        lambda: connection.execute(
            "INSERT INTO trip VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (2, 1, "2026-02-01 09:00:00", "2026-02-01 08:00:00", 50, -104, 50, -104, 10, 2, 20, "Completed"),
        ),
        "trip timestamp order",
    )
    expect_integrity_error(
        lambda: connection.execute(
            "INSERT INTO charging_session VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (2, 1, 1, "2026-02-02 10:00:00", "2026-02-02 11:00:00", -1, 101, 10, 0.18, 0, "Completed"),
        ),
        "charging battery range",
    )
    expect_integrity_error(
        lambda: connection.execute(
            "INSERT INTO operating_cost VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (2, 1, None, "2026-02-02", "Maintenance", None, None, None, -5, "CAD", None, None),
        ),
        "nonnegative operating cost",
    )


def main() -> int:
    """Running all local schema validations and reporting the outcome."""
    checks = (
        ("Creating all expected tables", validate_structure),
        ("Accepting valid related records", insert_valid_records),
        ("Rejecting invalid records", validate_rejections),
    )

    try:
        with create_database() as connection:
            for label, check in checks:
                check(connection)
                print(f"[PASS] {label}")
    except (OSError, sqlite3.Error, ValidationFailure) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        return 1

    print(f"[PASS] Local schema validation completed for {len(EXPECTED_TABLES)} tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
