# Database design

ClearSpend separates untrusted bank-file input from trusted financial records.
That boundary is the central database decision in the project: a CSV row can be
malformed, duplicated, or ambiguous, while a saved transaction must be valid,
owner-scoped, and traceable.

## Staging and trusted data

`transaction_imports` records the file-level workflow and its reconciliation
metrics. `transaction_import_rows` stores each source row before it can affect
trusted data. `transactions` contains only committed records used by the
application and analytics.

Staging makes failures inspectable. An invalid row can keep its original values
and error explanation without creating a partial transaction. It also gives the
user a place to review possible duplicates before deciding whether they belong
in the trusted table.

```text
transaction_imports
        |
        | one-to-many
        v
transaction_import_rows ---- optional one-to-one ----> transactions
```

The optional link becomes populated only after a staged row is committed. This
provides lineage from a trusted transaction back to its filename, source, and
physical CSV row number.

## Raw and normalized values

Each staged row retains `raw_values` as JSON. Parsed fields such as `date`,
`amount`, `merchant`, and `currency` are stored separately in normalized
columns. `merchant_raw` is preserved alongside the cleaned merchant.

Keeping both forms avoids two failure modes:

- destructive cleaning, where the original source can no longer be inspected;
- repeated parsing, where every preview or commit could interpret the source
  differently.

Normalization happens once through deterministic functions. The resulting
columns can be validated, indexed, queried, and committed without depending on
the original CSV layout.

## Ownership and uniqueness

Every transaction and import belongs to a user. Queries filter by `owner_id`
before returning, aggregating, updating, or deleting data. Cross-owner resources
are returned as `404` so the API does not reveal whether another user's record
exists.

The transaction fingerprint is a SHA-256 digest of normalized date, amount,
case-folded merchant, and currency. The database enforces uniqueness across
`(owner_id, fingerprint)`, rather than globally, because two users may import
the same real-world transaction.

Application-level classification provides useful review states, while the
database constraint remains the final concurrency safeguard. If two staged
imports are classified before either commits, the constraint still prevents
both from creating the same trusted row.

## Exact and possible duplicates

An exact fingerprint match is classified as an exact duplicate. A row sharing
an owner, date, and amount with an existing transaction but having a different
merchant fingerprint is only a possible duplicate.

Possible duplicates are not silently removed. `review_decision` records an
explicit approval or rejection, and the commit endpoint applies a safe default
to rows that have not been reviewed individually.

## Exact money

Money uses Python `Decimal`, SQLAlchemy `Numeric(12, 2)`, and PostgreSQL
`NUMERIC`. Binary floating-point values cannot exactly represent many decimal
fractions, which would make equality and reconciliation unreliable.

The commit report verifies that the sum of imported staging amounts equals the
sum of the transactions linked back to those rows. Monthly and category totals
are also calculated in the database using exact numeric values.

## Transaction boundaries

Staging rows are inserted in 1,000-row batches for bounded application memory,
but the staging operation is committed only after the complete file has been
classified. A parsing or database failure rolls the operation back.

The final commit locks the owning import record, writes approved transactions,
links their source rows, updates row statuses and file-level counts, and commits
those changes as one database transaction. An integrity error rolls back all of
them, leaving the import inspectable and preventing partial trusted data.

Repeated commit requests are idempotent: once the import is committed, the API
returns its existing reconciliation result rather than inserting again.

## Indexes

Indexes reflect measured access patterns rather than indexing every column:

| Index | Purpose |
|---|---|
| `(owner_id, fingerprint)` unique | Idempotency and concurrent duplicate protection |
| `(owner_id, date)` | Owner-scoped date filters, monthly analytics, and exports |
| `(owner_id, merchant)` | Owner-scoped merchant grouping and lookup |
| `date` | General date ordering and range scans |
| import owner/state | Private import lookup and workflow filtering |
| import-row import/status | Paginated preview, reconciliation, and quality counts |

The repository includes `scripts/explain_analytics.py` for reproducible
`EXPLAIN (ANALYZE, BUFFERS)` output. The PostgreSQL guide records the measured
effect of the transaction date index and the plans for priority analytics.

## Reconciliation

ClearSpend does not consider an import complete based only on a successful SQL
commit. It also checks:

```text
input rows = imported + exact duplicates + invalid + rejected
accepted staging total = linked trusted transaction total
```

These invariants turn row statuses and lineage into a correctness guarantee.
They also make operational failures diagnosable: a mismatched count or total
identifies the import as unreconciled instead of silently publishing questionable
financial data.
