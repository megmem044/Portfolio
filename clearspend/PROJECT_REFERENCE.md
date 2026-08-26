# ClearSpend Project Reference

| Reference identity | Verified value |
|---|---|
| Reference version | 2.0 |
| Application version | 0.1.0 |
| Last verified | August 25, 2026 |
| Verified Git baseline | `3d43551` plus the documented working-tree CI, contract-test, and documentation changes |
| Schema head | `20260824_11` |
| Verified toolchain | Python 3.11, PostgreSQL 17, Node 22 in CI |
| Development status | Active development; no production deployment is defined |

`Last verified` means the claims, commands, test count, schema, and measurements
were checked against that state. It is intentionally different from the date of
a later wording-only edit. Labels used below have precise meanings:

- **IMPLEMENTED** exists in source code.
- **VERIFIED** was exercised by tests or an explicit check.
- **MEASURED** is a reproducible observation on the documented development setup.
- **PLANNED** is a possible direction, not current behavior.
- **KNOWN LIMITATION** is an accepted gap in the present implementation.

This document is the starting point for understanding ClearSpend. It explains
what the product does, who can use it, how data moves through it, how the
repository is divided, what every file is responsible for, why the main design
choices were made, and where the implementation is strong or still limited.

The README is the short introduction and setup guide. The files under `docs/`
provide deeper treatment of individual topics. When those documents overlap,
this reference is the authoritative map of the current implementation.

## 1. What ClearSpend is

ClearSpend is a personal-finance data application built around a data-integrity
problem: banks export transactions in inconsistent formats, while financial
records still need to be exact, private, explainable, and safe to process more
than once.

The system accepts manual transactions and mapped CSV files. CSV rows first
enter staging, where ClearSpend preserves the source values, validates and
normalizes important fields, identifies exact and possible duplicates, and lets
the user review ambiguous rows. Only approved data crosses into the trusted
transaction table. Every committed row remains traceable to its source file and
row number.

ClearSpend also turns trusted transactions into SQL-backed analytics: monthly
changes, rolling averages, merchant totals, category shares, largest
transactions, uncategorized rate, monthly summaries, and filtered CSV exports.

The project is deliberately split into two layers:

- The FastAPI/PostgreSQL backend owns correctness, security, persistence,
  reconciliation, and analytics.
- The React/TypeScript frontend guides the user through authentication,
  transaction management, import mapping, review, and commit.

This is primarily a data-processing system with a web interface, not a frontend
dashboard with incidental storage.

### 1.1 ClearSpend in five minutes

Five ideas form the mental model for the entire project:

1. A `Transaction` is the trusted financial record. Imports are workflows that
   may create transactions; they are not themselves financial records.
2. Uploaded rows enter persistent staging first. Invalid and duplicate rows stay
   visible instead of disappearing during parsing.
3. Every source row must receive an accounted outcome: imported, exact duplicate,
   invalid, or rejected.
4. Owner identity is part of resource lookup, uniqueness, categorization, and
   analytics. A bare database ID is never enough to authorize access.
5. Correctness comes from combined controls: Pydantic validation, `Decimal` and
   `NUMERIC`, database constraints, transactions, lineage, locking, and
   reconciliation. No single layer is treated as sufficient.

At runtime the dependency direction is:

```text
React page -> typed frontend API module -> HTTP/FastAPI route
                                           |
                                           v
                                   schema + service/query
                                           |
                                           v
                                  SQLAlchemy model/session
                                           |
                                           v
                                     SQLite/PostgreSQL
```

Routes may call services and database queries. Services do not depend on FastAPI
request objects, and models do not import routes. Frontend pages call API modules
rather than constructing backend requests throughout the component tree.

## Key aspects

- Built a streamed FastAPI/PostgreSQL import pipeline with staged validation,
  deterministic normalization, source-row lineage, duplicate review,
  transactional commits, and complete reconciliation.
- Reduced measured peak Python memory for a generated 100,000-row workload from
  126.85 MiB to 29.99 MiB through streaming, 1,000-row staging batches, and
  paginated previews—a 76.4% reduction.
- Measured native PostgreSQL `COPY` at approximately 66,108 rows/second for
  10,000 generated rows: 87.8 times row-at-a-time insertion and 10.3 times
  SQLAlchemy bulk execute in that run.
- Prevented repeated and competing imports with SHA-256 fingerprints,
  owner-scoped uniqueness, row locking, idempotent commits, and tested rollback.
- Enforced count and money reconciliation with exact `Decimal`/`NUMERIC` values.
- Implemented SQL aggregation and window-function analytics for monthly changes,
  rolling averages, merchants, categories, largest transactions, and data quality.
- Improved a representative PostgreSQL date query from 10.107 ms to 0.840 ms,
  backed by reproducible benchmark and `EXPLAIN ANALYZE` scripts.
- Maintained 80 backend tests on SQLite and PostgreSQL, including deliberate HTTP
  contract coverage for authentication, owner hiding, conflicts, idempotency,
  pagination, status codes, and content types.
- Added GitHub Actions gates for Python checks, both database suites, an Alembic
  migration round trip, frontend lint/type-checking, Vitest, and production build.
- Documented the entire system in this canonical reference and a focused database
  design guide covering files, choices, principles, advantages, and drawbacks.

Measurements use generated data on the development machine and are reproducible
benchmarks, not hardware-independent guarantees.

## 2. End-user use cases

### 2.1 Import transactions from different banks

A user can upload a CSV even when its headers do not match ClearSpend's standard
names. The interface suggests mappings for familiar labels such as `posted`,
`description`, `debit`, or `credit`, and lets the user correct the mapping before
processing.

### 2.2 Inspect bad data without losing the good rows

Invalid dates, amounts, merchants, or currency codes receive row-level error
messages. A malformed row does not hide valid rows from the same file, and its
raw source values remain available for diagnosis.

### 2.3 Retry an upload safely

The same file or transaction data can be submitted again without silently
creating repeated financial records. Stable fingerprints, owner-scoped database
uniqueness, locking, and idempotent commit behavior work together to protect the
trusted table.

### 2.4 Review ambiguous duplicates

Rows with an exact fingerprint are classified as exact duplicates. Rows with
the same date and amount but a different merchant are possible duplicates. The
user can approve or reject those ambiguous rows instead of relying on an opaque
automatic deletion rule.

### 2.5 Prove that an import is complete

After commit, the user receives a reconciliation report. ClearSpend checks that
every source row has an outcome and that the accepted staging total equals the
total of the linked trusted transactions.

### 2.6 Manage transactions manually

A user can create, browse, search, filter, sort, paginate, edit, and delete
transactions. Editing a merchant can recalculate its category, while a manual
category selection remains possible.

### 2.7 Manage categories and categorization rules

Shared default categories and rules are visible to every user. Users can also
create private categories and ordered merchant-keyword rules. Rules can be
enabled, disabled, reprioritized, or removed when they are not protected defaults
or referenced by other data.

### 2.8 Understand spending patterns

The user can view exact monthly totals, category breakdowns, month-over-month
changes, three-month rolling averages, merchant aggregates, category share,
largest transactions, and uncategorized rate.

### 2.9 Export trusted data

Filtered transactions can be downloaded as CSV for spreadsheets or external
analysis without giving the user direct database access.

### 2.10 Keep accounts separate

Authentication and owner filters isolate transactions, imports, custom
categories, rules, and analytics. Requests for another user's resource are
returned as not found so the API does not disclose its existence.

## 3. Domain model and system architecture

### 3.1 Domain concepts

| Concept | Meaning |
|---|---|
| User | An authenticated owner and the security boundary for private data. |
| Transaction | A trusted financial record created manually or from at most one accepted import row. |
| Category | A default or owner-created classification assigned to transactions. |
| Category rule | A keyword-to-category instruction used to classify a merchant. |
| Transaction import | One owner's staged workflow for a source CSV, its metrics, counts, and commit state. |
| Import row | The preserved source row plus its normalized interpretation, validation result, duplicate status, review decision, and optional transaction link. |
| Revoked token | A logged-out JWT identifier that remains rejected until the token would have expired. |
| Reconciliation | The proof that all input rows are accounted for and imported monetary totals match saved transactions. |

