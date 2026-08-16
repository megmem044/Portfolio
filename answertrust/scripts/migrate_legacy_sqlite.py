"""Command-line importer for the original AnswerTrust SQLite database."""

import argparse
from pathlib import Path

from src.config import DATABASE_PATH
from src.db import create_database_engine, create_session_factory
from src.legacy_migration import migrate_legacy_sqlite


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DATABASE_PATH)
    arguments = parser.parse_args()
    summary = migrate_legacy_sqlite(
        arguments.source,
        create_session_factory(create_database_engine()),
    )
    print(
        f'Migrated {summary["migrated"]}; skipped {summary["skipped"]}; '
        f'imported reviews {summary["reviews"]}.'
    )


if __name__ == "__main__":
    main()
