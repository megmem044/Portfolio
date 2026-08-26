# AnswerTrust project reference

**Status:** authoritative technical and product reference
**Last verified:** August 25, 2026

This is the single detailed reference for AnswerTrust. It describes the product,
its current implementation, every maintained project unit, the reasons behind
its design, and its known limitations. The root `README.md` remains the concise
entry point and runbook. When implementation changes, this document and the
README should be updated in the same change.

## 1. What AnswerTrust is

AnswerTrust is a paper-grounded quality-control system for AI-generated answers.
It accepts a research question, the text of one academic paper, and an answer to
check. It splits the answer into claims, retrieves relevant passages from the
paper, classifies each claim, and returns cited evidence, explanations, safety
signals, and an overall `PUBLISH`, `REVIEW`, or `REJECT` recommendation.

The key boundary is deliberate: the supplied paper is the evidence universe.
AnswerTrust does not browse the web, use general model knowledge as proof, or
decide whether the paper itself is scientifically true. It evaluates fidelity
to a source, not truth in the abstract.

The project began as a synchronous Streamlit/SQLite prototype and now uses a
React client, versioned FastAPI service, relational persistence, a Redis queue,
and a separate evaluation worker. The original evaluation behavior remains the
domain core; the surrounding system demonstrates how an ML subsystem can be
made asynchronous, testable, observable, auditable, and resource-aware.

### Product principles

- Ground every decision in the supplied paper.
- Show claim-level evidence instead of returning an unexplained score.
- Prefer abstention and human review when model confidence is insufficient.
- Keep ML inference outside the HTTP request path.
- Preserve the original system decision when a reviewer acts.
- Persist lifecycle transitions and make worker retries idempotent.
- Combine probabilistic ML with deterministic academic checks.
- Protect public resource boundaries with explicit input, rate, and queue limits.
- Treat current benchmark figures as regression results, not general scientific
  performance claims.

### AnswerTrust in five minutes

1. One supplied paper is the only allowed evidence source.
2. The answer is split into separate claims.
3. Retrieval finds paper passages that are related to each claim.
4. Clear rules and optional NLI classify each claim.
5. A fixed decision policy turns the claim results into `PUBLISH`, `REVIEW`, or
   `REJECT`.
6. Slow evaluation work runs in a worker. The database keeps the request,
   result, evidence, state, and human review history.

```text
User
  |
  v
React
  |
  v
FastAPI ----> database
  |
  v
Redis queue
  |
  v
Worker ----> retrieval + rules + optional NLI
  |
  v
database ----> React status polling
```

The most important design rule is simple: **ML does not directly choose
`PUBLISH`, `REVIEW`, or `REJECT`.** ML can provide evidence scores and an NLI
prediction. The fixed decision rules make the final system decision.

## 2. Main concepts

```text
User
  |-- may review ----------> Evaluation
  |                              |
  |                              |-- uses ------> Paper
  |                              |-- contains --> Claims
  |                              |                 |-- Evidence passages
  |                              |                 `-- Model prediction
  |                              `-- may create -> Review task
  |                                                  `-- Review decision
  `-- admin may run -------> Benchmark run
                                 `-- Benchmark results
```

| Term | Simple meaning |
| --- | --- |
| User | A reviewer or administrator account. Evaluation submission itself is currently public. |
| Paper | The exact text supplied by the user. It is the only allowed evidence source. |
| Evaluation | One full check of one AI answer against one paper and one question. |
| Claim | One statement taken from the answer that can be checked on its own. |
| Evidence passage | A section-labelled passage from the supplied paper used to judge a claim. |
| Model prediction | The NLI model's label and confidence. It is stored separately from the final claim label. |
| System decision | The original automatic `PUBLISH`, `REVIEW`, or `REJECT` result. Human review never replaces it. |
| Review task | A work item created when the system decision is `REVIEW`. |
| Review decision | A reviewer's `APPROVE` or `REJECT` choice, notes, identity, and time. |
| Benchmark run | One saved execution of a labelled test dataset. |
| Evaluation attempt | One worker try. The current schema stores the attempt count and latest failure message on the evaluation rather than in a separate attempt table. |

## 3. End-user use cases

### Primary use cases

1. **Pre-publication answer screening.** An editor or content team can check
   whether a generated summary overstates, contradicts, or goes beyond a paper.
2. **Research-assistant quality control.** A researcher can inspect which source
   passages support each generated claim before reusing the answer.
3. **Human-review triage.** Reviewers can focus on uncertain or risky answers
   while straightforward supported answers remain visible in the evaluation log.
4. **Evidence-oriented explanation.** A user can see section-labelled passages,
   claim labels, failure types, and NLI confidence rather than a single opaque
   verdict.
5. **Model or prompt regression testing.** Teams can run the publication safety
   benchmark, compare historical runs, and inspect error categories.
6. **Reviewer calibration.** De-identified review sheets and agreement metrics
   support comparison between project labels and independent reviewers.
7. **Responsible-AI portfolio demonstration.** The full stack demonstrates
   retrieval, hybrid ML/rules, asynchronous work, persistence, authentication,
   auditability, analytics, testing, and containerized delivery around one
   coherent safety problem.

### Deliberate non-use cases

AnswerTrust is not a substitute for peer review, clinical judgment, statistical
review, fact checking across multiple sources, or verification of a paper's own
methods. It does not perform multi-paper synthesis, general-purpose RAG,
autonomous publication, or model training. These exclusions keep the system's
claims and operational scope understandable.

## 4. System architecture and request flow

```text
React + TypeScript client
          |
          | versioned JSON REST API
          v
       FastAPI -------- authentication / validation / throttling
          |
          +-----------> PostgreSQL (SQLite fallback for local work)
          |
          +-----------> Redis / RQ queue
                            |
                            v
                    evaluation worker
                    section parsing
                    claim extraction
                    MiniLM retrieval
                    deterministic checks + NLI
                            |
                            v
                         database
                            |
                            v
                    client status polling
```

An evaluation submission is persisted as `QUEUED`, enqueued, and acknowledged
with HTTP `202` and an evaluation ID. The worker claims the job, records an
attempt, executes the pipeline, and saves normalized claim/evidence records and
the final state. The browser polls the status endpoint. Review-required results
enter a protected human-review workflow; reviewer decisions are stored without
overwriting the system verdict.

This is a modular monolith with an external worker, not a microservice system.
That choice keeps database work, shared data types, and deployment easier to understand
while separating CPU-heavy inference from latency-sensitive HTTP handling.

## 5. Data model

The current database shape is:

```text
papers 1 -------- N evaluations
                       |
                       |-- 1 -------- N claims
                       |                  |-- 1 -------- N evidence_passages
                       |                  `-- 1 -------- 0..N model_predictions
                       |
                       |-- 1 -------- 0..1 review_tasks
                       |                  `-- 1 -------- 0..1 review_decisions
                       `-- attempt_count and latest failure on evaluation

users 1 -------- 0..N review_decisions

benchmark_runs 1 -------- N benchmark_results
```