```text
User 1 ---- N Transaction N ---- 0..1 Category
  |                                  ^
  +---- N Category ------------------+
  +---- N CategoryRule N ------------+
  +---- N TransactionImport
  |             |
  |             +---- N ImportRow 0..1 ---- 0..1 Transaction
  +---- N RevokedToken
```

Default categories and rules have a null owner and are readable by all users;
private categories and rules carry an owner. A transaction always has an owner,
while its category is optional. An import row has at most one resulting
transaction, enforced by a unique lineage link.

### 3.2 Runtime components and topology

```text
Development                              Continuous integration
-----------                              ----------------------
Browser                                  GitHub Actions
  |                                      +-- Ruff + SQLite tests
Vite/React :5173                         +-- PostgreSQL 17 tests
  | HTTP + bearer JWT                    +-- Alembic round trip/check
FastAPI/Uvicorn :8000                    +-- ESLint + TypeScript
  | SQLAlchemy                           +-- Vitest + Vite build
PostgreSQL Docker :55432
  or local SQLite
```

**IMPLEMENTED:** local SQLite and Dockerized PostgreSQL paths plus CI validation.
**PLANNED:** no production topology, reverse proxy, TLS termination, worker
process model, deployment automation, or managed backup service exists yet.

### 3.3 Dependency and trust boundaries

- The browser is untrusted. Backend schemas and ownership checks repeat every
  security- or integrity-relevant validation.
- Authentication converts a bearer token into a current user. Resource queries
  then combine resource ID and owner ID; cross-owner lookups normally appear as
  `404` rather than disclosing existence.
- Staging is inspectable and mutable only in narrowly defined review fields.
  Trusted transactions alone feed summaries, analytics, and exports.
- Pydantic owns transport validation, services own reusable processing, routes
  coordinate HTTP and transaction behavior, and database constraints arbitrate
  concurrent writes.
- SQLAlchemy parameterization is the query boundary. Code must not interpolate
  untrusted values into SQL text.

## 4. Critical workflows

### 4.1 Import flow

```text
Browser file selection
        |
        v
Multipart upload and column mapping
        |
        v
Streamed CSV parsing (5 MiB / 100K-row limits)
        |
        v
Validation + normalization + fingerprinting
        |
        v
Staging rows written in 1,000-row batches
        |
        v
Paginated preview and duplicate decisions
        |
        v
Locked transactional commit
        |
        v
Trusted transactions + source-row lineage
        |
        v
Count and money reconciliation
```

The concrete source path is:

```text
ImportPage.tsx -> frontend/src/api/imports.ts
  -> POST /imports/upload
  -> app/api/routes/transaction_imports.py
  -> ImportMapping / ImportRead schemas
  -> app/services/transaction_imports.py
  -> TransactionImport + TransactionImportRow
  -> database

ImportPage.tsx -> PATCH review decisions -> import route -> staging row
ImportPage.tsx -> POST commit -> locked import route -> Transaction
  -> lineage link -> reconciliation schema -> UI result
```

### 4.2 Manual transaction flow

```text
HTTP request → Pydantic validation → merchant rules → SQLAlchemy model
             → database transaction → response schema
```

### 4.3 Analytics flow

```text
Authenticated owner → trusted transactions → grouped/window SQL
                    → exact Decimal response or CSV export
```

The backend analytics routes execute owner-filtered grouped/window queries
directly against trusted transaction/category tables and return bounded read
models. The current `DashboardPage.tsx` uses the simpler
`frontend/src/api/transactions.ts` monthly-summary call; the richer `/analytics/*`
endpoints and filtered export are not yet wired into frontend screens.

### 4.3.1 Authentication and categorization

```text
Login/Register UI -> frontend auth API -> /auth route
  -> auth schema -> security service -> User/RevokedToken -> bearer response

Manual/imported merchant -> deterministic rule lookup for current owner
  -> matching CategoryRule -> Category -> trusted Transaction.category_id
```

Protected requests resolve the JWT through `app/api/dependencies.py` before
route logic runs. Logout records the token identifier so reuse is rejected until
its original expiry. Categorization is a deterministic write-time convenience;
analytics reads the category actually stored on the trusted transaction.

### 4.4 Trust boundaries

- Browser input is untrusted. The backend repeats all important validation.
- Staging data is inspectable but not used as trusted financial data.
- Only committed transactions feed summaries and analytics.
- Authentication identifies the owner; every resource query applies ownership.
- Pydantic controls request and response shapes; database constraints remain the
  final integrity boundary under concurrent requests.

### 4.5 Import state and row outcomes

The implemented import lifecycle is intentionally small:

```text
create import -> validating -> ready -> committed
                    |             |
                    | failure     +-- review possible-duplicate rows
                    v             +-- commit with approve/reject default
               transaction rollback
```

There is no persisted `uploaded`, `review_required`, `committing`, or `failed`
state. Upload and staging run synchronously inside one request. A `ready` import
can accept review decisions and can be committed. Repeating a commit on a
`committed` import returns its existing reconciliation result without creating
more transactions.

| Import state | Operation | Result |
|---|---|---|
| `validating` | Internal staging work | Becomes `ready` only after staging commits. |
| `ready` | Review possible duplicate | Decision changes; import remains `ready`. |
| `ready` | Commit | Approved/new rows become transactions; state becomes `committed`. |
| `committed` | Commit again | Safe read-like result; existing reconciliation is returned. |
| `committed` | Review row | Rejected with `409`. |

Row outcomes are `new`, `possible_duplicate`, `exact_duplicate`, `invalid`,
`rejected`, and `imported`. Only `new` and approved possible-duplicate rows may
cross the trust boundary.

### 4.6 Atomic commit and concurrency

```text
BEGIN
  SELECT owned import FOR UPDATE
  if committed: return existing reconciliation
  stream staged rows in bounded batches
  apply duplicate decisions
  INSERT trusted transactions
  link each imported staging row to its transaction
  aggregate outcome counts
  set import state and metrics
COMMIT
then calculate and return reconciliation
```

An integrity error rolls the session back and returns `409`; no partial trusted
import remains. Two simultaneous commits serialize on the import row. The second
request acquires the lock after the first commits, observes `committed`, and
returns the established result. Separate simultaneous imports containing the
same normalized transaction are resolved by the owner/fingerprint unique
constraint; one succeeds and the competing commit rolls back.

Category deletion uses application checks for transaction/rule references plus
foreign-key constraints as the final boundary. There is still a race window
between an application pre-check and a competing reference insertion, so the
database—not the pre-check—is authoritative.

## 5. Data architecture and invariants

### 5.1 Entity relationships and storage roles

The domain diagram in Section 3 is also the logical ERD. The most important
physical distinction is between `transaction_import_rows` and `transactions`:
the first stores evidence and interpretation; the second stores trusted finance.
Raw JSON and normalized columns coexist so a reader can explain both what the
bank supplied and what ClearSpend decided it meant. See `docs/database-design.md`
for column-level rationale, constraints, and indexes.

### 5.2 Invariant catalogue

