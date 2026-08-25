# Transaction import pipeline

ClearSpend stages CSV data before it changes trusted transactions.

## API flow

1. `POST /imports/` with `filename`, `source`, `csv_content`, and an optional
   column `mapping`.
2. Review the returned raw values, normalized values, statuses, and errors.
3. `POST /imports/{id}/commit`. Possible duplicates are rejected by default;
   pass `{"possible_duplicates": "import"}` to approve them.
4. Read `GET /imports/{id}/reconciliation` to verify counts and exact totals.

Supported dates are ISO, US-style month/day, day/month, and two-digit-year
variants. Amounts can come from one signed column or mapped debit/credit
columns. Amounts are stored as positive spending values. The raw dictionary is
always retained, while normalized values use exact decimal money, an uppercase
three-letter currency, trimmed whitespace, and stable SHA-256 fingerprints.

The database unique constraint on `(owner_id, fingerprint)` is the final guard
against concurrent or repeated imports. Possible duplicates share an owner,
date, and amount but have a different merchant fingerprint, so they require an
explicit decision.

The committed reconciliation invariant is:

```text
input = imported + exact duplicates + invalid + rejected
```

Accepted staging totals must also equal totals linked to saved transactions.

## Benchmark

Run the generated-data parsing and validation baseline with:

```powershell
python scripts/benchmark_import_pipeline.py --phase processing --sizes 1000 10000 100000
```

The command reports phase timings, total throughput, and peak Python memory.
It uses generated merchants only and never reads personal financial data.

Baseline captured August 24, 2026 on the development machine (Python 3.11,
SQLite duplicate lookup, `tracemalloc` enabled):

| Rows | Parse | Validate/classify | Total | Throughput | Peak memory |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.027 s | 0.615 s | 0.641 s | 1,560 rows/s | 2.08 MiB |
| 10,000 | 0.271 s | 3.757 s | 4.029 s | 2,482 rows/s | 12.68 MiB |
| 100,000 (original materialized path) | 1.960 s | 48.086 s | 50.046 s | 1,998 rows/s | 126.85 MiB |
| 100,000 (streaming path) | — | 64.832 s | 64.844 s | 1,542 rows/s | 29.99 MiB |

These are reproducible baselines, not cross-machine performance claims. The
streaming path cut measured peak Python memory by 76.4%. Its tracemalloc-enabled
runtime is slower, leaving validation throughput as a future optimization rather
than a correctness blocker.

Uploaded files are spooled by FastAPI, parsed as a text stream, and inserted into
staging in 1,000-row batches. The API stores processing duration, throughput,
commit duration, and an estimated peak staging-buffer size. Preview responses
are paginated to at most 500 rows rather than returning the entire import.

Database insertion strategies can be measured independently:

```powershell
python scripts/benchmark_import_pipeline.py --phase insertion --sizes 1000 10000 --batch-size 1000
```

The default isolated in-memory SQLite baseline measured 10,000 rows at 10,833
rows/s row-at-a-time, 57,280 rows/s in 1,000-row batches, and 83,843 rows/s in
one bulk execute. That is a 7.74x bulk improvement over row-at-a-time insertion
on this machine. Pass `--database-url postgresql+psycopg://...` to add a fourth
native PostgreSQL `COPY` measurement. The benchmark uses only the scoped
`benchmark_import_inserts` table and removes it afterward.

PostgreSQL 17 baseline captured August 24, 2026 on the development machine:

| Strategy | 10K throughput |
|---|---:|
| Row-at-a-time | 753 rows/s |
| 1,000-row batches | 5,062 rows/s |
| Bulk execute | 6,429 rows/s |
| Native `COPY` | 66,108 rows/s |

`COPY` measured 87.8x the row-at-a-time throughput and 10.3x the SQLAlchemy
bulk-execute throughput in this run. The complete backend suite also passes
against PostgreSQL.