A paper may be reused by many evaluations. Each evaluation has one or more
claims after successful processing. Claims may have evidence and an NLI
prediction. Only a `REVIEW` result creates one review task. One task can have
only one saved review decision. A benchmark run holds many example results.

The database does not have a separate `evaluation_attempts` table. It stores an
attempt count and the latest failure message on the evaluation. This is simple,
but it does not keep a full error record for every attempt.

## 6. Rules that must always stay true

These are the main laws of AnswerTrust. Before changing the system, ask which
of these rules the change could affect.

| ID | Rule | How it is protected today |
| --- | --- | --- |
| `INV-01` | Evidence comes only from the supplied paper. | Retrieval receives only parsed text from that paper. |
| `INV-02` | Each saved claim keeps its label, explanation, flags, and evidence. | Domain result types and separate database rows. |
| `INV-03` | Human review never replaces the original system decision. | `final_decision` and review records are separate. |
| `INV-04` | An NLI-only contradiction cannot cause automatic rejection. | NLI adds `NLI_ONLY_CONTRADICTION`; the decision engine sends it to review. |
| `INV-05` | Low-confidence NLI does not change the rule result. | The NLI confidence gate defaults to `0.65`. |
| `INV-06` | Repeating a completed job must not add duplicate claim results. | Stable evaluation ID, terminal-state check, and replace-on-save logic. |
| `INV-07` | Failed work must not look complete. | Separate lifecycle state, failure message, and transaction rollback. |
| `INV-08` | Real-paper benchmark cases must carry source and label details. | Dataset schema validation. |
| `INV-09` | Logs must not contain paper text, answer text, passwords, tokens, or reviewer notes. | The JSON logger uses a small allowed field list. |
| `INV-10` | Size, rate, and queue limits apply before ML work starts. | API middleware, Pydantic limits, and queue admission check. |
| `INV-11` | Only an open review task for a `REVIEW_REQUIRED` evaluation can be resolved. | Repository state and task checks. |
| `INV-12` | A failed database transaction must not leave a half-saved final result. | Session rollback and one worker transaction. |

## 7. What happens during an evaluation

### Submission and worker sequence

```text
React                         FastAPI and database
  |                                   |
  | POST /api/v1/evaluations          |
  |---------------------------------->|
  |                                   | check body size and rate
  |                                   | validate fields
  |                                   | save paper + QUEUED evaluation
  |                                   | commit
  |                                   | check queue size and enqueue
  |<----------------------------------| 202 + evaluation_id
  |                                   |
  | poll GET /evaluations/{id}        |
  |---------------------------------->|

Redis/RQ                    Worker and database
  |                                   |
  | deliver evaluation ID             |
  |---------------------------------->|
  |                                   | mark attempt PROCESSING/RETRYING
  |                                   | load paper, question, and answer
  |                                   | run evaluation pipeline
  |                                   | save result in one transaction
  |                                   | raise errors so RQ can retry
```

Submission is public in the current API. Authentication is required for review
work and for administrator-only actions. The queue step happens after the
`QUEUED` record is committed. If queueing fails or the queue is full, that
evaluation is changed to `FAILED` and the client receives `503`.

### Decision pipeline

```text
AI answer
   |
   v
split into claims
   |
   v
semantic matching (when supplied) + lexical matching + section priority
   |
   v
candidate evidence from the supplied paper
   |
   v
fixed checks: numbers, negation, causal wording, scope, qualification
   |
   v
optional NLI prediction -> confidence gate
   |
   v
hybrid claim label
   |
   v
SUPPORTED / PARTIALLY_SUPPORTED / UNSUPPORTED /
CONTRADICTED / INSUFFICIENT_EVIDENCE
   |
   v
fixed decision engine
   |
   v
PUBLISH / REVIEW / REJECT
```

The default `evaluate_answer()` call does not create the embedding or NLI model
by itself. It uses them only when callers pass a `SemanticMatcher` or
`NLIClassifier`. Without them, the academic rule and lexical paths still work.
This is an important current limitation: the code supports the ML models, but
the default worker does not wire them in.

### Why did this result happen?

Example 1: wording that is too strong.

```text
Paper:     "Treatment was associated with lower symptom scores."
Answer:    "The treatment caused symptom reduction."
Claim:     The treatment caused symptom reduction.
Evidence:  The association statement from the paper.
Rule flag: Correlation was changed into causation.
Result:    Not fully supported.
Decision:  REVIEW, because a person should check the stronger wording.
```

Example 2: a confirmed contradiction.

```text
Paper:     "The difference was not statistically significant."
Answer:    "The treatment produced a significant improvement."
Claim:     The treatment produced a significant improvement.
Evidence:  The paper's non-significant result.
Rule flag: The claim reverses the reported significance.
Result:    CONTRADICTED.
Decision:  REJECT, because a fixed check confirms the contradiction.
```

These examples show decision paths, not promised output text for every input.

## 8. Async states, retries, and concurrent work

### State machine

```text
QUEUED
  |
  | first worker attempt
  v
PROCESSING ---------------------> COMPLETED (system PUBLISH)
  |                              REVIEW_REQUIRED (system REVIEW)
  |                              REJECTED (system REJECT)
  |
  | attempt fails before limit
  v
RETRYING ---- next attempt ----> RETRYING or a result state
  |
  | third attempt fails
  v
FAILED

REVIEW_REQUIRED -- reviewer approves --> APPROVED
REVIEW_REQUIRED -- reviewer rejects  --> REJECTED
```

| Current state | Event | Current result |
| --- | --- | --- |
| `QUEUED` | First worker attempt starts | `PROCESSING`, attempt count becomes 1. |
| `PROCESSING` or `RETRYING` | Evaluation succeeds | `COMPLETED`, `REVIEW_REQUIRED`, or `REJECTED`. |
| Any non-final worker state | Another attempt starts | `RETRYING`, attempt count increases. |
| Attempt fails before the third try | Worker records failure | `RETRYING`; RQ receives the raised error. |
| Third attempt fails | Worker records final failure | `FAILED`. |
| Any completed/result state | Duplicate job starts | Worker returns without running inference again. |
| `REVIEW_REQUIRED` with open task | Reviewer decides | `APPROVED` or `REJECTED`; review task becomes resolved. |
| Any other state | Reviewer decides | Repository rejects the operation. The API does not yet map this `ValueError` to a clean `409`, so this is a known error-handling gap. |

### At-least-once work and safe repeats

RQ may deliver the same job more than once. This is called **at-least-once
delivery**. A repeated job should have the same safe effect; this is called
**idempotent work**.

AnswerTrust uses the evaluation ID as both the database key and RQ job ID. A
worker checks the saved state before inference. If the evaluation is already in
`COMPLETED`, `REVIEW_REQUIRED`, `APPROVED`, or `REJECTED`, it exits. If a result
is saved again, old claim, evidence, and prediction rows are replaced instead
of appended.