| ID | Rule that must remain true | Primary enforcement |
|---|---|---|
| INV-01 | Money never uses binary floating point. | Pydantic/Python `Decimal`; database `NUMERIC`. |
| INV-02 | Every trusted transaction belongs to one user. | Non-null owner FK and owner-scoped queries. |
| INV-03 | One user cannot retrieve another user's private records. | Authentication plus ID-and-owner predicates; contract tests. |
| INV-04 | One accepted import row creates at most one transaction. | Unique `transaction_id` lineage link. |
| INV-05 | Import commit is atomic. | One database session transaction and rollback on failure. |
| INV-06 | Every source row has an accounted final outcome after commit. | Count reconciliation. |
| INV-07 | Recommitting the same import does not recreate rows. | Row lock and committed-state check. |
| INV-08 | Exact duplicate classification is deterministic. | Canonical normalization, SHA-256 fingerprint, owner uniqueness. |
| INV-09 | Only trusted transactions feed financial reads. | Analytics/summary/export queries target `transactions`. |
| INV-10 | Default categories and rules cannot be privately changed or deleted. | Route-level business rules and ownership semantics. |
| INV-11 | Imported accepted value equals saved trusted value. | Post-commit `Decimal`/`NUMERIC` reconciliation through lineage detects disagreement. |

## 6. Contracts, failures, and security

### 6.1 Human-readable API catalogue

OpenAPI remains the field-level contract. This table records intent and security
boundaries without duplicating generated schemas.

| Method | Endpoint | Auth | Responsibility |
|---|---|---|---|
| `GET` | `/`, `/health` | No | Process and dependency health signals. |
| `POST` | `/auth/register`, `/auth/login` | No | Create an account or obtain an access token. |
| `GET/POST` | `/auth/me`, `/auth/logout` | Yes | Read identity or revoke the current token. |
| `GET/POST/PATCH/DELETE` | `/transactions` and `/{id}` | Yes | Owner-scoped transaction CRUD and paging. |
| `GET` | `/transactions/summary`, `/transactions/export.csv` | Yes | Trusted summary and filtered CSV export. |
| `GET/POST/PATCH/DELETE` | `/categories` and `/{id}` | Yes | Default/private category reads and private-category changes. |
| `GET/POST/PATCH/DELETE` | `/rules` and `/{id}` | Yes | Default/private categorization-rule management. |
| `GET/POST` | `/imports/presets`, `/imports`, `/imports/upload` | Yes | Discover mappings or stage a CSV/string import. |
| `GET/PATCH` | `/imports/{id}`, `/imports/{id}/rows/{row_id}` | Yes | Paginated staged review and duplicate decisions. |
| `POST/GET` | `/imports/{id}/commit`, `/imports/{id}/reconciliation` | Yes | Atomic commit and integrity result. |
| `GET` | `/analytics/*` | Yes | Owner-scoped SQL analytical read models. |

### 6.2 Error architecture

| HTTP result | ClearSpend meaning | Typical example |
|---|---|---|
| `400` | Not currently a primary application mapping. | FastAPI/Pydantic maps understood malformed payloads to `422`. |
| `401` | Missing, invalid, expired, or revoked authentication. | Bad bearer token. |
| `404` | Resource absent or hidden by owner-scoped lookup. | Another owner's import ID. |
| `409` | Current resource state or uniqueness conflicts with the operation. | Re-review committed import; competing duplicate commit. |
| `413` | Upload exceeds the 5 MiB limit. | Oversized multipart CSV. |
| `422` | Structurally understood input violates validation/business rules. | Bad mapping, date range, category, or CSV. |
| `5xx` | Unexpected application/dependency failure. | PostgreSQL unavailable or unhandled fault. |

FastAPI/Pydantic convert transport failures into response bodies; routes convert
known domain/state failures into stable status codes; frontend API modules turn
non-success responses into UI messages. User-facing errors may describe a safe
correction. Operator diagnostics must preserve the error class and context but
must not disclose another owner's resource or sensitive payload.

### 6.3 Failure and recovery matrix

| Failure | User-visible behavior | Internal/data behavior | Recovery |
|---|---|---|---|
| Malformed CSV row | Row marked invalid with a reason. | Raw row remains staged; valid rows survive. | Correct source/mapping and import again. |
| Invalid CSV/mapping or over 100K rows | `422`; import not completed. | Staging transaction rolls back. | Fix input or split it. |
| File over 5 MiB | `413`. | Nothing is staged. | Upload a smaller file. |
| Exact/possible duplicate | Visible classification/review. | Not silently double-committed. | Review or accept reported duplicate. |
| Database error during commit | Request fails. | Database transaction rolls back atomically. | Restore dependency and retry. |
| Invalid/revoked JWT | `401`. | Request is rejected before resource access. | Log in again. |
| Cross-owner ID | `404`. | Owner predicate returns no private record. | No recovery; access is intentionally denied. |
| Category still referenced | `409`. | Category remains unchanged. | Reassign/remove references first. |
| Browser request interrupted | UI reports/stops waiting. | Backend may finish a synchronous request. | Refresh import state before retrying. |

### 6.4 Security and lightweight threat model

Protected assets are credentials, JWTs, transaction data, staged raw rows,
ownership metadata, exports, and database secrets. Principal threats and current
controls are:

| Threat | Current controls |
|---|---|
| Cross-user data access | Authenticated current user, owner-scoped queries, hidden `404`, contract tests. |
| Password/token compromise | Argon2 password hashing, signed expiring JWTs, logout revocation. |
| Injection/malformed input | Pydantic validation, SQLAlchemy parameters, CSV/mapping validation. |
| Oversized or abusive CSV | 5 MiB and 100K-row limits, streaming, bounded batches/pages. |
| Duplicate/replayed writes | Fingerprints, uniqueness, locks, idempotent import commit. |
| Secret/data leakage | Environment configuration; responses exclude password hashes and raw cross-owner data. |

**KNOWN LIMITATIONS:** local defaults include a development-only signing secret;
there is no refresh-token rotation, rate limiting, CSP/security-header policy,
malware scanning, encryption-key management, external secrets manager, or formal
security review. Production use would require those decisions.

## 7. Source-code map

The repository is divided into fundamental units. Each unit has one primary
reason to change and a clear boundary with the others.

## 7.1 Root configuration and project entry points

This block defines installation, local infrastructure, documentation entry
points, and repository hygiene.

| File | Responsibility |
|---|---|
| `README.md` | Short product introduction, measured results, setup, verification commands, and links to deeper documentation. |
| `PROJECT_REFERENCE.md` | This canonical, complete map of the product and repository. |
| `pyproject.toml` | Python package metadata, runtime/dev dependencies, Pytest settings, package discovery, and Ruff policy. |
| `compose.yaml` | Local PostgreSQL 17 service, health check, port mapping, persistent volume, and initialization mount. |
| `alembic.ini` | Alembic script location and migration logging configuration. |
| `.env.example` | Safe template for application name, database URL, token secret, token lifetime, and frontend origin. |
| `.gitignore` | Prevents local databases, environments, secrets, caches, and build artifacts from entering Git. |
| `.gitattributes` | Normalizes line endings for Python, Markdown, TOML, INI, and example files. |

**Frameworks and principles.** Python packaging follows PEP 517 through
`setuptools`. Configuration follows the twelve-factor principle by allowing
environment variables to replace defaults. Docker Compose supplies a repeatable
database without requiring PostgreSQL to be installed directly on the host.

**Why this design.** SQLite keeps first-run development simple; PostgreSQL
provides production-like constraints, query plans, window functions, and bulk
loading. Both are intentional because the project needs low-friction local use
and credible database integration evidence.

**Advantages.** Setup is reproducible, secrets stay outside source control, and
the same package installs in local development and CI.

**Drawbacks.** Supporting two database engines creates dialect and migration
testing work. Docker Compose uses development credentials and is not a production
deployment definition.

**Standout feature.** The root configuration supports a genuinely dual-database
test story rather than mentioning PostgreSQL without exercising it.

## 7.2 `app/`: backend application

`app/` is the deployable FastAPI package. It uses a layered design: routes handle
HTTP, schemas validate contracts, services implement reusable decisions, models
describe persistence, and `db`/`core` provide infrastructure.

### 7.2.1 Application composition and shared infrastructure

