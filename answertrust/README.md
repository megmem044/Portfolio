# AnswerTrust

**Last updated: August 16, 2026**

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
- GitHub Actions for build and test automation;
- structured logging and operational metrics.

These platform components are the planned direction, not current completed
features. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the phased roadmap and
definitions of done.

## Current status

The repository currently contains the verified web MVP:

- a React evaluation interface, human-review queue, and benchmark dashboard;
- a versioned FastAPI service;
- SQLAlchemy persistence with SQLite for local use and PostgreSQL support;
- Alembic database migrations and a documented legacy-data importer;
- local MiniLM embeddings for paraphrase-aware evidence retrieval;
- academic section priors and keyword retrieval fallback;
- confidence-gated NLI with deterministic fallback;
- claim-level evidence, explanations, failure types, and confidence details;
- preserved system and reviewer decisions with timestamps;
- repository-local model caching and Windows setup scripts;
- pytest API and database tests plus Playwright browser tests.

React is the primary interface. The asynchronous queue and worker remain future
project-plan phases.

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

Evaluation requests will return an ID immediately. The worker will advance each
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

Measured on 50 self-authored, paper-grounded examples:

| Metric | Result |
| --- | ---: |
| Decision accuracy | 100% |
| Unsupported-claim detection | 100% |
| Contradiction detection | 100% |
| False-publish rate | 0% |
| Human-review rate | 40% |

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

## Run the current application

AnswerTrust currently targets Python 3.11. Install and verify the backend in
PowerShell:

```powershell
python -m pip install -r requirements.txt
.\setup_ml.ps1
python -m pytest -q
```

Start the API from the project root:

```powershell
python -m uvicorn src.api:app --reload
```

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

The NLI analysis reports incorrect or below-threshold examples, false
entailments, false contradictions, and a confidence-threshold sweep.

## Project boundary

The pivot strengthens the engineering around AnswerTrust without turning it
into a generic LLM application. Multi-paper synthesis, general-purpose RAG,
hosted LLM dependencies, autonomous publication, premature microservices, and
Kubernetes without a concrete operational need remain outside the near-term
scope.

## Database guide

See [docs/database.md](docs/database.md) for SQLite and PostgreSQL setup,
Alembic migrations, integration testing, and legacy data import instructions.
