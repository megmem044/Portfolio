# ClearSpend Project Plan

_Last updated: August 15, 2026_

## Goal

Build ClearSpend into a reliable transaction data platform. It will accept inconsistent bank data, check and clean it, prevent duplicate financial records, and create trustworthy analytics with SQL.

The existing FastAPI API, PostgreSQL database, and React website will stay in place. They support the main project story, which is now data pipelines, analytics, data quality, performance, and financial correctness.

## What success looks like

A user should be able to upload a bank CSV file, review every row, understand any errors or duplicate warnings, and safely save approved transactions. Uploading the same data again must not create duplicate records.

The system should also:

- Keep an audit trail from each saved transaction back to its source file and row.
- Prove that all input rows are imported, rejected, or marked as duplicates.
- Keep money calculations exact.
- Produce useful reports with SQL.
- Measure pipeline quality and processing speed.
- Learn simple categorization patterns from corrections without making machine learning the main feature.

## Current state

The project already has:

- A FastAPI backend and React frontend
- PostgreSQL and SQLite support
- Alembic database migrations
- Private user accounts and protected user data
- Transaction creation, editing, deletion, search, filtering, sorting, and pagination
- Categories and merchant categorization rules
- Monthly category totals calculated in the database
- Backend tests and a measured PostgreSQL index improvement

The import pipeline, staging tables, analytics models, dbt project, data-quality dashboard, large-import benchmarks, and correction-trained model have not been built yet.

## Planned data flow

```text
Upload bank file
       |
       v
Choose or detect its format
       |
       v
Map and parse columns
       |
       v
Store rows in staging tables
       |
       v
Validate and normalize data
       |
       v
Find exact and possible duplicates
       |
       v
Preview and approve results
       |
       v
Save trusted transactions
       |
       +------------------+
       |                  |
       v                  v
Categorization       SQL analytics
       |                  |
       v                  v
 Corrections       Reports and exports
```

## Roadmap

### Milestone 1: Design the import foundation

Status: Next

Build:

- Define one standard transaction format for all sources.
- Add `imports` and `import_rows` staging tables.
- Store the filename, source, row number, raw values, cleaned values, status, and error reason.
- Define import states such as uploaded, validating, ready, committed, and failed.
- Document how a saved transaction links back to its source row.

Complete when:

- Database migrations work on a clean database.
- Relationships and ownership rules are tested.
- A failed import can be inspected without adding partial transactions.

### Milestone 2: Build CSV parsing and validation

Status: Not started

Build:

- Accept common bank CSV layouts.
- Let users map unfamiliar columns to ClearSpend fields.
- Parse dates, debit and credit columns, signed amounts, merchants, and currencies.
- Validate required values and explain row-level errors.
- Preview the results before saving them.
- Add safe file-size and row-count limits.

Complete when:

- Several different sample bank formats produce the same standard records.
- Invalid rows show clear reasons and do not block the review of valid rows.
- Empty, malformed, oversized, and unusual files are tested.

### Milestone 3: Normalize and deduplicate data

Status: Not started

Build:

- Create small, testable cleaning steps for whitespace, case, dates, amounts, and merchant names.
- Preserve both raw and cleaned merchant values.
- Support merchant aliases such as different Amazon descriptions becoming `Amazon`.
- Create a stable fingerprint from important transaction fields.
- Classify rows as new, exact duplicate, possible duplicate, or invalid.
- Make import retries idempotent, meaning repeated requests do not create repeated records.

Complete when:

- Normalization rules have regression tests.
- Uploading the same file twice creates no extra transactions.
- Possible duplicates are shown for review instead of silently removed.

### Milestone 4: Commit and reconcile imports

Status: Not started

Build:

- Commit approved rows in a safe database transaction.
- Process rows in batches and roll back safely after failures.
- Produce a reconciliation report for each import.
- Track input, valid, invalid, exact duplicate, possible duplicate, and imported counts.
- Confirm that every input row is accounted for.

Complete when:

- The report satisfies this rule: `input rows = imported + duplicates + invalid or rejected rows`.
- Money totals for accepted rows match the saved transaction totals.
- Interrupted and repeated commits are tested.

### Milestone 5: Add SQL analytics and marts

Status: Not started

Build:

- Monthly spending by category
- Month-over-month spending changes
- Merchant spending totals and transaction counts
- Three-month rolling averages
- Largest transactions and category share
- Uncategorized transaction rate
- Analytics tables for monthly, category, merchant, and import-quality reporting
- CSV exports for filtered transactions and analytics

Use SQL joins, common table expressions, window functions, conditional totals, indexes, and query plans where they make the result clearer or faster.

Complete when:

- Analytics totals agree with the trusted transaction records.
- Important queries have tests and documented query plans.
- Users can export useful datasets without direct database access.

