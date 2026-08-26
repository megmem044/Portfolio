# AnswerTrust

**Last updated: August 25, 2026**

AnswerTrust is a paper-grounded AI evaluation system. It decomposes an
AI-generated answer into claims, retrieves relevant passages from a supplied
academic paper, checks whether each claim is supported or contradicted, and
routes the complete answer to `PUBLISH`, `REVIEW`, or `REJECT`.

It does not search the web or treat outside knowledge as evidence.

## Project pivot

AnswerTrust is evolving from a local Streamlit and SQLite prototype into a
production-style asynchronous web platform. The evaluator and its safety
behavior remain the core product; the new architecture is intended to show how
that ML subsystem can operate reliably inside a full software system.

The target stack is:

- React, TypeScript, and Vite for the primary frontend;
- FastAPI for a versioned REST API;
- PostgreSQL, SQLAlchemy, and Alembic for relational persistence;
- Redis and a separate worker for asynchronous evaluation;
- Docker Compose for reproducible local environments;
- pytest and Playwright for unit, integration, and browser testing;
- a future CI workflow for build and test automation;
- structured logging and operational metrics.

Most of this platform foundation is implemented. Continuous integration,
benchmark expansion, release preparation, and optional deployment remain. See
[the complete project reference](PROJECT_REFERENCE.md) for the verified
file map, design rationale, implementation tradeoffs, and roadmap.

## Current status

The repository currently contains the verified web MVP:

- a React evaluation interface, human-review queue, and benchmark dashboard;
- a versioned FastAPI service;
- SQLAlchemy persistence with SQLite for local use and PostgreSQL support;
- Alembic database migrations and a documented legacy-data importer;
- Redis-backed asynchronous evaluation with a separate RQ worker;
- persisted queued, processing, retrying, completed, and failed states;
- reviewer and administrator authentication with protected actions;
- structured logs, health checks, readiness checks, and persistent analytics;
- a Docker Compose stack for React, FastAPI, PostgreSQL, Redis, and the worker;
- local commands for backend, frontend, browser, and container verification;
- local MiniLM embeddings for paraphrase-aware evidence retrieval;
- academic section priors and keyword retrieval fallback;
- confidence-gated NLI with deterministic fallback;
- claim-level evidence, explanations, failure types, and confidence details;
- preserved system and reviewer decisions with timestamps;
- repository-local model caching and Windows setup scripts;
- pytest API and database tests plus Playwright browser tests;
- a de-identified export of system-versus-reviewer benchmark disagreements;
- a built-in overstatement demonstration and visible responsible-use guidance.

React is the primary interface. Evaluation requests return immediately while a
separate worker processes claims and the result page polls for status updates.

### Key aspects

- The supplied paper is the only evidence source; outside knowledge is never
  silently treated as proof.
- Every answer is decomposed into claims with section-labelled evidence and an
  inspectable explanation.
- MiniLM semantic retrieval and confidence-gated NLI are constrained by
  deterministic academic rules and conservative fallback behavior.
- Evaluation is asynchronous: the API persists and queues work, an RQ worker
  performs inference, and the client polls persisted state.
- Review-required cases enter an authenticated human workflow that preserves
  the original system decision as an audit record.
- SQLAlchemy repositories and Alembic migrations support easy local SQLite use
  and a production-style PostgreSQL topology.
- Structured logs, request IDs, health/readiness checks, metrics, analytics,
  benchmarks, and browser/backend tests make behavior observable and testable.
- Public resource boundaries cap body, question, paper, and answer size;
  throttle evaluation bursts; and reject saturated worker queues explicitly.
- Current benchmarks are regression sets, not evidence that the system can
  autonomously validate scientific or clinical truth.

## Current architecture

```text
paper + research question + AI answer
                |
                v
         paper section parsing
                |
                v
          claim extraction
                |
                v
   semantic evidence retrieval
   + academic section ranking
   + keyword fallback
                |
                v
 deterministic academic checks
   + confidence-gated NLI
                |
                v
 claim labels and cited evidence
                |
                v
    PUBLISH / REVIEW / REJECT
                |
                v
       human-review audit trail
```

## Target architecture

```text
React + TypeScript
        |
        | REST
        v
     FastAPI ----------> PostgreSQL
        |
        v
   Redis queue
        |
        v
evaluation worker ----> PostgreSQL
MiniLM | NLI | rules

Docker Compose | CI/CD | tests | logs | metrics
```

Evaluation requests return an ID immediately. The worker advances each
job through persisted states such as `QUEUED`, `PROCESSING`, `COMPLETED`,
`REVIEW_REQUIRED`, `APPROVED`, `REJECTED`, `FAILED`, and `RETRYING`.

