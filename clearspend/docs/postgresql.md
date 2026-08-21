# Running the Project with PostgreSQL

SQLite is convenient for learning and quick tests. PostgreSQL is closer to the database commonly used by deployed applications. This project supports both.

## What Docker provides

The `compose.yaml` file starts one PostgreSQL server containing two separate databases:

- `transactions` stores development data used by the running API.
- `transactions_test` is temporary space used by automated tests.

Keeping them separate prevents tests from deleting development data.

The username, password, and database addresses in this setup are only for local development. Production credentials must be private and different.

## Start PostgreSQL

```powershell
docker compose up -d database
```

Check its status:

```powershell
docker compose ps
```

## Prepare the development database

Set the database address for the current PowerShell window:

```powershell
$env:DATABASE_URL="postgresql+psycopg://transaction_app:local_dev_password@localhost:5433/transactions"
```

Apply all database migrations:

```powershell
python -m alembic upgrade head
```

The API will use PostgreSQL when it is started from the same PowerShell window.

## Run the tests against PostgreSQL

In a separate PowerShell window, set the test database address:

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://transaction_app:local_dev_password@localhost:5433/transactions_test"
python -m pytest
```

The test suite creates and removes its own tables inside `transactions_test`. It does not touch the development database.

Remove the temporary setting when finished:

```powershell
Remove-Item Env:TEST_DATABASE_URL
```

## Measure a database index

With `DATABASE_URL` still pointing to PostgreSQL, run:

```powershell
python scripts/measure_index_performance.py
```

The script creates 50,000 temporary example transactions and measures the same date search before and after adding an index. It prints PostgreSQL's chosen search method and timing. The temporary table is removed automatically and does not affect app data.

Recorded development measurement:

| Version | Search method | Time |
|---|---|---:|
| Without index | Sequential scan | 10.107 ms |
| With date index | Bitmap index scan | 0.840 ms |

This run measured a 12.03× speedup. Timings depend on the computer, database state, and data shape, so the repeatable script is more important than any single result.

## Stop PostgreSQL

```powershell
docker compose stop database
```

Stopping the container keeps the development data. Removing its storage is a separate destructive action and is not part of the normal workflow.