| File | Responsibility |
|---|---|
| `app/main.py` | Application factory; registers CORS and the auth, category, rule, health, transaction, analytics, and import routers. Exposes the ASGI `app`. |
| `app/core/config.py` | Loads typed settings with `pydantic-settings` from defaults, environment variables, and optional `.env`. |
| `app/db/base.py` | Defines the shared SQLAlchemy declarative base used by all models and Alembic metadata. |
| `app/db/session.py` | Creates the database engine and session factory; applies SQLite's thread option only when needed. |
| `app/api/dependencies.py` | Provides request-scoped sessions, bearer-token parsing, revocation checks, and current-user resolution. |
| `app/__init__.py` | Marks `app` as a Python package. |
| `app/api/__init__.py` | Marks the API namespace as a package. |
| `app/api/routes/__init__.py` | Marks the route namespace as a package. |
| `app/core/__init__.py` | Marks the core configuration namespace as a package. |
| `app/db/__init__.py` | Marks the database namespace as a package. |

**Frameworks and principles.** FastAPI dependency injection manages session and
authentication lifetimes. The application-factory pattern lets tests build an
isolated app and override dependencies. SQLAlchemy's unit-of-work model keeps
database changes explicit.

**Why this design.** HTTP concerns should not create engines or decode tokens in
every route. Central dependencies ensure consistent cleanup and authentication.

**Advantages.** Routes stay focused, tests can replace the database dependency,
and configuration is centralized and typed.

**Drawbacks.** The session factory is synchronous, so long database work occupies
a worker thread. The default secret is development-only and requires deployment
configuration discipline.

**Standout feature.** The same application factory runs against an in-memory test
database, local SQLite, and PostgreSQL without route-specific changes.

### 7.2.2 API routes

| File | Responsibility |
|---|---|
| `app/api/routes/health.py` | Lightweight `/health` liveness response. |
| `app/api/routes/auth.py` | Registration, login, current-user lookup, logout, password hashing integration, generic credential errors, and token revocation persistence. |
| `app/api/routes/categories.py` | Lists shared/private categories and safely creates, reads, updates, or deletes user-owned categories while protecting defaults and referenced categories. |
| `app/api/routes/category_rules.py` | CRUD for ordered merchant-keyword rules, including category ownership checks, duplicate handling, activation, priority, and default-rule protection. |
| `app/api/routes/transactions.py` | Manual transaction CRUD, categorization, filtering, sorting, pagination, exact monthly summaries, and filtered CSV export. |
| `app/api/routes/transaction_imports.py` | Mapping presets, legacy JSON staging, streamed multipart uploads, batched staging, paginated/status-filtered preview, per-row decisions, locked commit, metrics, and reconciliation. |
| `app/api/routes/analytics.py` | Owner-scoped monthly trends, SQL window calculations, merchant/category summaries, largest transactions, and data-quality rate. |

**Frameworks and principles.** REST-style resources use explicit HTTP status
codes and Pydantic response models. Tenant isolation is applied in the query, not
after retrieval. SQL aggregation and window functions keep analytical work close
to the data. Streaming responses provide CSV downloads.

**Why this design.** Routes are grouped by resource so changes to imports,
transactions, or categories have an obvious home. The import route coordinates
the transaction boundary because it owns the workflow, while parsing details
remain in a service.

**Advantages.** OpenAPI documentation is generated automatically; ownership and
response contracts are consistent; analytical queries avoid moving raw datasets
into Python.

**Drawbacks.** `transaction_imports.py` currently coordinates several concerns
and is denser than the other route modules. The API is synchronous and does not
move 100K-row processing to a background job. CSV export currently constructs
the complete output string before yielding it.

**Standout feature.** The import API exposes an explainable workflow rather than
a single opaque upload endpoint: stage, inspect, decide, commit, and reconcile.

### 7.2.3 Services

| File | Responsibility |
|---|---|
| `app/services/categorizer.py` | Pure ordered keyword matching with default fallback rules and `Uncategorized` fallback. |
| `app/services/security.py` | Argon2 password hashing, HS256 JWT creation/verification, unique token IDs, expiry parsing, and typed token claims. |
| `app/services/transaction_imports.py` | CSV streaming, size/row constants, merchant/date/amount normalization, currency checks, fingerprints, exact/possible duplicate classification, and compatibility parsing helpers. |
| `app/services/__init__.py` | Marks the service namespace as a package. |

**Frameworks and principles.** Business transformations are deterministic and
mostly pure. Money uses `Decimal`; text comparison uses Unicode-aware
`casefold`; fingerprints use SHA-256 over canonical normalized fields. Generators
allow streaming classification.

**Why this design.** Parsing and categorization should be testable without an
HTTP request. Stable transformations are essential because fingerprints and
idempotency depend on producing the same output every time.

**Advantages.** Small functions support focused regression tests, generator-based
processing bounds memory, and the rule categorizer remains explainable.

**Drawbacks.** Possible-duplicate discovery loads an owner's existing fingerprint
and date/amount sets into memory. Merchant normalization is intentionally basic,
and debit versus credit direction is reduced to a positive spending amount.

**Standout feature.** A canonical transaction representation connects parsing,
deduplication, database uniqueness, and retry safety through one deterministic
fingerprint.

### 7.2.4 Database models

| File | Responsibility |
|---|---|
| `app/models/user.py` | User identity, normalized unique email, password hash, active state, creation time, and relationships to owned data. |
| `app/models/revoked_token.py` | Logged-out JWT IDs and expiry timestamps so logout invalidates a token immediately. |
| `app/models/category.py` | Shared defaults and private categories, owner/name uniqueness, descriptions, and relationships to transactions and rules. |
| `app/models/category_rule.py` | Keyword, target category, priority, active/default flags, owner-scoped uniqueness, and relationship-derived category name. |
| `app/models/transaction.py` | Exact amount, merchant, date, owner, category, optional import fingerprint, source-row relationship, uniqueness, and analytics indexes. |
| `app/models/transaction_import.py` | File-level state/counts/metrics plus row-level raw and normalized values, errors, statuses, review decisions, fingerprint, and transaction lineage. |
| `app/models/__init__.py` | Marks the model namespace as a package. Model modules are imported explicitly where metadata is assembled. |

**Frameworks and principles.** The schema uses normalization for trusted
entities, explicit foreign keys, unique constraints, referential integrity,
owner-scoped keys, exact numeric types, and indexes aligned with measured query
patterns. Staging intentionally contains denormalized raw JSON beside parsed
columns.

**Why this design.** Trusted transactions should be compact and queryable, while
staging must preserve imperfect input and its explanation. Database constraints
protect invariants even when application checks race.

**Advantages.** Source lineage is first-class; tenant uniqueness is encoded in
the schema; analytics filters have composite indexes; financial totals remain
exact.

**Drawbacks.** Status and state values are strings rather than database enums or
check constraints. Cascades are primarily ORM-defined. The fixed `Numeric(12,2)`
range and three-letter currency model may need extension for broader financial
domains.

**Standout feature.** A trusted transaction has an optional one-to-one path back
to the exact staged row and raw source record that created it.

### 7.2.5 Pydantic schemas

| File | Responsibility |
|---|---|
| `app/schemas/user.py` | Registration/login validation, normalized email, safe user output, and bearer-token response. |
| `app/schemas/category.py` | Category create/update/read contracts, whitespace cleaning, optional descriptions, and non-empty update enforcement. |
| `app/schemas/category_rule.py` | Rule create/update/read contracts, case-folded keywords, priority bounds, and non-null patch behavior. |
| `app/schemas/transaction.py` | Exact positive money validation, merchant/date cleaning, patch semantics, sort enums, page shape, and monthly summary shape. |
| `app/schemas/transaction_import.py` | Column mappings, staged rows, paginated import metadata, metrics, commit options, row decisions, presets, and reconciliation output. |
| `app/schemas/analytics.py` | Monthly trend, merchant, category, largest-transaction, and data-quality response contracts. |
| `app/schemas/__init__.py` | Marks the schema namespace as a package. |

