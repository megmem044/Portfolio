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
$env:DATABASE_URL="postgresql+psycopg://transaction_app:local_dev_password@localhost:55432/transactions"
```

Apply all database migrations:

```powershell
python -m alembic upgrade head
```

The API will use PostgreSQL when it is started from the same PowerShell window.

## Run the tests against PostgreSQL

In a separate PowerShell window, set the test database address:

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://transaction_app:local_dev_password@localhost:55432/transactions_test"
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

## Inspect analytics query plans

With `DATABASE_URL` pointing to PostgreSQL, run:

```powershell
python scripts/explain_analytics.py
```

The script runs `EXPLAIN (ANALYZE, BUFFERS)` for monthly trends, merchant
aggregation, and filtered export. All three queries apply `owner_id` before
aggregation; the filtered export can combine the owner and date indexes. Treat
plans from an empty database as structural checks and capture portfolio timing
claims only after loading representative generated data.

The August 24 structural run selected owner-scoped indexes for both grouped
analytics queries and completed them in under 0.3 ms on the empty development
database. The filtered export completed in 0.06 ms. Composite `(owner_id, date)`
and `(owner_id, merchant)` indexes are included so representative datasets can
filter tenant data before date ordering or merchant grouping.

## Stop PostgreSQL

```powershell
docker compose stop database
```

Stopping the container keeps the development data. Removing its storage is a separate destructive action and is not part of the normal workflow.
