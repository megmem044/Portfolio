# Database setup

AnswerTrust uses SQLite for simple local development and PostgreSQL for the
production-style setup. Alembic is the only tool that should change the real
database structure.

## Local SQLite

With no environment variable, the API uses `data/answertrust-v2.db`.

```powershell
python -m alembic upgrade head
python -m uvicorn src.api:app --reload
```

## PostgreSQL

Create an empty database, set its URL, and apply every migration:

```powershell
$env:DATABASE_URL="postgresql://answertrust:password@localhost:5432/answertrust"
python -m alembic upgrade head
python -m alembic current
```

The final command should show the latest migration with `(head)`.

## PostgreSQL integration test

Use a separate migrated test database:

```powershell
$env:TEST_DATABASE_URL="postgresql://answertrust:password@localhost:5432/answertrust_test"
$env:DATABASE_URL=$env:TEST_DATABASE_URL
python -m alembic upgrade head
python -m pytest -m postgres -q
```

## Import the old SQLite prototype

Back up the source file first. Apply migrations to the destination database,
then run:

```powershell
python -m scripts.migrate_legacy_sqlite --source data/answertrust.db
```

The importer skips evaluation IDs that already exist, so rerunning it does not
duplicate evaluations.
