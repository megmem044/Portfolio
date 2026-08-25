# ClearSpend

ClearSpend is a personal-finance data application built around a simple problem:
bank exports are inconsistent, but financial records still need to be exact,
traceable, and safe to process more than once.

The project combines a FastAPI service, PostgreSQL, and a React interface. A user
can upload a CSV, map unfamiliar columns, inspect normalized rows and validation
errors, review possible duplicates, and commit approved transactions. Every
saved transaction keeps its link to the original file and row.

## Import pipeline

```text
CSV upload → column mapping → staging → validation and normalization
           → duplicate review → transactional commit → reconciliation
```

Uploads are parsed as streams and written to staging in 1,000-row batches. The
preview API is paginated, so large imports do not produce a single enormous
response. Raw values are retained alongside cleaned dates, merchants, currency
codes, and exact decimal amounts.

Stable SHA-256 fingerprints identify exact duplicates. Transactions with the
same date and amount but a different merchant are treated as possible duplicates
and remain visible for an explicit decision. A database constraint provides a
final safeguard against repeated or competing commits.

After a commit, ClearSpend verifies both of these invariants:

```text
input rows = imported + exact duplicates + invalid + rejected
accepted staging total = saved transaction total
```

## Features

- Private user accounts and owner-scoped data
- Manual transaction creation, editing, deletion, filtering, sorting, and paging
- Streamed CSV uploads with custom mappings and reusable format presets
- Row-level validation errors without silently dropping input
- Deterministic normalization, fingerprints, and idempotent retries
- Explicit possible-duplicate approval or rejection
- Transactional commits, rollback protection, lineage, and reconciliation
- Stored import duration, throughput, commit time, and staging-buffer metrics
- Monthly trends, rolling averages, merchant totals, category share, largest
  transactions, and uncategorized-rate analytics
- Filtered transaction export as CSV
- React import workflow for mapping, paginated review, decisions, and results
- SQLite for lightweight development and PostgreSQL for production-like testing

## Measured results

Benchmarks use generated data rather than personal bank records. On the
development machine:

- Streaming the 100,000-row parsing and validation path reduced peak Python
  memory from 126.85 MiB to 29.99 MiB, a 76.4% reduction.
- PostgreSQL `COPY` processed a 10,000-row insertion benchmark at approximately
  66,108 rows/second.
- In that run, `COPY` delivered 87.8 times the throughput of row-at-a-time
  insertion and 10.3 times the throughput of SQLAlchemy bulk execute.
- A PostgreSQL date-index benchmark improved a representative query from
  10.107 ms to 0.840 ms, a 12.03-times speedup.
- The backend suite contains 73 tests and passes on both SQLite and PostgreSQL.

Timings vary by machine and database state. The repository includes the scripts
used to reproduce the measurements.

## Technology

- Python 3.11, FastAPI, SQLAlchemy, Alembic, and Pytest
- PostgreSQL 17 with exact `NUMERIC` money fields, indexes, window functions,
  query-plan inspection, and native `COPY`
- React 19, TypeScript, and Vite
- Docker Compose for the local PostgreSQL environment

## Run locally

Create a virtual environment and install the backend:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

The API documentation is available at `http://127.0.0.1:8000/docs`.

To use PostgreSQL instead of SQLite:

```powershell
docker compose up -d database
$env:DATABASE_URL="postgresql+psycopg://transaction_app:local_dev_password@localhost:55432/transactions"
python -m alembic upgrade head
```

Run the frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

## Verification and benchmarks

```powershell
python -m pytest
python scripts/benchmark_import_pipeline.py --phase processing --sizes 1000 10000 100000
python scripts/benchmark_import_pipeline.py --phase insertion --sizes 1000 10000 --database-url $env:DATABASE_URL
python scripts/explain_analytics.py
```

Frontend checks:

```powershell
cd frontend
npm run build
npm run lint
```

Never commit `.env` files or real financial data. Tests and benchmarks use
generated or anonymous records.

## Documentation

- [Project plan](PROJECT_PLAN.md)
- [Import pipeline](docs/import-pipeline.md)
- [Analytics](docs/analytics.md)
- [PostgreSQL and performance](docs/postgresql.md)
- [Architecture](docs/architecture.md)
- [Product requirements](docs/product-requirements.md)