This protects normal retries, but it is not a full distributed lock. Two workers
that begin the same non-final evaluation at almost the same time can both run
inference. Database uniqueness rules and transactions reduce bad writes, but
the current code does not use a row lock or compare-and-set claim step. Atomic
worker claiming is a future hardening task.

### Review races

- The first valid review changes the evaluation state and resolves its task.
- A second review fails the repository state/task checks. The existing review
  and system result remain unchanged.
- Review cannot succeed before `REVIEW_REQUIRED`, because no open task exists.
- Two reviewers submitting at the same time rely on database uniqueness and
  transaction behavior. The code does not lock the review task first, so one
  request may fail with a database error instead of a friendly conflict.

### Transaction boundaries

Creating an evaluation and submitting it to Redis are not one shared
transaction. The API first commits the paper and `QUEUED` evaluation, then
enqueues it. Queue failure is handled by a second commit that marks it `FAILED`.

One worker session covers attempt start, evaluation, claim/evidence/prediction
writes, metrics, final decision, and final state. A successful session commits
all of these changes. An unexpected database error rolls back the session, so a
partly written final result is not committed. Worker error handling saves the
failure state before raising the error to RQ.

One API session covers review checks, review decision, reviewer ID and notes,
task resolution, and evaluation state. These changes commit together. On an
error, they roll back together.

## 9. Repository units

### 9.1 Application and domain core: `src/`

The Python application uses FastAPI and Pydantic at the HTTP boundary,
SQLAlchemy's repository pattern at the persistence boundary, protocols for ML
substitution, and dataclasses/enums for domain values.

| File | Responsibility |
| --- | --- |
| `src/__init__.py` | Marks `src` as a Python package. |
| `src/api.py` | FastAPI application, CORS, schemas, error envelopes, dependency injection, versioned evaluation/review/benchmark/analytics/auth endpoints. |
| `src/api_client.py` | Python client that submits and polls evaluations, lists reviews, and converts API JSON back into domain objects. |
| `src/config.py` | Central paths, Redis URL, model-cache setup, benchmark paths, and environment-driven resource limits. |
| `src/models.py` | Domain enums and dataclasses for inputs, evidence, claims, dimensions, results, decisions, states, and failure types. |
| `src/academic.py` | Academic-section parsing, sentence and claim splitting, lexical evidence matching, numerical/negation rules, claim checks, and section statistics. |
| `src/semantic.py` | Encoder protocol, cosine similarity, and MiniLM-backed semantic matching. |
| `src/retrieval.py` | `EvidenceRetriever` protocol and hybrid academic retriever combining embeddings, section priors, and lexical fallback. |
| `src/nli.py` | Local natural-language-inference classifier, confidence calculation, and guarded application of entailment/contradiction signals. |
| `src/classification.py` | `ClaimClassifier` protocol and hybrid classifier combining academic rules with NLI. |
| `src/decision_engine.py` | Deterministic aggregation from claim results and dimension scores to `PUBLISH`, `REVIEW`, or `REJECT`. |
| `src/pipeline.py` | Connects retrieval and classification interfaces into the claim-processing pipeline. |
| `src/evaluator.py` | Top-level orchestration, scoring, explanations, recommendations, and latency measurement. |
| `src/db.py` | Database URL normalization, engine/session factories, and transaction-scoped session context manager. |
| `src/db_models.py` | SQLAlchemy mappings and database constraints for users, papers, evaluations, reviews, claims, evidence, predictions, and benchmarks. |
| `src/evaluation_repository.py` | Transactional persistence and reconstruction of evaluation lifecycle, results, claims, evidence, and review tasks. |
| `src/benchmark_repository.py` | Persistence for benchmark runs and per-example results. |
| `src/analytics_repository.py` | SQL-backed aggregate evaluation, latency, review, decision, and benchmark trends. |
| `src/benchmark_service.py` | Runs the publication benchmark and records completion or failure atomically through the repository. |
| `src/job_queue.py` | Redis connectivity, RQ submission, bounded retries/timeouts, unique job IDs, and queue-depth saturation guard. |
| `src/worker.py` | Worker entry point; records attempts, executes evaluation, persists outcomes, and rethrows failures for RQ retry behavior. |
| `src/resource_limits.py` | Early request-body enforcement and thread-safe process-local sliding-window throttling. |
| `src/auth.py` | Password hashing/verification, signed expiring bearer tokens, user creation, and role dependencies. |
| `src/observability.py` | Structured JSON logging, request IDs, latency measurement, and non-sensitive in-process counters. |
| `src/example_data.py` | Loads and validates benchmark schema, provenance, licensing, difficulty, and annotation metadata. |
| `src/experiments.py` | Publication, retrieval, and NLI benchmark runners; threshold sweeps; metrics; de-identified disagreement exports. |
| `src/reviewer_agreement.py` | Blind review-sheet export, Wilson intervals, Cohen's kappa, validation, and agreement reports. |
| `src/legacy_migration.py` | Idempotent conversion from the original SQLite schema into the current repository model. |
| `src/database.py` | Legacy SQLite persistence retained solely as the source-format compatibility layer for old data/workflows. |

**Architecture and computer-science principles.** The application has clear
boundaries between major parts. Python protocols let tests or new code replace
retrieval and classification. Repositories keep database code out of the main
evaluation logic. FastAPI dependencies let tests replace the queue and database.
The worker allows repeated delivery, but uses stable evaluation IDs, limited
retries, and clear states to keep repeats safe. Semantic retrieval and NLI can
find more meaning, while fixed rules and confidence checks limit unsafe model
changes.

**Why this design.** A single codebase lets API and worker share domain types and
evaluation logic. Separating the worker prevents model loading and inference
from blocking web requests. Normalized result tables make claims and evidence
queryable, while JSON remains useful for flexible dimension data. SQLite keeps
local setup easy; PostgreSQL supports the production-style stack.

**Advantages.** Explainability, replaceable ML components, deterministic tests,
auditable review history, transactional writes, graceful lexical fallback, and
clear asynchronous states.

**Drawbacks.** `api.py` contains many schemas and routes and will become a
maintenance hotspot if the API grows. In-process metrics and rate limits are not
shared across API replicas. The legacy `database.py` creates two persistence
styles to understand. RQ/Redis provides practical jobs but not strict global
queue admission under concurrent producers. Model downloads and CPU inference
remain operationally expensive.

**Striking feature.** The domain core never asks a model for an ungrounded final
verdict: it exposes evidence per claim and lets deterministic policy decide how
uncertainty and contradictions affect publication.

### 9.2 Frontend: `frontend/`

The primary interface uses React 19, TypeScript, React Router, and Vite. It is a
thin client: domain decisions remain on the server, and the UI concentrates on
workflow, status, evidence, and error presentation.