## Evaluation behavior

AnswerTrust currently:

- parses common academic sections;
- extracts independently reviewable claims;
- labels claims as `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`,
  `CONTRADICTED`, or `INSUFFICIENT_EVIDENCE`;
- detects overstatement, missing qualifications, correlation presented as
  causation, unsupported claims, and population or scope extrapolation;
- routes NLI-only contradictions to human review;
- rejects contradictions confirmed independently by deterministic checks;
- exposes the passages and sections used as evidence.

## Measured baseline

### Publication safety benchmark

Historical baseline measured on the original 50 self-authored, paper-grounded examples:

| Metric | Result |
| --- | ---: |
| Decision accuracy | 100% |
| Unsupported-claim detection | 100% |
| Contradiction detection | 100% |
| False-publish rate | 0% |
| Human-review rate | 40% |

Current mixed benchmark, measured on August 17, 2026 using 50 synthetic cases
and 100 provenance-labelled real-paper cases:

| Metric | Result |
| --- | ---: |
| Decision accuracy | 82.67% |
| Unsupported-claim detection | 100% |
| Contradiction detection | 66.67% |
| False-publish rate | 0% |
| Human-review rate | 26.67% |

The current backend verification completes with 82 tests passing and one
optional PostgreSQL test skipped. The browser suite covers the primary
evaluation, authentication, review, benchmark, and analytics workflows. The
harder mixed benchmark intentionally exposes remaining conservative errors
while retaining a zero false-publish rate. The lower accuracy relative to the
earlier 100-case run reflects the addition of harder null-result, limitation,
subgroup, confidence-interval, and paraphrase cases rather than a change to the
earlier test set.

### Semantic retrieval benchmark

Measured on 10 deliberately paraphrased claim and evidence examples:

| Matcher | Top-passage accuracy |
| --- | ---: |
| Keyword overlap | 0% |
| MiniLM plus academic section ranking | 100% |
| Absolute improvement | +100 points |

### Natural-language-inference benchmark

Measured on 30 balanced entailment, contradiction, and neutral pairs:

| Metric | Result |
| --- | ---: |
| Overall accuracy | 93.33% |
| Confidence-threshold coverage | 93.33% |
| Abstention rate | 6.67% |
| Entailment recall | 100% |
| Contradiction recall | 100% |
| Neutral recall | 80% |
| False-entailment rate | 0% |
| False-contradiction rate | 10% |

These deliberately constructed regression benchmarks are not estimates of
general performance across academic literature. AnswerTrust is not suitable for
autonomous clinical or scientific decision-making.

The publication benchmark uses schema version 2 and now contains 150 cases: 50
project-created synthetic cases and 100 real-paper cases. The real-paper cases
use short Creative Commons PLOS excerpts with stable DOI provenance. They test
numbers, converted tables, subgroups, limitations, causal language, statistical
significance, scope changes, and reporting overstatement. Future real-paper
excerpts must record a source title, stable URL or DOI, excerpt section, reuse
license, difficulty category, reviewer label and confidence, annotation status,
and label rationale. This prevents synthetic cases from being presented as
independent or real-world evidence.

The evaluation page includes a loadable end-to-end example in which an AI
changes a result about some participants into a claim about every participant
and extends a four-week observation to long-term effectiveness. The interface
also states that AnswerTrust is a screening aid, not proof of scientific truth
or a replacement for expert medical, scientific, or publication review.

Repeated paper-level metadata is stored in `data/evaluation_sources.json`, while
each benchmark case retains its own excerpt section, expected label, difficulty,
confidence, and rationale.

## Run the current application

AnswerTrust currently targets Python 3.11. Install and verify the backend in
PowerShell:

```powershell
python -m pip install -r requirements.txt
.\setup_ml.ps1
python -m pytest -q
```

Asynchronous evaluations require Redis. Start Redis locally with Docker:

```powershell
docker run --name answertrust-redis -p 6379:6379 redis:8
```

Start the API from the project root:

```powershell
python -m alembic upgrade head
python -m uvicorn src.api:app --reload
```