**Frameworks and principles.** Pydantic acts as an anti-corruption layer between
untrusted JSON/form values and application objects. Separate create, update, and
read models avoid exposing storage-only fields or accepting server-owned values.

**Why this design.** Database nullability is not a sufficient API contract.
Schemas give clients predictable validation, generated OpenAPI definitions, and
precise decimal serialization.

**Advantages.** Invalid requests fail before business work; patch requests must
contain meaningful changes; enums constrain sorting and review decisions.

**Drawbacks.** Frontend TypeScript types are maintained manually rather than
generated from OpenAPI, so contract drift remains possible. Some import status
fields are free-form strings.

**Standout feature.** Reconciliation is a declared response type, making data
correctness part of the public API rather than an internal log message.

## 7.3 `.github/workflows/`: continuous integration

| File | Responsibility |
|---|---|
| `.github/workflows/clearspend-ci.yml` | Runs ClearSpend-only checks on relevant pushes and pull requests through backend-quality, PostgreSQL integration, migration round-trip, and frontend jobs. |

The workflow lives at the portfolio repository root because GitHub only discovers
workflows under root `.github/workflows`, even though all commands run from the
`clearspend` subdirectory.

**Frameworks and principles.** GitHub Actions provides continuous integration;
path filters avoid running ClearSpend jobs for unrelated portfolio projects;
jobs are separated by failure domain. PostgreSQL services provide disposable
databases. `npm ci` enforces the lockfile.

**Why this design.** Local success is not an enforceable quality signal. CI turns
the existing test and migration work into repeatable pull-request gates.

**Advantages.** SQLite and PostgreSQL behavior are both checked; migrations must
upgrade, fully downgrade, re-upgrade, and match model metadata; frontend lint,
types, tests, and build are independent of backend results.

**Drawbacks.** Separate Python jobs repeat dependency installation. The workflow
does not yet publish coverage, build containers, scan dependencies, or deploy.
Ruff currently emphasizes fatal errors and Pyflakes correctness rather than a
full style policy.

**Standout feature.** Database portability and migration reversibility are
enforced, not merely documented.

## 7.4 `docker/` and local PostgreSQL

| File | Responsibility |
|---|---|
| `docker/postgres/init.sql` | Creates the separate `transactions_test` database when the local PostgreSQL volume is initialized. |
| `compose.yaml` | Defines the PostgreSQL container that consumes the initialization script. |

**Frameworks and principles.** Disposable infrastructure and environment
parity keep integration testing close to production database behavior. Separate
development and test databases reduce accidental data loss.

**Why this design.** Tests create and drop schema objects, so they must never run
against the normal development database.

**Advantages.** One command starts a health-checked PostgreSQL 17 instance with
persistent development data and isolated test space.

**Drawbacks.** The initialization script runs only for a new volume. The local
port and credentials are development conventions, and port conflicts can still
occur on a busy machine.

**Standout feature.** Test isolation is designed into database provisioning.

## 7.5 `frontend/`: React client

The frontend is a Vite-built React 19 single-page application. It keeps server
data authoritative and calls the API through small typed modules.

### 7.5.1 Frontend configuration and entry files

| File | Responsibility |
|---|---|
| `frontend/package.json` | Runtime/dev dependencies and commands for development, ESLint, explicit type-checking, Vitest, and production build. |
| `frontend/package-lock.json` | Exact npm dependency graph used by `npm ci` locally and in CI. |
| `frontend/vite.config.ts` | Vite configuration with the React plugin. |
| `frontend/tsconfig.json` | TypeScript project references for browser and tooling configurations. |
| `frontend/tsconfig.app.json` | Strict no-emit browser/React compilation settings and source inclusion. |
| `frontend/tsconfig.node.json` | TypeScript settings for Vite's Node-side configuration. |
| `frontend/eslint.config.js` | ESLint flat configuration with JavaScript, TypeScript, React Hooks, and Vite refresh rules. |
| `frontend/index.html` | Browser HTML shell, root mount point, title metadata, and favicon reference. |
| `frontend/src/main.tsx` | Mounts the React application under `StrictMode` and loads global CSS. |
| `frontend/src/index.css` | Global typography, colors, sizing defaults, and form-control inheritance. |
| `frontend/src/App.tsx` | Top-level authentication and screen state; selects overview, transactions, or imports and coordinates logout. |
| `frontend/src/App.css` | Shared shell, sidebar, dashboard, summary-card, modal, button, and responsive styles. |

**Frameworks and principles.** React uses component state and effects rather than
a global state library. TypeScript runs in strict no-emit mode. Vite handles local
development and production bundling. Browser and Node compiler settings remain
separate through project references.

**Why this design.** The current application state is small enough that local
component ownership is easier to understand than adding Redux or another state
framework. Server responses remain the source of truth.

**Advantages.** The client has few dependencies, fast builds, clear screen
boundaries, and compile-time API shapes.

**Drawbacks.** Authentication state is memory-only and disappears on refresh.
Navigation is state-based rather than URL-routed. Several screens are large
components, and API types are handwritten.

**Standout feature.** The frontend exposes the data pipeline's review and
reconciliation concepts instead of hiding them behind a generic upload spinner.

### 7.5.2 API client modules

| File | Responsibility |
|---|---|
| `frontend/src/api/auth.ts` | Registration, login, current-user, logout requests, bearer headers, and authentication error extraction. |
| `frontend/src/api/categories.ts` | Loads visible default and user-owned categories for forms and filters. |
| `frontend/src/api/transactions.ts` | Transaction and monthly-summary types plus create, update, delete, filtered/paginated list, and summary requests. |
| `frontend/src/api/imports.ts` | Import/mapping/reconciliation types plus multipart staging, paginated retrieval, row decisions, commit, and safe error-message extraction. |
| `frontend/src/api/imports.test.ts` | Vitest coverage for FastAPI detail extraction and non-JSON fallback behavior. |

**Frameworks and principles.** A small gateway layer keeps fetch details out of
pages. `FormData` streams uploaded files without manually setting a multipart
boundary. Abort signals are used for cancellable reads where screens can unmount.

**Why this design.** Central request functions make page components describe UI
state rather than repeat URL, header, and parsing logic.

**Advantages.** Network behavior is reusable and typed; errors are translated
into user-readable messages; import upload uses the browser's multipart support.

**Drawbacks.** Error handling is not yet unified across all modules. There is no
generated API client, retry policy, request cache, or refresh-token mechanism.

**Standout feature.** `imports.ts` models both row-level review state and final
reconciliation, preserving the backend's correctness vocabulary in the UI.

### 7.5.3 Pages and components

| File | Responsibility |
|---|---|
| `frontend/src/pages/LoginPage.tsx` | Credential form, login request, current-user fetch, error/loading states, and transition to registration. |
| `frontend/src/pages/RegisterPage.tsx` | Registration form, password confirmation/visibility, validation feedback, success state, and return to login. |
| `frontend/src/pages/RegisterPage.css` | Registration layout and responsive styling. |
| `frontend/src/pages/DashboardPage.tsx` | Authenticated shell content, current-month summary, top-category calculation, navigation, logout access, and manual transaction modal. |
| `frontend/src/pages/TransactionsPage.tsx` | Category loading, transaction filters, sorting, paging, edit/delete flows, confirmation dialog, and list feedback. |
| `frontend/src/pages/TransactionsPage.css` | Transaction filters, table, pagination, empty state, and delete-dialog styling. |
| `frontend/src/pages/ImportPage.tsx` | File selection, header sampling, mapping guesses, streamed staging, paginated preview, per-row duplicate decisions, commit fallback, and reconciliation display. |
| `frontend/src/pages/ImportPage.css` | Mapping grid, import summary, status pills, review table, pagination, errors, and reconciliation styling. |
| `frontend/src/components/TransactionForm.tsx` | Shared create/edit transaction modal with controlled inputs, local-date default, submission states, and callbacks. |