| File or group | Responsibility |
| --- | --- |
| `frontend/src/main.tsx` | Browser entry point and React root mounting. |
| `frontend/src/App.tsx` | Layout and routed login, evaluation, result polling, review, benchmark, and analytics pages. |
| `frontend/src/api.ts` | Typed fetch wrapper, bearer-token attachment, error propagation, and endpoint functions. |
| `frontend/src/types.ts` | TypeScript contracts mirroring public API inputs, states, results, reviews, benchmarks, and analytics. |
| `frontend/src/index.css` | Global reset, typography, colors, and shared primitives. |
| `frontend/src/App.css` | Application shell and evaluation/result presentation. |
| `frontend/src/Review.css` | Review-queue and decision form styling. |
| `frontend/src/Benchmark.css` | Benchmark table, metrics, and error-detail styling. |
| `frontend/src/Analytics.css` | Analytics cards and trend presentation. |
| `frontend/e2e/fixtures.ts` | Stable API fixtures shared by browser tests. |
| `frontend/e2e/evaluation.spec.ts` | Submission, polling, evidence, loading, and failure paths. |
| `frontend/e2e/review.spec.ts` | Protected reviewer workflow and resolution behavior. |
| `frontend/e2e/auth.spec.ts` | Login and authorization-facing behavior. |
| `frontend/e2e/benchmark.spec.ts` | Benchmark runs, metrics, and result inspection. |
| `frontend/e2e/analytics.spec.ts` | Persistent dashboard rendering. |
| `frontend/index.html` | Vite HTML shell. |
| `frontend/public/favicon.svg` | Product favicon. |
| `frontend/package.json` / `package-lock.json` | Reproducible dependencies and dev/build/lint/browser-test commands. |
| `frontend/tsconfig*.json` | Strict TypeScript project/build configuration. |
| `frontend/vite.config.ts` | React plugin and Vite build configuration. |
| `frontend/playwright.config.ts` | Isolated Chromium E2E server, tracing, and parallel test settings. |
| `frontend/.oxlintrc.json` | Frontend lint rules. |
| `frontend/nginx.conf` | Static hosting, SPA routing, and container health path. |
| `frontend/Dockerfile` | Multi-stage Node build followed by small nginx runtime image. |

**Principles and design choice.** The frontend follows a server-authoritative,
typed API architecture. Polling was selected before server-sent events because
it is easy to observe, retry, proxy, and test. Route-level pages share one small
API adapter rather than duplicating fetch behavior.

**Advantages.** Small dependency surface, compile-time contracts, fast builds,
direct visibility of queued/failed states, and browser tests that mock stable API
boundaries.

**Drawbacks.** `App.tsx` currently concentrates all page components; component
and state extraction would help future growth. API types are manually mirrored
rather than generated from OpenAPI. Polling adds repeated requests and eventual
latency. Authentication is stored client-side and is intentionally basic.

**Striking feature.** The UI exposes the entire safety trail—claim, label,
passage, section, confidence, and reviewer outcome—rather than hiding the system
behind a score.

### 9.3 Database migrations: `migrations/`

Alembic is the only supported mechanism for changing the current database
schema. Migrations are ordered, reversible where practical, and written to work
with both SQLite batch operations and PostgreSQL.

| File | Schema change |
| --- | --- |
| `migrations/env.py` | Loads SQLAlchemy metadata and runs online/offline migrations against `DATABASE_URL`. |
| `migrations/script.py.mako` | Template for new revision files. |
| `0001_create_evaluations_and_reviews.py` | Creates evaluations, lifecycle/score constraints, indexes, and reviewer decisions. |
| `0002_add_papers.py` | Adds deduplicated papers and evaluation foreign keys. |
| `0003_move_paper_text.py` | Hashes and migrates inline paper text into the paper table. |
| `0004_add_claims_and_evidence.py` | Adds normalized ordered claim and evidence tables. |
| `0005_move_claim_json.py` | Migrates embedded claim JSON into normalized rows. |
| `0006_add_model_predictions.py` | Separates model predictions and removes prediction fields from claims. |
| `0007_add_review_tasks.py` | Adds explicit review-task lifecycle and migrates existing review work. |
| `0008_add_benchmarks.py` | Adds benchmark run and result history. |
| `0009_add_users_and_reviewers.py` | Adds users/roles and reviewer attribution. |
| `0010_add_async_evaluation_state.py` | Adds attempt counts and failure messages for worker retries. |

**Principles and design choice.** The database changed in small, safe steps:
move one kind of data into its own table, copy old values, then remove old columns.
Content hashes deduplicate papers without requiring users to manage paper IDs.
Foreign keys, uniqueness, checks, indexes, and transactions enforce invariants
below the application layer.

**Advantages.** Reproducible upgrades, an inspectable data history, rollback
definitions, and compatibility with local and production databases.

**Drawbacks.** Supporting SQLite and PostgreSQL increases migration complexity;
some downgrades can only approximately reconstruct older shapes. The historical
table name `evaluations_v2` remains visible.

**Striking feature.** The migration chain demonstrates safe normalization of a
working JSON-heavy prototype without discarding its evaluations or audit data.

### 9.4 Data and benchmark assets: `data/`

| File | Responsibility |
| --- | --- |
| `evaluation_examples.json` | 150 publication-safety cases: 50 synthetic and 100 provenance-labelled real-paper cases. |
| `evaluation_examples.manifest.json` | Dataset-level schema and composition metadata. |
| `evaluation_sources.json` | Deduplicated paper provenance, stable locators, and reuse information. |
| `semantic_examples.json` | Ten paraphrase-oriented retrieval regression cases. |
| `nli_examples.json` | Thirty balanced entailment, contradiction, and neutral cases. |

**Principles and design choice.** Test data carries provenance, licensing,
difficulty, rationale, annotation status, and reviewer confidence so synthetic
examples cannot be mistaken for independent evidence. Dataset validation fails
early when required metadata is absent.

**Advantages.** Reproducible measurements, traceable sources, explicit label
rationale, and targeted difficult categories.

**Drawbacks.** The datasets remain small and partly project-authored. They do not
estimate general performance, clinical safety, or behavior across disciplines.

**Striking feature.** Benchmark provenance is treated as an application
invariant, not informal documentation.

### 9.5 Scripts and experiment entry points

| File | Responsibility |
| --- | --- |
| `scripts/create_user.py` | Secure terminal command for creating reviewer/admin accounts without echoing passwords. |
| `scripts/migrate_legacy_sqlite.py` | CLI wrapper for idempotent legacy import. |
| `scripts/__init__.py` | Makes scripts executable as Python modules. |
| `setup_ml.ps1` | Windows setup for the local ML environment and repository model cache. |
| `src/experiments.py` | CLI-accessible benchmark and comparison routines. |
| `src/reviewer_agreement.py` | CLI-accessible independent-review export and reporting. |

These scripts favor repeatability and explicit parameters over ad hoc database
editing. Their advantage is a safe operational path for common maintenance;
their drawback is that they assume shell access and are not administrative UI
features. The striking detail is that legacy import is idempotent by evaluation
ID, making reruns safe.

### 9.6 Tests: `tests/` and `frontend/e2e/`