### Milestone 6: Add dbt and data-quality checks

Status: Not started

Build:

- Organize dbt models into staging, intermediate, and reporting layers.
- Test required fields, unique keys, relationships, and accepted status values.
- Document each reporting model and its source data.
- Run dbt models and tests automatically.

Complete when:

- A clean PostgreSQL database can build all analytics models.
- Data-quality failures stop bad reporting data from being published.
- Model definitions and important columns are documented.

### Milestone 7: Measure and improve import performance

Status: Not started

Build:

- Generate safe test files with 1,000, 10,000, 100,000, and larger row counts.
- Measure parsing, validation, database insertion, total runtime, memory use, and rows per second.
- Compare row-by-row inserts, batch inserts, and PostgreSQL bulk loading where appropriate.
- Record the effect of batch size, indexes, and transaction boundaries.

Complete when:

- Results can be reproduced from documented commands.
- Before-and-after measurements support any performance claims.
- Large imports stay within defined time and memory limits.

### Milestone 8: Show pipeline quality

Status: Not started

Build:

- Display import row counts and reconciliation results.
- Track validation failure rate, duplicate rate, missing merchant rate, categorization coverage, import duration, and processing speed.
- Add alerts or visible warnings for important quality failures.
- Keep historical results so quality changes can be compared over time.

Complete when:

- Each import has a clear quality report.
- The dashboard explains what failed and why.
- Important metrics can be queried or exported.

### Milestone 9: Add simple learning from corrections

Status: Later

Build:

- Save the original category suggestion and the user's correction.
- Create privacy-safe training and evaluation datasets.
- Start with a simple text classifier and compare it with merchant rules.
- Return a confidence score and ask for review when confidence is low.
- Version models and keep rule-based categorization as a fallback.
- Track confidence, correction rate, and category or merchant changes over time.

Complete when:

- Results are measured on data that was not used for training.
- Accuracy, precision, recall, and F1 are reported by category.
- The app still works when the model is unavailable.
- A model version can be reproduced or rolled back.

### Milestone 10: Automate and deploy

Status: Not started

Build:

- Run backend, pipeline, dbt, frontend, and migration checks in CI.
- Containerize the application where it improves repeatable setup.
- Add health checks, structured logs, request IDs, and basic monitoring.
- Create repeatable deployment, backup, and restore instructions.
- Keep security and frontend quality at a practical production-ready level.

Complete when:

- A clean environment can build and run the project from the documentation.
- Failed required checks block deployment.
- A deployed environment passes smoke tests.
- Backup restoration has been tested.

## Immediate priorities

1. Design the standard transaction format and staging tables.
2. Collect or create safe example CSV files with different column layouts.
3. Define import statuses, row results, and reconciliation rules.
4. Build the first CSV parser and preview flow.
5. Add merchant normalization and deterministic fingerprints.
6. Prove that retrying the same import creates no duplicates.

Frontend category screens, richer charts, and extra authentication features are still useful, but they should not delay the data pipeline.

## Data-quality rules

- Use Python `Decimal` and PostgreSQL `NUMERIC` for money.
- Never silently discard an input row.
- Preserve raw source values before cleaning them.
- Make every transformation small, deterministic, and testable.
- Keep user data isolated at every pipeline stage.
- Require category totals to equal the monthly total.
- Require reconciliation counts to equal the number of input rows.
- Treat duplicate matching as an explained classification, not a hidden deletion.
- Use generated or anonymous test data; never commit real bank records.

## Main risks

| Risk | Response |
|---|---|
| Banks use different CSV layouts | Support column mapping and keep reusable fixtures for each format. |
| Cleaning changes the meaning of data | Preserve raw values and test each transformation. |
| Retries create duplicate transactions | Use stable fingerprints, database constraints, and idempotency tests. |
| Possible duplicates are incorrectly removed | Show them for review and separate them from exact duplicates. |
| Financial totals are wrong | Use exact number types and test reconciliation and total invariants. |
| Large files use too much time or memory | Stream or batch work, set limits, and benchmark realistic sizes. |
| Analytics drift away from source records | Add dbt relationship tests and compare report totals with trusted data. |
| Machine learning distracts from the pipeline | Keep the model simple and focus on its data lifecycle and measurements. |

## Main skills demonstrated

- Python and PostgreSQL
- SQL analytics and query tuning
- ETL pipelines and CSV processing
- Data modeling and staging tables
- Data cleaning and normalization
- Deduplication and idempotency
- Batch processing and performance measurement
- dbt and analytics engineering
- Data quality, lineage, and reconciliation
- Exact financial calculations
- A small, measured machine-learning lifecycle

## Plan maintenance

Review this plan after every milestone and update its status and date. Put detailed implementation notes and measured results in `docs/`. Update the README whenever the current feature list or next major priority changes.