**Frameworks and principles.** Controlled forms make state explicit; effects use
cleanup through `AbortController`; shared components avoid duplicating create and
edit behavior; semantic status/alert roles improve accessibility.

**Why this design.** Each page owns the data needed for its workflow, while the
top-level app only owns authentication and screen selection.

**Advantages.** User flows are easy to trace from component to API module;
loading, empty, success, and error states are explicit; import preview remains
bounded through pagination.

**Drawbacks.** `ImportPage.tsx` and `TransactionsPage.tsx` are large and should be
split if their workflows grow. CSV header guessing uses simple comma splitting,
so quoted headers containing commas can be guessed incorrectly even though the
backend parses the actual file correctly. Category and rule management currently
have APIs but no dedicated frontend screens.

**Standout feature.** The import page lets a user see and decide what will happen
before trusted financial records change.

### 7.5.4 Static assets

| File | Responsibility |
|---|---|
| `frontend/public/favicon.svg` | Browser favicon referenced by `index.html`. |
| `frontend/public/icons.svg` | Public SVG sprite/source asset; currently not referenced by application code. |
| `frontend/src/assets/hero.png` | Image asset retained in the source tree; currently not referenced. |
| `frontend/src/assets/react.svg` | Vite template React asset; currently not referenced. |
| `frontend/src/assets/vite.svg` | Vite template asset; currently not referenced. |

**Advantages.** Public assets can be served without bundler imports, while source
assets can be optimized and fingerprinted when imported.

**Drawbacks.** The unused template/source assets add noise and can be removed in
a later cleanup.

**Standout feature.** The active interface is primarily CSS-driven and does not
depend on a large image or icon package.

## 7.6 `migrations/`: database evolution

Alembic migrations are the ordered history of the schema. Application startup
does not create production tables implicitly; environments move to a known
revision through explicit commands.

| File | Responsibility |
|---|---|
| `migrations/env.py` | Loads settings, imports all models into shared metadata, and configures online/offline migrations with type comparison. |
| `migrations/script.py.mako` | Template used when generating a new revision. |
| `migrations/versions/20260808_01_create_transactions.py` | Creates the original transaction table. |
| `migrations/versions/20260808_02_add_transaction_indexes.py` | Adds the initial date and merchant indexes for common filters. |
| `migrations/versions/20260808_03_create_categories.py` | Creates normalized categories, seeds defaults, links transactions, and migrates earlier category strings. |
| `migrations/versions/20260808_04_create_category_rules.py` | Creates categorization rules and seeds ordered starter rules. |
| `migrations/versions/20260809_05_create_users.py` | Creates authenticated user accounts. |
| `migrations/versions/20260809_06_add_transaction_owners.py` | Adds transaction ownership and safely assigns legacy rows to a disabled migration user. |
| `migrations/versions/20260809_07_add_category_and_rule_owners.py` | Separates shared defaults from private categories/rules and handles legacy ownership. |
| `migrations/versions/20260809_08_create_revoked_tokens.py` | Adds persisted JWT revocation records and expiry indexes. |
| `migrations/versions/20260824_09_create_transaction_imports.py` | Adds fingerprints, staging imports/rows, raw/normalized data, statuses, and source lineage. |
| `migrations/versions/20260824_10_add_import_metrics.py` | Adds import timing/throughput/buffer metrics and per-row review decisions. |
| `migrations/versions/20260824_11_add_analytics_indexes.py` | Adds composite owner/date and owner/merchant indexes for tenant-scoped queries. |

**Frameworks and principles.** Schema evolution is versioned, reversible, and
data-aware. Batch table alteration supports SQLite where direct constraint
changes are unavailable. Legacy migrations preserve existing data instead of
assuming an empty database.

**Why this design.** Model definitions describe the desired current schema;
migrations describe how real existing databases safely reach it.

**Advantages.** CI verifies upgrade, downgrade, re-upgrade, and metadata drift.
The history demonstrates normalization and multi-tenant evolution rather than a
single generated snapshot.

**Drawbacks.** Full downgrade is useful for verification but would be destructive
on a real production database and should not be used as a rollback strategy for
financial data. Seeded defaults are embedded in historical migrations.

**Standout feature.** Ownership was introduced with an explicit legacy-data
strategy, showing that schema changes consider existing rows.

## 7.7 `scripts/`: reproducible engineering evidence

| File | Responsibility |
|---|---|
| `scripts/benchmark_import_pipeline.py` | Generates anonymous CSV/insert data; measures streamed parsing/validation memory and throughput; compares row-at-a-time, batch, bulk execute, and PostgreSQL `COPY`. |
| `scripts/measure_index_performance.py` | Builds a temporary 50K-row PostgreSQL table and measures a date query before and after indexing. |
| `scripts/explain_analytics.py` | Runs `EXPLAIN (ANALYZE, BUFFERS)` for monthly trends, merchant aggregation, and filtered export. |

**Frameworks and principles.** Performance claims are tied to executable,
generated-data experiments. `perf_counter` measures elapsed time, `tracemalloc`
tracks Python allocations, and PostgreSQL plans reveal actual access methods.

**Why this design.** A resume claim is more credible when another developer can
run the same workload and inspect the method.

**Advantages.** No personal finance data is required; database benchmark tables
are scoped and removed; insertion strategies are compared under the same shape.

**Drawbacks.** Microbenchmarks vary by machine, cache state, tracing overhead,
and database configuration. The processing benchmark does not reproduce browser
or network time, and a synthetic distribution cannot represent every bank file.

**Standout feature.** Performance is treated as measured evidence, including a
baseline and alternatives, rather than an unqualified “optimized” claim.

## 7.8 `tests/`: executable behavior specification

`tests/conftest.py` runs the same suite against an in-memory SQLite database by
default or PostgreSQL when `TEST_DATABASE_URL` is set. It creates a fresh schema,
seeds a user, shared categories, and ordered rules, overrides FastAPI's session
dependency, supplies a bearer token, and drops the schema afterward.

| File | Responsibility |
|---|---|
| `tests/__init__.py` | Marks the test directory as a package. |
| `tests/conftest.py` | Isolated database/client fixture, deterministic seed data, dependency override, authentication setup, and teardown. |
| `tests/test_auth.py` | Registration, normalized duplicate emails, login, generic credential errors, token validation/expiry, logout revocation, and CORS. |
| `tests/test_categories.py` | Default/private category visibility, CRUD, uniqueness, ownership, references, authentication, and protected defaults. |
| `tests/test_category_rules.py` | Rule ordering, activation, ownership, uniqueness, category relationships, protected defaults, and categorization effects. |
| `tests/test_categorizer.py` | Parameterized unit tests for the pure merchant keyword matcher and fallback. |
| `tests/test_transactions.py` | Transaction validation, categorization, CRUD, filters, sort, pagination, monthly exact totals, ownership, and authentication. |
| `tests/test_transaction_imports.py` | Staging, mappings, normalization, invalid rows, reconciliation, exact/possible duplicates, retries, privacy, streaming, pagination, metrics, row review, conflict rollback, and repeated commit. |
| `tests/test_analytics.py` | Window calculations, exact merchant/category totals, largest transactions, data-quality rate, ownership, empty results, and CSV filtering. |
| `tests/test_api_contract.py` | Deliberate HTTP contract for success codes, JSON/CSV media types, malformed and oversized uploads, bearer errors, owner hiding, conflicts, idempotency, invalid states, pagination, methods, and download headers. |

**Frameworks and principles.** Pytest fixtures isolate state; FastAPI's
`TestClient` exercises the HTTP boundary; dependency inversion replaces the
database session; parameterization keeps pure-rule tests compact. The same
behavior suite is reused as a database compatibility test.