| File | Coverage |
| --- | --- |
| `tests/test_answertrust.py` | Academic parsing, deterministic safety rules, retrieval interfaces/fallback, semantic ranking, NLI gates/metrics, benchmark validation, de-identification, and reviewer agreement. |
| `tests/test_api.py` | HTTP schemas/errors, auth/RBAC, CORS, health/readiness/metrics, async submission/status, limits/throttling/saturation, reviews, analytics, benchmarks, and Python client behavior. |
| `tests/test_db_models.py` | Transactions, rollback, lifecycle/retries, repositories, paper reuse, normalized predictions, review audit, benchmarks, and legacy import. |
| `tests/test_migrations.py` | Alembic revision-chain presence and paper migration. |
| `tests/test_postgres_integration.py` | Optional real-PostgreSQL connection and migrated-table verification. |
| `pytest.ini` | Test discovery and the optional `postgres` marker. |
| `frontend/e2e/*.spec.ts` | Browser-level evaluation, authentication, review, benchmark, and analytics workflows. |

**Principles and design choice.** The suite uses a test pyramid: fast domain
tests, in-memory API/database integration, an opt-in real PostgreSQL check, and
browser tests at user-visible seams. Fake encoders/models and dependency
overrides make probabilistic and infrastructure behavior deterministic.

**Advantages.** High behavioral coverage without requiring Redis, PostgreSQL,
or model downloads for the default backend suite; explicit regression cases for
past safety failures.

**Drawbacks.** The default API test queue is synchronous, so full Redis/RQ worker
behavior is not exercised in every run. PostgreSQL is opt-in. Browser tests mock
the API and therefore complement rather than replace a full-stack smoke test.

**Striking feature.** Tests cover abstention, fallback, audit preservation, and
resource exhaustion—not only successful model predictions.

### 9.7 Containers and runtime configuration

| File | Responsibility |
| --- | --- |
| `compose.yaml` | Production-style local topology: PostgreSQL, persistent Redis, API, worker, frontend, health checks, dependencies, and volumes. |
| `Dockerfile` | Shared Python 3.11 CPU image for API and worker, including ML runtime and migrations. |
| `frontend/Dockerfile` | Reproducible frontend build and nginx runtime. |
| `.dockerignore` | Excludes local/generated content from container build context. |
| `.env.example` | Documents secrets and resource-boundary configuration. |
| `requirements.txt` | Pinned Python runtime/test dependencies. |
| `alembic.ini` | Alembic logging and migration location. |
| `.gitignore` / `frontend/.gitignore` | Excludes secrets, caches, databases, results, dependencies, and builds. |

Docker Compose selects one container per operational responsibility but retains
a shared application image. Health-conditioned startup prevents the API and
worker from racing unavailable dependencies. Named volumes preserve database,
queue, and model-cache data.

The advantage is a close-to-production topology from one command. Drawbacks are
large ML image builds, local default secrets that must be replaced, lack of TLS
or backup automation, and no deployed infrastructure definition. The striking
feature is that API and worker share code but have distinct processes and model
loading behavior.

### 9.8 CI and release automation

There is currently **no checked-in `.github/workflows` or equivalent CI
pipeline**. Backend tests, frontend lint/build, Playwright, and container builds
are available as local commands, but the repository does not presently enforce
them on commits or pull requests.

This is the clearest gap between the earlier project plan and the implemented
repository. A future CI unit should run Python tests, frontend lint/build,
browser tests, migration checks, and image builds, with the PostgreSQL suite on
a service container. Its advantage would be repeatable merge gates; its cost is
runtime, browser/image caching complexity, and maintenance. CI must not be
claimed as implemented until its workflow files exist and pass.

### 9.9 Documentation and legal material

| File | Responsibility |
| --- | --- |
| `README.md` | Concise product overview, key aspects, verified metrics, setup, operations, and link to this reference. |
| `PROJECT_REFERENCE.md` | Authoritative product, architecture, file, decision, advantage/drawback, and roadmap reference. |
| `THIRD_PARTY_NOTICES.md` | Required attribution for third-party content; retained separately because legal notices should not be rewritten into general documentation. |
| `LICENSE` | Repository license. |

The former project plan, standalone database guide, and frontend README were
absorbed here because they repeated or contradicted the root README. Two clear
documentation levels reduce drift: README for adoption and this file for
understanding and maintenance.

### 9.10 Generated and local-only directories

`frontend/node_modules/`, `frontend/dist/`, `.venv/`, `.pytest_cache/`,
`__pycache__/`, `model_cache/`, `results/`, and local database files are runtime
or generated artifacts, not maintained project units. They should not be used
as documentation sources or committed. `results/` contains reproducible
benchmark outputs; `model_cache/` prevents repeated external model downloads.

## 10. API and resource boundaries

The API is versioned under `/api/v1`. Its main endpoint groups are health and
readiness, authentication, evaluation submission/status/listing, protected
reviews, benchmarks, administrator metrics, and administrator analytics.
FastAPI publishes the exact OpenAPI schema at `/docs` and `/openapi.json`.

