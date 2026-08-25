# ClearSpend Project Plan

_Last updated: August 24, 2026_

## Purpose

ClearSpend is meant to be more than a personal-finance CRUD application. Its
main engineering story is a trustworthy Python and PostgreSQL pipeline that can
turn inconsistent bank exports into clean, explainable transaction data.

A successful import should be safe to retry, easy to inspect, and fully
reconciled. No source row should disappear without an outcome, no duplicate
should be removed without an explanation, and no financial total should depend
on floating-point arithmetic.

## Key aspects

These are the strongest verified results from the project and the most useful
ones to carry into a resume or technical interview:

- Built a streamed FastAPI/PostgreSQL transaction-import pipeline with staged
  validation, deterministic normalization, row-level lineage, duplicate review,
  transactional commits, and complete reconciliation.
- Reduced measured peak Python memory for a generated 100,000-row workload from
  126.85 MiB to 29.99 MiB by replacing whole-file materialization with streaming,
  1,000-row staging batches, and paginated previews—a 76.4% reduction.
- Benchmarked PostgreSQL insertion strategies and measured native `COPY` at
  approximately 66,108 rows/second for 10,000 generated rows: 87.8 times the
  throughput of row-at-a-time insertion and 10.3 times SQLAlchemy bulk execute.
- Prevented repeated and competing imports through stable SHA-256 fingerprints,
  an owner-scoped uniqueness constraint, row locking, idempotent commit behavior,
  and rollback tests that prove partial transactions are not retained.
- Enforced the reconciliation rule `input = imported + duplicates + invalid +
  rejected` and verified that accepted staging totals match linked transaction
  totals using exact decimal money types.
- Implemented SQL analytics with grouped queries and window functions, including
  month-over-month changes, three-month rolling averages, merchant totals,
  category share, largest transactions, and uncategorized rate.
- Improved a representative PostgreSQL date query from 10.107 ms to 0.840 ms
  through indexing, with reproducible `EXPLAIN ANALYZE` tooling and additional
  owner/date and owner/merchant composite indexes.
- Maintained 73 backend tests that pass on both SQLite and PostgreSQL, alongside
  a React/TypeScript production build and lint-clean frontend.

The measurements above come from generated workloads on the development
machine. They should be presented as reproducible benchmark results, not as
hardware-independent guarantees.

## Current architecture

```text
Bank CSV or manual entry
           |
           v
 Mapping and streamed parsing
           |
           v
 Staging, validation, normalization
           |
           v
 Exact and possible duplicate review
           |
           v
 Transactional commit and reconciliation
           |
     +-----+-----+
     |           |
     v           v
Categorization  SQL analytics and exports
```

The FastAPI backend owns validation and financial correctness. PostgreSQL stores
trusted transactions, staging records, lineage, review decisions, and import
metrics. The React application provides the mapping, preview, review, and commit
workflow without trying to reproduce backend business rules.

## Completed work

### Import integrity

The core pipeline is complete. It supports streamed multipart uploads, custom
column mappings, debit/credit or signed-amount layouts, several date formats,
currency validation, deterministic fingerprints, exact and possible duplicate
classification, and reusable mapping presets.

Raw and normalized values are stored together in owner-scoped staging tables.
Preview results are paginated, and possible duplicates can be approved or
rejected individually. Commits use database transactions and locking, keep a
source-row link on each saved transaction, and remain safe when repeated or when
two staged imports compete for the same fingerprint.

### Performance and observability

Generated 1K, 10K, and 100K workloads measure processing time, throughput, and
memory. Separate insertion benchmarks compare row-at-a-time, configurable
batches, bulk execute, and PostgreSQL `COPY`. Each real import stores its
processing duration, throughput, commit duration, and estimated peak staging
buffer size.

### Analytics

The focused analytics layer is complete. It uses SQL aggregation and window
functions for monthly trends and rolling averages, and provides merchant,
category, largest-transaction, and uncategorized-rate reports. Users can export
filtered trusted transactions without direct database access. Important query
plans can be reproduced from a checked-in script.

### Application workflow

The React interface supports authentication, transaction management, monthly
summaries, CSV selection, automatic mapping suggestions, manual mapping,
paginated row review, duplicate decisions, safe commit, and reconciliation
results. The backend and frontend verification commands pass cleanly.

## Next phase

The original high-priority pipeline work is finished. Future work should be
chosen for a specific product or job-search need rather than added only to make
the stack larger.

Good next options are:

1. Add dbt staging and reporting models if targeting analytics-engineering roles.
2. Build a historical data-quality view for validation, duplicate,
   categorization, and throughput trends.
3. Add CI for backend tests, PostgreSQL integration tests, migrations, frontend
   build, and lint.
4. Add structured logs, request IDs, health checks, backup instructions, and a
   tested restore procedure before deployment.
5. Experiment with category suggestions learned from user corrections only after
   the pipeline and evaluation dataset justify it.

## Engineering rules

- Use `Decimal` and PostgreSQL `NUMERIC` for money.
- Preserve raw values before applying transformations.
- Keep transformations deterministic, small, and testable.
- Scope every staging, transaction, and analytics query to its owner.
- Never silently discard an input row.
- Treat possible duplicates as review decisions, not automatic deletions.
- Require count reconciliation and exact accepted-versus-saved totals.
- Use generated or anonymous data in tests, fixtures, and benchmarks.
- Attach performance claims to reproducible commands and recorded conditions.

## Known tradeoffs

Streaming reduced memory substantially, but the tracemalloc-enabled 100K
validation benchmark takes about 65 seconds on the development machine. Further
speed work should profile normalization and fingerprinting before changing the
correctness model.

Mapping presets are intentionally simple and local. A larger preset library
would need versioning and fixture coverage because bank export formats can
change. Likewise, machine learning remains optional: deterministic merchant
rules are easier to explain and already provide a reliable fallback.

## Plan maintenance

Update this document only when implementation or measurements change. Detailed
commands and benchmark conditions belong in `docs/`, while the README should
remain the shortest accurate introduction to the project.