**Why this design.** Unit tests alone would not prove routing, validation,
serialization, ownership filters, or transactions. API tests verify behavior at
the boundary users and clients actually depend on.

**Advantages.** Eighty backend tests run on both databases. Contract behavior is
explicit, and conflict tests prove rollback leaves no partial trusted rows.

**Drawbacks.** Most tests are synchronous and in-process. There are no browser
end-to-end tests, load-test assertions, property-based parsing tests, or fault
injection for a database connection disappearing mid-commit.

**Standout feature.** One suite verifies both lightweight development behavior
and real PostgreSQL integration instead of maintaining divergent test sets.

## 7.9 `docs/`: supporting documentation

This directory contains focused deep dives. It should support—not compete with—
this canonical reference.

| File | Responsibility |
|---|---|
| `docs/database-design.md` | Detailed rationale for staging, trusted tables, raw/normalized fields, ownership, fingerprints, money, transactions, indexes, and reconciliation. |
| `docs/import-pipeline.md` | Import API flow, supported normalization behavior, invariants, benchmark commands, and recorded pipeline/insertion results. |
| `docs/analytics.md` | Available analytical read models, SQL techniques, ownership, and exact-value behavior. |
| `docs/postgresql.md` | Local PostgreSQL setup, separate test database, index benchmark, analytics-plan tooling, and shutdown instructions. |

**Frameworks and principles.** Documentation is layered: one canonical map,
short onboarding in the README, and decision records in focused guides.

**Why this design.** One enormous file is useful for complete orientation but
inefficient for every task. Focused documents let a developer go deeper after
finding the relevant block here.

**Advantages.** Product intent, code ownership, database rationale, operating
commands, and measurements are all documented without forcing the README to
become a manual.

**Drawbacks.** Documentation can drift. Historical documents contain older plans
by design, so their role must remain clearly labeled.

**Standout feature.** The documentation explains not only what exists, but why
the boundaries and invariants exist.

## 8. Cross-cutting engineering

### Exactness over convenience

Financial amounts use `Decimal`/`NUMERIC`, and correctness is checked through
count and money reconciliation. Binary floating point is intentionally excluded
from money paths.

### Explainability over silent automation

Raw rows, normalized rows, validation reasons, duplicate classifications, and
review decisions remain visible. Rule-based categorization is deterministic and
falls back safely.

### Defense in depth

Pydantic validates the HTTP contract, services normalize values, route logic
checks ownership and workflow state, transactions make multi-write operations
atomic, and database constraints handle races.

### Tenant isolation at query time

Owner filters are included in database queries. Data is not fetched broadly and
filtered in Python. Cross-owner resource lookup intentionally returns `404`.

### Bounded processing

Uploads have byte and row limits, parsing uses a generator, staging writes in
batches, and previews are paginated. These choices reduced measured peak Python
memory for 100K generated rows by 76.4%.

### Reproducibility

Migrations define schema history, lockfiles define frontend dependencies, Docker
defines local PostgreSQL, benchmark scripts define performance experiments, and
CI defines required checks.

### Error, transaction, and observability ownership

Routes own HTTP status translation and commit/rollback coordination. Services
own reusable parsing and normalization failures. Database constraints are the
last write-integrity boundary. The frontend owns presentation, not
reinterpretation of backend error semantics.

**IMPLEMENTED observability:** Uvicorn request logs, persisted per-import parsing,
validation, staging and commit times, rows/second, counts, and estimated peak
batch memory; benchmark scripts expose query plans and timings.

**PLANNED observability:** structured request IDs, safe user identifiers, import
IDs, endpoint latency, 5xx rate, duplicate rate, reconciliation-failure alerts,
and database latency dashboards. Passwords, JWTs, raw CSV contents, and full
financial exports must never be logged. Current metrics are diagnostic fields,
not a production monitoring system.

## 9. Testing and verification

### 9.1 Requirements traceability

| Requirement | Unit/service | API | PostgreSQL | Contract | Frontend | Browser E2E |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Exact money | Yes | Yes | Yes | — | — | — |
| Owner isolation | — | Yes | Yes | Yes | — | — |
| Idempotent import | Yes | Yes | Yes | Yes | — | — |
| Atomic rollback/concurrency | — | Yes | Yes | Yes | — | — |
| Duplicate classification/review | Yes | Yes | Yes | Yes | Yes | — |
| Count and money reconciliation | Yes | Yes | Yes | Yes | Yes | — |
| Pagination/status/content type | — | Yes | Yes | Yes | Yes | — |
| Import API client behavior | — | — | — | — | Yes | — |
| Complete browser journey | — | — | — | — | Partial | Planned |

`Yes` means an existing test layer directly exercises the property; it does not
mean every possible case is proven. The 80-test backend result includes
parameterized cases even though there are fewer textual test functions.

### 9.2 CI verification matrix

| Gate | Environment | Enforced check |
|---|---|---|
| Backend quality | Python 3.11 + SQLite | Ruff and complete Pytest suite. |
| Database integration | Python 3.11 + PostgreSQL 17 | Same complete Pytest suite against PostgreSQL. |
| Schema evolution | PostgreSQL 17 | Upgrade head, downgrade base, re-upgrade, `alembic check`. |
| Frontend | Node 22 | Clean install, ESLint, TypeScript, Vitest, production build. |

**VERIFIED:** 80 backend tests passed on SQLite and PostgreSQL; Ruff, migration
round trip, frontend lint, type-check, two Vitest tests, and production build
passed in the documented development verification. CI makes those checks pull-
request gates. There is no coverage threshold, security scan, container build,
or browser E2E gate yet.

## 10. Performance engineering

### 10.1 Measurements and method

- **MEASURED:** generated 100K-row processing reduced peak Python allocation
  from 126.85 MiB to 29.99 MiB after streaming, batching, and pagination.
- **MEASURED:** PostgreSQL `COPY` reached about 66,108 rows/second for the
  documented generated 10K-row run, 87.8 times row-at-a-time and 10.3 times
  SQLAlchemy bulk execute in that run.
- **MEASURED:** a representative date query improved from 10.107 ms to 0.840 ms
  after indexing.

Scripts, generated-data shapes, commands, and caveats live in
`docs/import-pipeline.md` and `docs/postgresql.md`. Results characterize one
machine and database state; they are evidence, not universal guarantees.

### 10.2 Budgets and regression boundaries

| Area | Current engineering boundary |
|---|---|
| Upload | Hard limit: 5 MiB and 100,000 rows. |
| Staging | Fixed 1,000-row write batches; no full-file row list. |
| Preview | 1–500 rows per response; default 100. |
| Commit | Rows streamed with `yield_per(1,000)` inside one transaction. |
| Analytics | Aggregation/window work remains in SQL rather than unbounded Python materialization. |
| Latency/SLO | No formal production p95/p99 latency or availability SLO exists. |

A change is a regression if it removes these bounds or materially exceeds the
recorded benchmark under the same fixture without an explained tradeoff. Formal
latency and throughput budgets should be set only after a representative
deployment and workload exist.

## 11. Operations

### 11.1 Routine commands

| Task | Command or source |
|---|---|
| Install backend | `python -m pip install -e ".[dev]"` |
| Start PostgreSQL | `docker compose up -d database` |
| Check PostgreSQL | `docker compose ps` |
| Apply schema | `python -m alembic upgrade head` |
| Show schema revision | `python -m alembic current` |
| Start API | `python -m uvicorn app.main:app --reload` |
| Start frontend | From `frontend`: `npm install`, then `npm run dev` |
| Stop PostgreSQL safely | `docker compose stop database` (volume retained) |
| SQLite tests | Clear `TEST_DATABASE_URL`, then `python -m pytest` |
| PostgreSQL tests | Set the test URL from `docs/postgresql.md`, then `python -m pytest` |
| One backend test | `python -m pytest tests/<file>.py -k <name>` |
| Migration validation | Upgrade, downgrade, re-upgrade, then `python -m alembic check`. |
| Import benchmark | `python scripts/benchmark_import_pipeline.py --help` |
| Inspect slow analytics | Set PostgreSQL `DATABASE_URL`; run `python scripts/explain_analytics.py`. |