OpenAPI is the exact field contract. This table is a quick map of intent:

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/v1/health` | Public | Check that the API process is running. |
| `GET` | `/api/v1/readiness` | Public | Check that the database can be reached. |
| `POST` | `/api/v1/auth/login` | Public | Exchange email/password for an eight-hour bearer token. |
| `POST` | `/api/v1/evaluations` | Public | Submit an evaluation and receive an ID. |
| `GET` | `/api/v1/evaluations/{evaluation_id}` | Public | Read current state or the final result. |
| `GET` | `/api/v1/evaluations` | Public | List a page of completed evaluations. |
| `GET` | `/api/v1/reviews/pending` | Reviewer or admin | List open review work. |
| `POST` | `/api/v1/evaluations/{evaluation_id}/review` | Reviewer or admin | Resolve a review item. |
| `POST` | `/api/v1/benchmarks/publication` | Admin | Run and save the publication benchmark. |
| `GET` | `/api/v1/benchmarks` | Public | List saved benchmark runs. |
| `GET` | `/api/v1/benchmarks/{run_id}` | Public | Read one run and its example results. |
| `GET` | `/api/v1/metrics` | Admin | Read process-local counters. |
| `GET` | `/api/v1/analytics` | Admin | Read saved system and benchmark trends. |

Evaluation submissions currently enforce these environment-configurable
defaults:

| Boundary | Default | Failure behavior |
| --- | ---: | --- |
| Request body | 1,048,576 bytes | HTTP 413, `REQUEST_TOO_LARGE` |
| Question | 2,000 characters | HTTP 422, `VALIDATION_ERROR` |
| Paper text | 500,000 characters | HTTP 422, `VALIDATION_ERROR` |
| Answer | 20,000 characters | HTTP 422, `VALIDATION_ERROR` |
| Submission rate | 30/client/60 seconds | HTTP 429, `RATE_LIMITED`, `Retry-After` |
| Queue backlog | 100 jobs | HTTP 503, `SERVICE_UNAVAILABLE`, `Retry-After` |

Malformed JSON and missing/invalid fields use the same non-sensitive JSON error
envelope. Queue connectivity failure also returns 503 and records the accepted
evaluation as failed. These controls prevent one request or burst from claiming
unbounded memory, inference time, or backlog.

The throttler is intentionally small and process-local. It is appropriate for a
single API process and tests, but multiple replicas require shared Redis/gateway
limiting. Queue depth is a practical backpressure signal, not an atomic global
admission guarantee when many producers enqueue simultaneously.

### HTTP status guide

| HTTP status | Meaning in AnswerTrust |
| ---: | --- |
| `200` | Request completed. |
| `202` | Evaluation was saved and accepted for queue work. |
| `400` | Malformed request metadata, such as an invalid `Content-Length`. |
| `401` | Sign-in token is missing, invalid, or expired. |
| `403` | The user is signed in but lacks the needed role. |
| `404` | The requested evaluation or benchmark does not exist. |
| `413` | The HTTP body is too large. |
| `422` | JSON or field validation failed. |
| `429` | The submission rate limit was reached. Check `Retry-After`. |
| `503` | Redis, the queue, or another needed service is unavailable. |
| `500` | An unexpected server error occurred. Invalid review-state errors can currently reach this response. |

`409 Conflict` is not returned today. It is the planned response when a valid
request conflicts with the current workflow state.

### Failure guide

| Failure | Client sees | Saved state | Recovery |
| --- | --- | --- | --- |
| Body larger than 1 MiB | `413` | No evaluation. | Send a smaller request. |
| Paper or answer exceeds its field limit | `422` | No evaluation. | Shorten the field. |
| Malformed JSON or missing field | `422` | No evaluation. | Fix the request. |
| Rate limit reached | `429` and `Retry-After` | No evaluation. | Wait and retry. |
| Queue is full | `503` and `Retry-After` | Evaluation is saved, then marked `FAILED`. | Wait and submit a new evaluation. |
| Redis cannot be reached | `503` | Evaluation is saved, then marked `FAILED`. | Restore Redis and submit again. |
| Worker evaluation error | Polling shows `RETRYING` or `FAILED`. | Attempt count and latest message are saved. | RQ retries up to the limit. |
| NLI call fails | No direct error. | Rule result continues. | Repair the model before relying on NLI. |
| NLI confidence is below `0.65` | No direct error. | NLI does not replace the rule result. | No action required. |
| Result save fails | Worker fails and can retry. | Transaction rolls back. | Fix the database and retry. |
| Review uses the wrong state | Currently an unexpected server error. | Review transaction rolls back. | Refresh; map this case to `409` in a future change. |

## 11. Persistence, security, and observability

Paper text is content-hashed and deduplicated. Claims, evidence passages, model
predictions, review tasks, reviewer decisions, and benchmark results have
separate records. Database constraints protect ranges, valid states, ordering,
and uniqueness; repository transaction boundaries commit complete operations or
roll them back.

Passwords use salted PBKDF2 hashes. Signed bearer tokens expire after eight
hours. Roles are `REVIEWER` and `ADMIN`; reviews accept either role, while
metrics, analytics, and benchmark execution require administrators. Production
must set a strong `ANSWERTRUST_AUTH_SECRET` and terminate TLS outside the app.

Every HTTP response receives a request ID. Structured JSON logs include method,
path, status, duration, evaluation ID, and outcome where useful, while excluding
paper text, answers, passwords, and reviewer notes. `/health` tests process
liveness; `/readiness` tests the database. Metrics are non-sensitive process
counters and therefore reset on restart and do not aggregate across replicas.

### Threat model

| What must be protected | Main risks | Current controls |
| --- | --- | --- |
| Passwords and tokens | Theft, weak secrets, role bypass | Salted PBKDF2 passwords, signed expiring tokens, role checks. |
| Paper and answer text | Log leaks, unwanted access, oversized-input attacks | Small log field list, body/field limits, no paper text in logs. |
| Reviewer identity and notes | Access by the wrong user, log leaks | Protected review endpoints, foreign keys, notes excluded from logs. |
| Database and Redis credentials | Secret exposure | Environment variables and ignored `.env` files. |
| Evaluation capacity | Request floods, repeated inference, full queue | Rate limit, size limits, queue-depth limit, worker timeout/retries. |
| Benchmark data | Bad source claims or changed labels | Required provenance and schema checks. |

Known security limits are important. Public evaluation and result endpoints can
expose submitted content to anyone who knows or obtains an evaluation ID. Tokens
are stored in browser local storage and cannot be revoked. There is no account
recovery, SSO, audit log for sign-in, TLS inside the app, malware scanning, or
paper retention/deletion policy. The process-local rate limit is not enough for
many API replicas. A public deployment must add TLS, stronger secret handling,
shared limits, access policy for evaluations, backups, and a retention policy.

### Log and diagnosis policy

When a user reports a problem, start with the HTTP `X-Request-ID` and the
evaluation ID. The API log can show whether submission succeeded. Worker logs
then show the attempt and outcome. The database holds the current state, latest
failure, result, and review record.

| Safe to log | Never log |
| --- | --- |
| Request ID | Password or password hash |
| Evaluation ID | Bearer token or signing secret |
| HTTP method and route path | Full paper text |
| Status and lifecycle state | AI answer text |
| Duration and attempt number | Reviewer notes |
| Error class or short safe message | Database or Redis password |
| Model name/version when available | Raw private request bodies |

The current logger does not yet emit retrieval time, NLI time, queue depth, or
actual model version. Those are useful future fields if they remain free of user
content.

## 12. Model setup and version tracking

| Part | Current value |
| --- | --- |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| NLI model | `cross-encoder/nli-MiniLM2-L6-H768` |
| NLI confidence gate | `0.65` |
| Cache location | Repository `model_cache/` through `HF_HOME` |
| Download behavior | Disabled by default in model classes; setup can download files first. |
| Device | Chosen by the sentence-transformers/PyTorch runtime; not fixed in AnswerTrust config. |
| Model failure | NLI falls back to rule output; retrieval can use lexical matching when no semantic matcher is supplied. |

Model repository names are in code, but exact model revisions are not pinned.
Saved model predictions use the general name `nli-classifier`, not the real
model name or revision. Benchmark runs do not save the model revision, threshold,
rule-policy version, or code commit. This makes an old benchmark harder to
reproduce exactly after model or policy changes.

The next versioning improvement should save a model configuration with each
evaluation and benchmark: embedding model and revision, NLI model and revision,
confidence threshold, device, rule-policy version, and source commit. Until that
exists, benchmark notes must state the configuration used.

## 13. Test proof and benchmark meaning

### Test traceability

| Important promise | Domain tests | API tests | DB tests | PostgreSQL test | Browser tests |
| --- | :---: | :---: | :---: | :---: | :---: |
| Section and claim extraction | Yes |  |  |  |  |
| NLI confidence gate | Yes |  |  |  |  |
| Lexical fallback | Yes |  |  |  |  |
| NLI-only contradiction goes to review | Yes |  |  |  |  |
| Async submission and status contract |  | Yes | Yes |  | Yes |
| Retry state and attempt count |  |  | Yes |  |  |
| Review preserves system decision |  | Yes | Yes |  | Yes |
| Reviewer/admin roles |  | Yes |  |  | Yes |
| Request and queue limits |  | Yes |  |  |  |
| Paper deduplication |  |  | Yes |  |  |
| Migration works on PostgreSQL |  |  |  | Yes, opt-in |  |
| Benchmark source validation | Yes | Yes | Yes |  | Yes |

The default API tests replace Redis/RQ with a synchronous test function. The
browser tests mock API replies. They prove public behavior, but they do not
prove that the complete container stack works together. That needs a separate
full-stack smoke test.

### Software tests versus ML benchmarks

Software tests ask, “Does the program follow its rules?” Examples include
input rejection, state updates, safe rollback, role checks, and review audit
history. They should be stable and pass every time.

ML benchmarks ask, “How well does this model-and-rule setup perform on labelled
examples?” Examples include retrieval accuracy, contradiction detection, and
false-publish rate. Their results depend on the dataset, model, threshold, and
policy. Passing software tests does not prove high ML quality, and a good
benchmark score does not prove correct queue or database behavior.

## 14. Verified measurement baseline

The current publication dataset contains 150 cases: 50 synthetic and 100
Creative Commons real-paper excerpt cases with provenance. The last documented
mixed benchmark reported 82.67% decision accuracy, 100% unsupported-claim
detection, 66.67% contradiction detection, 0% false-publish rate, and 26.67%
review rate. The original 50-case synthetic baseline reported 100% decision
accuracy and 0% false-publish rate.

The semantic set reported 100% top-passage accuracy on 10 deliberately
paraphrased cases versus 0% for keyword overlap. The 30-pair NLI set reported
93.33% overall accuracy, 93.33% threshold coverage, 6.67% abstention, 0%
false-entailment, and 10% false-contradiction.

These are small regression benchmarks created and curated within the project.
They are useful for detecting changes, not for claiming broad scientific,
medical, or cross-domain validity. Metrics should be re-run before changing
these figures.

## 15. Running and operating the project

### Configuration reference

| Setting | Purpose | Default | Production note |
| --- | --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database connection | Local `data/answertrust-v2.db` | Use PostgreSQL for the production-style stack. |
| `REDIS_URL` | RQ queue connection | `redis://127.0.0.1:6379/0` | Required for async evaluation. |
| `ANSWERTRUST_AUTH_SECRET` | Signs bearer tokens | Unsafe local development value | Must be replaced with a long random secret. |
| `POSTGRES_PASSWORD` | Compose database password | Local Compose fallback | Must be replaced outside local work. |
| `MAX_REQUEST_BODY_BYTES` | Maximum evaluation HTTP body | `1048576` | Set at API start. |
| `MAX_QUESTION_LENGTH` | Maximum question characters | `2000` | Set at API start. |
| `MAX_PAPER_LENGTH` | Maximum paper characters | `500000` | Set at API start. |
| `MAX_ANSWER_LENGTH` | Maximum answer characters | `20000` | Set at API start. |
| `EVALUATION_RATE_LIMIT` | Requests allowed per client window | `30` | Process-local only. |
| `EVALUATION_RATE_WINDOW_SECONDS` | Rate-limit window | `60` | Use shared limiting for many replicas. |
| `MAX_QUEUED_EVALUATIONS` | Queue backlog allowed | `100` | Practical check, not an atomic global claim. |
| `VITE_API_URL` | Frontend API address | `http://127.0.0.1:8000/api/v1` | Baked into the frontend build. |