Start the evaluation worker in another terminal from the project root:

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\rq.exe worker --url redis://127.0.0.1:6379/0 --worker-class rq.worker.SpawnWorker evaluations
```

Create the first administrator in a separate terminal. The command asks for the
password without showing it on screen:

```powershell
python -m scripts.create_user --email admin@example.com --role ADMIN
```

Create reviewer accounts in the same way with `--role REVIEWER`. In a deployed
environment, set `ANSWERTRUST_AUTH_SECRET` to a long random value before
starting the API so signed sessions use a private secret.

Evaluation submissions have explicit resource boundaries. By default, request
bodies are capped at 1 MiB, questions at 2,000 characters, paper text at
500,000 characters, and answers at 20,000 characters. A client may submit 30
evaluations per 60-second window, and the Redis queue accepts a backlog of up
to 100 jobs. Oversized, malformed, throttled, and queue-saturated requests use
the standard JSON error envelope; throttled or saturated responses also include
`Retry-After`. These values can be adjusted with the corresponding variables in
`.env.example`. The built-in rate limiter is process-local, so a multi-instance
deployment should enforce a shared limit at its gateway or replace it with a
Redis-backed limiter.

The API exposes two operational checks:

- `GET /api/v1/health` confirms that the process is running;
- `GET /api/v1/readiness` confirms that the database is reachable.

Administrators can read non-sensitive process counters from
`GET /api/v1/metrics` with their bearer token. API requests and completed
evaluations produce structured JSON logs without paper text, answers,
passwords, or reviewer notes.

The administrator-only `GET /api/v1/analytics` endpoint and React Analytics
page calculate persistent totals and trends from saved evaluations, review
tasks, review decisions, and benchmark runs.

In a second terminal, start the React application:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173`. The first ML setup downloads model files into the
ignored `model_cache/` directory. The local application database is created at
`data/answertrust.db`. Both remain excluded from Git.

## Reproduce the benchmarks

```powershell
python -m src.experiments
python -m src.experiments --compare-matchers
python -m src.experiments --benchmark-nli
python -m src.experiments --analyze-nli
```

The publication benchmark writes the full result set to
`results/experiment_results.csv`. It also writes only system-versus-reviewer
differences to `results/benchmark_disagreements.csv`. The disagreement export
excludes the question, paper text, and answer so it can be shared for review
without copying benchmark text into the export.

## Run an independent label review

Create a repeatable blind sample of 30 real-paper cases:

```powershell
python -m src.reviewer_agreement export --sample-size 30
```

Give `results/independent_review.csv` to a second person. They should fill in
only `independent_label`, `reviewer_confidence`, and `reviewer_notes`. Valid
labels are `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`,
and `INSUFFICIENT_EVIDENCE`; confidence is a number from 0 to 1. The sheet does
not contain the project-authored label or the system prediction.

After the completed sheet is returned, calculate agreement:

```powershell
python -m src.reviewer_agreement report results/independent_review.csv
```

The command validates the sheet and writes `results/reviewer_agreement.json`
with raw agreement, a 95% Wilson confidence interval, Cohen's kappa,
category-level agreement, and the disputed case IDs. The reviewer must work
independently for these numbers to be meaningful; a project author filling in
the second column does not count as independent validation.

## Run the complete stack with Docker

Copy `.env.example` to `.env` and replace both example secrets before using the
stack outside local development. Then build and start all five services:

```powershell
docker compose up --build
```

The website is available at `http://127.0.0.1:5173` and the API documentation
at `http://127.0.0.1:8000/docs`. PostgreSQL and Redis data are stored in Docker
volumes and survive container restarts.

Create the first administrator after the API is healthy:

```powershell
docker compose exec api python -m scripts.create_user --email admin@example.com --role ADMIN
```

Stop the stack with `Ctrl+C`. To stop containers without deleting saved data:

```powershell
docker compose down
```

Continuous integration is not checked into the repository yet. The intended
workflow should run backend tests against PostgreSQL, build and lint the React
application, run Playwright in Chromium, and verify both container images on
pushes and pull requests.

The NLI analysis reports incorrect or below-threshold examples, false
entailments, false contradictions, and a confidence-threshold sweep.

## Project boundary

The pivot strengthens the engineering around AnswerTrust without turning it
into a generic LLM application. Multi-paper synthesis, general-purpose RAG,
hosted LLM dependencies, autonomous publication, premature microservices, and
Kubernetes without a concrete operational need remain outside the near-term
scope.

## Possible future improvements

The current release is intentionally limited to checking one answer against
paper text supplied by the user. Reasonable next steps would be:

- complete the independent 30-case review and publish agreement results;
- improve contradiction handling for difficult paraphrases and null results;
- add PDF text extraction while preserving page and section references;
- add accessibility testing beyond the existing browser checks;
- deploy the Docker stack with managed secrets, backups, and error monitoring;
- repeat the real-paper benchmark with reviewers from different backgrounds.

Multi-paper synthesis and autonomous publication decisions should only be
considered after the single-paper safety workflow has stronger external
validation.

## Database guide

See the [database modes and legacy import section](PROJECT_REFERENCE.md#database-modes-and-legacy-import)
for SQLite and PostgreSQL setup, Alembic migrations, integration testing, and
legacy data import instructions.