The API exposes interactive OpenAPI documentation at
`http://127.0.0.1:8000/docs`. Reproduce an import failure with anonymous or
generated data, preserve the response status/detail and import ID, then inspect
staged row reasons and reconciliation; never attach real bank exports to issues.

### 11.2 Backup, restore, and migration recovery

**KNOWN LIMITATION:** the repository does not automate PostgreSQL backup or
restore and defines no production recovery-point/recovery-time objective. Before
any production-like migration, take and verify a PostgreSQL-native backup using
the operator's deployment tooling. Test restore into a separate database; never
validate recovery by overwriting the only copy.

For a bad development migration, inspect `alembic current` and `alembic history`,
fix the revision, and validate upgrade/downgrade against a disposable database.
Use `alembic downgrade` on valuable data only when the revision's downgrade is
understood and a verified backup exists. Destructive database-volume reset is
deliberately absent from routine instructions.

When PostgreSQL is unavailable, stop writes, restore the dependency, confirm its
health, inspect the current migration revision, and retry idempotent operations.
An interrupted import commit should be checked through its state/reconciliation
endpoint before the user retries.

## 12. Engineering decisions

These lightweight ADRs preserve reasoning likely to be lost. Each is a current
decision, not an irreversible rule.

| ADR | Decision and rejected alternative | Consequence / revisit trigger |
|---|---|---|
| ADR-001 | Persist raw and normalized rows in staging; reject direct validate-and-insert. | Enables review, lineage, and partial validity. Revisit only if an equally explainable workflow replaces staging. |
| ADR-002 | Use `Decimal`/`NUMERIC`; reject floating point for money. | Exact arithmetic with explicit serialization; not expected to change. |
| ADR-003 | Make fingerprints and uniqueness owner-scoped; reject global transaction uniqueness. | Users may own identical records while retries remain safe. |
| ADR-004 | Support SQLite and PostgreSQL tests; reject PostgreSQL-only first-run setup. | Easy onboarding plus real DB evidence, at the cost of compatibility discipline. |
| ADR-005 | Aggregate analytics in SQL; reject loading transactions into Python. | Bounded application memory and query-plan visibility. |
| ADR-006 | Run imports synchronously; defer a durable worker queue. | Simpler deployment, but request lifetime limits scale. Revisit when import duration becomes operationally significant. |
| ADR-007 | Hide cross-owner resources with `404`; reject existence-revealing responses. | Better privacy, with less distinction between absent and forbidden resources. |
| ADR-008 | Stream parsing and batch staging; reject whole-file `read()` processing. | Bounded memory and better large-file behavior, with more involved control flow. |
| ADR-009 | Keep frontend API types manual; defer OpenAPI generation. | Low tooling overhead but contract-drift risk. Revisit as API/frontend breadth grows. |

## 13. Safe-change guide

### 13.1 Change-impact matrix

| Change | Backend | Schema/migration | API contract | Frontend | Tests/CI | Docs |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| New analytics endpoint | Yes | Maybe | Yes | Maybe | Yes | Yes |
| New transaction field | Yes | Yes | Yes | Yes | Yes | Yes |
| New import normalization rule | Yes | No | Maybe | Maybe | Critical | Yes |
| Fingerprint inputs/algorithm | Yes | Maybe | Usually no | No | Critical | Yes/ADR |
| Authentication claims/lifetime | Yes | Maybe | Yes | Yes | Critical | Yes/security |
| Import state or row outcome | Yes | Yes | Yes | Yes | Critical | Yes/state machine |
| Category deletion behavior | Yes | Maybe | Yes | Maybe | Yes/concurrency | Yes |

For a new transaction field, update the model, create an Alembic revision,
update schemas/routes, decide whether imports and fingerprints use it, update
frontend types/forms, add SQLite and PostgreSQL API tests, run the migration
round trip, and update this reference.

### 13.2 Starting points

| Goal | Start here |
|---|---|
| Understand the product | Sections 1–6 of this reference. |
| Change CSV parsing | Import service, schemas, route, and import tests. |
| Change commit semantics | Import route/models, invariants/state machine, PostgreSQL reconciliation/concurrency tests. |
| Add analytics | Analytics route/schema/tests, plan script, performance and API catalogues. |
| Change authentication | Auth route, security service, user/token models, contract tests, threat model. |
| Change database | Models, new Alembic revision, both database suites, migration round trip, ERD. |
| Change import UI | `ImportPage.tsx`, API client/types, CSS, Vitest, and contract assumptions. |
| Diagnose PostgreSQL | `docs/postgresql.md`, Compose, benchmark scripts, and `explain_analytics.py`. |
| Understand quality gates | Workflow, `pyproject.toml`, frontend scripts, and Section 9. |

## 14. Current strengths and technical debt

### Strongest parts

- Explainable, idempotent import lifecycle with source lineage.
- Database-backed reconciliation and exact financial calculations.
- PostgreSQL-specific evidence: integration tests, `COPY`, indexes, plans, and
  reversible migrations.
- Measured streaming memory improvement and insertion alternatives.
- Deliberate HTTP contract and owner-hiding semantics.
- CI enforcement across backend, PostgreSQL, migrations, and frontend.

### Important limitations

- Authentication has no refresh-token or browser persistence strategy.
- Large imports run synchronously rather than through a durable job queue.
- Possible-duplicate matching is heuristic and loads owner candidate sets into
  application memory.
- Debit and credit direction is simplified into positive spending amounts.
- The frontend has no URL router, browser end-to-end suite, or category/rule
  management screens.
- Frontend API types are manual rather than generated from OpenAPI.
- Import and analytics route modules would benefit from further decomposition.
- CI has no coverage threshold, security scanner, container build, or deployment.
- Reconciliation is calculated after the commit transaction; it detects a count
  or money mismatch but does not itself roll back already committed rows.
- There is no formal structured logging/metrics pipeline, backup automation,
  production topology, disaster-recovery target, or latency SLO.
- Unused frontend template assets still warrant cleanup.

## 15. Glossary

| Term | Precise meaning in ClearSpend |
|---|---|
| Trusted transaction | A row in `transactions` allowed to feed financial reads. |
| Staging row / import row | Preserved source evidence plus ClearSpend's interpretation and workflow outcome. |
| Source-row lineage | The unique optional link from an imported staging row to its resulting transaction. |
| Exact duplicate | A row whose deterministic fingerprint already exists for the same owner. |
| Possible duplicate | Same date/amount with differing merchant context; requires an explicit/default decision. |
| Fingerprint | SHA-256 identity derived from canonical normalized transaction fields. |
| Review decision | Approval or rejection applied to a possible duplicate. |
| Commit | Atomic promotion of accepted staging rows into trusted transactions. |
| Reconciliation | Count and monetary proof that import outcomes and saved records agree. |
| Owner hiding | Returning no resource/`404` when an ID belongs to another user. |
| Mapping preset | Reusable mapping from bank-specific CSV headers to canonical fields. |
| Default entity | Category/rule with no private owner, readable but not privately mutable. |

## 16. Documentation maintenance rule

Update this reference when a block gains, loses, or changes responsibility; when
a file is added or removed; or when a major architectural tradeoff changes.
Update the README only for onboarding-visible changes. Record deep technical
details in the relevant focused guide and keep verified architectural outcomes
in this reference. Update `Last verified` only after rerunning checks relevant to
changed claims. Keep implemented, measured, planned, and limited behavior
visibly distinct.

The exhaustive tables in Section 7 form the complete file index. High-level
readers can stop after Sections 1–6; maintainers can use Sections 7–16 as the
engineering handbook and change reference.