The RQ retry count (`2` retries after the first try), retry waits (`2` and `5`
seconds), job timeout (`10m`), result lifetime (`3600` seconds), token lifetime
(`8` hours), and NLI gate (`0.65`) are hard-coded today. They are configuration
values in practice but are not environment settings yet.

### Runtime layouts

Simple local work uses the React dev server, FastAPI, local SQLite, Redis, and a
worker process. The API and worker use the same Python source tree.

```text
React dev server -> FastAPI -> SQLite
                         |
                         v
                    Redis -> local worker
```

Docker Compose is the production-style local setup:

```text
Browser -> nginx frontend -> FastAPI container -> PostgreSQL
                                  |
                                  v
                                Redis -> worker container
```

A hosted production design is **not implemented**. TLS termination, managed
secrets, shared rate limits, backups, alerts, and deployment rollback still
need to be chosen for the target host.

### Local backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\setup_ml.ps1
python -m alembic upgrade head
python -m uvicorn src.api:app --reload
```

Start Redis and then the worker in another terminal:

```powershell
docker run --name answertrust-redis -p 6379:6379 redis:8
.\.venv\Scripts\rq.exe worker --url redis://127.0.0.1:6379/0 --worker-class rq.worker.SpawnWorker evaluations
```

### Database modes and legacy import

Without `DATABASE_URL`, the current SQLAlchemy application uses
`data/answertrust-v2.db`. For PostgreSQL, set a SQLAlchemy URL and apply the
migrations:

```powershell
$env:DATABASE_URL="postgresql://answertrust:password@localhost:5432/answertrust"
python -m alembic upgrade head
python -m alembic current
```

After backing up an old SQLite database, import it idempotently:

```powershell
python -m scripts.migrate_legacy_sqlite --source data/answertrust.db
```

### Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1
```

Set `VITE_API_URL` when the API is not at
`http://127.0.0.1:8000/api/v1`.

### Full stack

```powershell
docker compose up --build
```

Replace `POSTGRES_PASSWORD` and `ANSWERTRUST_AUTH_SECRET` outside local
development. Apply backup, TLS, monitoring, and rollback policies before any
public deployment.

### Verification commands

```powershell
python -m pytest -q
python -m pytest -m postgres -q
cd frontend
npm.cmd run lint
npm.cmd run build
npm.cmd run test:e2e
```

The PostgreSQL test requires `TEST_DATABASE_URL` pointing to a migrated test
database. Benchmark and reviewer-agreement commands remain documented in the
root README.

## 16. Main design decisions

These short decision records explain why the project is shaped this way.

| ID and decision | Why | Other option | Result and when to revisit |
| --- | --- | --- | --- |
| `ADR-001`: one-paper evidence boundary | Source faithfulness must be clear. | Search the web or many papers. | Easier evidence tracing; revisit only for a separate multi-source product. |
| `ADR-002`: async work through RQ | ML work is too slow for an HTTP request. | Run inference in the API. | Fast `202` replies and retry support; revisit if the queue no longer meets scale or delivery needs. |
| `ADR-003`: rules plus optional NLI | Rules are clear but miss paraphrases; NLI adds meaning but can be wrong. | Use only rules or only ML. | Better coverage with a safe fallback; revisit with larger independent results. |
| `ADR-004`: NLI-only contradiction means review | The NLI benchmark has false contradictions. | Let high-confidence NLI reject. | More human work but lower false-reject risk; revisit after strong independent calibration. |
| `ADR-005`: keep the system decision | Audit history must show what automation originally chose. | Replace it with reviewer outcome. | Clear comparison of human and system behavior; do not revisit without a new audit model. |
| `ADR-006`: normalized claim/evidence rows | Claims and passages need ordering, links, and queries. | Keep one large JSON result. | Better analysis and integrity at the cost of more tables. |
| `ADR-007`: lexical fallback | Models may be missing or fail. | Fail the whole evaluation. | The service can continue conservatively; revisit only if degraded results become unsafe. |
| `ADR-008`: polling before server events | Polling is simple to build, proxy, and test. | SSE or WebSockets. | More requests but less moving state; revisit when load or latency requires it. |
| `ADR-009`: modular monolith plus worker | The domain is one product and shares types. | Many microservices. | Easier transactions and deployment; split only around a proven scaling or ownership need. |
| `ADR-010`: SQLite locally, PostgreSQL in Compose | New contributors need easy setup while the full stack needs a stronger database. | Require PostgreSQL everywhere. | Two useful setup levels but more migration testing. |

## 17. Safe-change guide

### Change the NLI threshold

1. Change the threshold in `src/nli.py` or first move it into shared config.
2. Run the NLI threshold sweep.
3. Run the publication benchmark.
4. Compare false contradictions, false publishes, coverage, and review rate.
5. Read changed examples rather than accepting only the total score.
6. Add a regression case if a real bug caused the change.
7. Record the accepted configuration and update this reference.

### Add or change a claim label

Check `src/models.py`, academic and NLI classification, the decision engine,
database constraints/data, Alembic migration needs, API schemas, frontend types
and display, analytics, benchmark labels, tests, and this reference. Old saved
rows must remain readable or be migrated.

### Add an evaluation state

Update the domain/state list, database check constraint through a new migration,
repository transitions, worker behavior, API status response, frontend polling,
analytics queries, unit/API/database/browser tests, and state diagrams here.

### Change an API limit

Update `src/config.py`, `.env.example`, relevant middleware or Pydantic field,
API tests, the README summary, and the configuration/resource tables here.
Consider whether the frontend should show the same limit before submission.

### Change-impact matrix

| Change | Domain/rules | DB/migration | Worker | API | Frontend | Benchmarks | Tests/docs |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| NLI threshold | Yes | No | Uses it | Maybe | Maybe | Yes | Yes |
| Claim label | Yes | Maybe/Yes | Yes | Yes | Yes | Yes | Yes |
| Lifecycle state | Yes | Yes | Yes | Yes | Yes | Maybe | Yes |
| Evidence shape | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Reviewer role | Yes | Yes | No | Yes | Yes | No | Yes |
| Request limit | Config | No | No | Yes | Maybe | No | Yes |
| Model name/revision | Yes | Future config record | Yes | Maybe | No | Yes | Yes |

For every change, identify the affected invariants from section 6 before coding.
After coding, run the smallest focused tests first and then the full required
suite. Never change published benchmark numbers without rerunning the matching
benchmark and recording its model and policy setup.

## 18. Current advantages and limitations

### System-level advantages

- One bounded problem connects ML, backend, frontend, data, operations, and UX.
- Evidence and rule traces make decisions inspectable.
- Asynchronous inference keeps the API responsive.
- Human decisions are auditable and cannot silently rewrite system output.
- Confidence gates and lexical fallback degrade conservatively.
- SQLite and Docker Compose provide two useful setup levels.
- Provenance-aware benchmarks and disagreement exports support honest analysis.
- Resource limits now make overload behavior explicit and testable.

### System-level limitations

- Benchmark scale and independent annotation are insufficient for broad claims.
- The hybrid evaluator is sensitive to section parsing, converted tables, long
  context, and domain-specific language.
- The application does not verify source quality or compare outside evidence.
- Rate limits and operational counters are process-local.
- Full Redis/PostgreSQL/browser/container integration is not one default test.
- No CI workflow currently enforces repository checks.
- Authentication lacks account recovery, token revocation, SSO, and managed
  identity integration.
- Deployment, backups, TLS, alerting, and cost controls are not automated.

## 19. Strategic roadmap

### Near-term priorities

1. Add checked-in CI for backend tests, frontend lint/build, Playwright,
   migrations, and container builds.
2. Add a full-stack smoke test that uses PostgreSQL, Redis, API, worker, and
   frontend together.
3. Expand independently reviewed real-paper cases and report agreement,
   confidence intervals, category slices, and error analysis.
4. Split API routes/schemas and frontend pages only when growth makes the
   current cohesive files hard to maintain.
5. If horizontally deploying, replace process-local limiting/metrics with
   shared infrastructure and make queue admission atomic.
6. Document deployment configuration, secrets, backups, rollback, monitoring,
   and cost boundaries before a public release.

### Deferred until justified

Multi-paper synthesis, vector databases, hosted LLM dependencies, training a
large custom model, autonomous publication, premature microservices, and
Kubernetes are deliberate non-goals. Kubernetes should only be considered after
the Docker system has a concrete scaling or orchestration requirement.

## 20. Documentation maintenance rule

The README answers: what is this, why does it matter, what is implemented, and
how do I run it? This reference answers: how does every unit work, why was it
designed this way, and what are its tradeoffs? Legal attribution remains in
`THIRD_PARTY_NOTICES.md`. Avoid adding narrow Markdown files whose content fits
one of these two documents; link to the relevant heading instead.

## 21. Glossary

| Term | Meaning |
| --- | --- |
| Abstention | Choosing not to trust a model prediction because confidence is too low. |
| At-least-once delivery | A queue may give the same job to a worker more than once. |
| Benchmark provenance | Details that show where a test example came from, its licence, and how it was labelled. |
| Claim | One statement from an answer that can be checked by itself. |
| Confidence gate | A minimum score a model must reach before its prediction can change a result. |
| Contradiction | The paper says the opposite of the claim. |
| Deterministic rule | A fixed code rule that gives the same result for the same input. |
| Entailment | The evidence supports the claim's meaning. |
| Evaluation attempt | One worker try for an evaluation. |
| Evidence passage | Text from the supplied paper used to judge a claim. |
| False publish | An unsafe answer that the system wrongly marks `PUBLISH`. |
| Idempotent | Safe to repeat without creating extra or broken final data. |
| Lexical fallback | Word-based evidence matching used when semantic matching is absent or fails. |
| NLI | Natural-language inference: a model check for entailment, contradiction, or neither. |
| Queue admission | The decision to accept a new evaluation job into the queue. |
| Review decision | A human reviewer's `APPROVE` or `REJECT` choice. |
| Review rate | The share of evaluations sent to a person. |
| Repository | Code that reads and writes one kind of database data for the rest of the app. |
| Section priority | A small ranking boost based on where a passage appears in a paper. |
| Semantic matching | Matching by meaning with embeddings rather than only shared words. |
| System decision | The original automatic `PUBLISH`, `REVIEW`, or `REJECT` result. |
| Transaction | A group of database changes that all commit or all roll back. |
