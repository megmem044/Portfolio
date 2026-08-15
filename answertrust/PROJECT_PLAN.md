# AnswerTrust project plan

**Last updated: August 15, 2026**

## Product direction

AnswerTrust is becoming a production-style asynchronous AI evaluation platform.
The product goal is unchanged: evaluate an AI-generated answer only against a
supplied academic paper, expose evidence for every claim-level decision, measure
system behavior, and escalate uncertain cases to a human reviewer.

The pivot is architectural. The verified evaluator remains the domain core, but
the Streamlit and SQLite prototype will evolve into a distributed web application
that demonstrates frontend, backend, database, asynchronous processing, testing,
ML integration, observability, and deployment practices.

## Target architecture

```text
React + TypeScript frontend
          |
          | REST API
          v
      FastAPI API --------> PostgreSQL
          |
          v
     Redis job queue
          |
          v
  Evaluation worker ------> PostgreSQL
  - evidence retrieval
  - MiniLM embeddings
  - NLI classification
  - deterministic rules

Docker Compose | CI/CD | pytest | Playwright | logs and metrics
```

The API will accept an evaluation, persist it with a `QUEUED` state, enqueue the
job, and immediately return its ID. A separate worker will run the CPU-heavy ML
pipeline, persist intermediate and final state, and support safe retries.

Planned lifecycle states are `QUEUED`, `PROCESSING`, `COMPLETED`,
`REVIEW_REQUIRED`, `APPROVED`, `REJECTED`, `FAILED`, and `RETRYING`.

## Verified baseline

The current local MVP is complete and remains the behavioral reference during
the migration.

### Evaluation engine

- Accept paper text, a research question, and an AI-generated answer.
- Parse common academic sections and extract independently reviewable claims.
- Retrieve section-labelled evidence with local MiniLM sentence embeddings,
  academic section priors, and keyword fallback.
- Classify claims as `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`,
  `CONTRADICTED`, or `INSUFFICIENT_EVIDENCE`.
- Combine confidence-gated NLI with deterministic academic checks.
- Detect overstatement, unsupported claims, missing qualifications,
  correlation-as-causation, and population or scope extrapolation.
- Produce `PUBLISH`, `REVIEW`, and `REJECT` decisions.
- Route NLI-only contradictions to review and independently confirmed
  contradictions to rejection.

### Prototype workflow

- Provide Streamlit evaluation, human-review, and benchmark pages.
- Persist evaluations, retries, system decisions, and reviewer decisions in
  SQLite.
- Preserve the original system decision when a reviewer resolves a case.
- Use repository-local model caching and Windows setup and launch scripts.

### Measurement baseline

- `22` automated tests pass.
- Publication decision accuracy: `100%` on 50 examples.
- False-publish rate: `0%` on the current safety set.
- Semantic top-passage accuracy: `100%` on 10 paraphrase examples.
- NLI accuracy: `93.33%` on 30 balanced pairs.
- NLI false-entailment rate: `0%`.
- NLI false-contradiction rate: `10%`.

These figures come from small, self-authored regression sets. They are not
general scientific-performance estimates.

## Migration principles

- Preserve evaluator behavior while changing delivery architecture.
- Keep ML inference outside the HTTP request path.
- Make jobs idempotent so a retry cannot duplicate evaluation results.
- Persist every state transition and retain the original system decision.
- Introduce service boundaries around retrieval, classification, and the full
  evaluation pipeline.
- Keep the application runnable at the end of each migration phase.
- Use migrations and compatibility tests rather than a one-step rewrite.

## Implementation roadmap

### Phase 1: FastAPI service boundary

- Extract the evaluator behind `EvidenceRetriever`, `ClaimClassifier`, and
  `EvaluationPipeline` interfaces.
- Add a versioned FastAPI REST API with request and response validation.
- Implement endpoints to create, retrieve, list, and review evaluations.
- Add pagination and consistent API error responses.
- Keep the existing Streamlit interface usable against the service during the
  transition.

### Phase 2: PostgreSQL persistence

- Replace prototype persistence with SQLAlchemy, Alembic, and PostgreSQL.
- Model users, papers, evaluations, claims, evidence passages, model
  predictions, review tasks, review decisions, benchmark runs, and benchmark
  results.
- Add foreign keys, uniqueness and state constraints, indexes, and transactions.
- Migrate representative SQLite data or provide a documented clean migration
  path.
- Add database integration tests for lifecycle and review audit behavior.

### Phase 3: Asynchronous evaluation

- Add Redis and a background job worker.
- Return an evaluation ID immediately with status `QUEUED`.
- Persist transitions through processing, completion, review, and failure.
- Add bounded retries with idempotency keys and recovery from worker failure.
- Ensure ML models load in worker processes rather than API processes.
- Expose status polling; consider server-sent events only after polling works.

### Phase 4: React frontend

- Build a React, TypeScript, and Vite application as the primary interface.
- Add `/evaluate`, `/evaluations/:id`, `/review`, and `/benchmarks` routes.
- Implement evaluation submission, live status, result details, claim evidence,
  review decisions, benchmark charts, and error analysis.
- Cover loading, empty, validation, failure, retry, and responsive states.
- Retire Streamlit as the primary UI after feature parity is verified.

### Phase 5: Containers and automated testing

- Add Dockerfiles and Docker Compose for frontend, API, worker, PostgreSQL, and
  Redis.
- Organize pytest coverage into unit and integration suites.
- Add Playwright tests for evaluation and review workflows.
- Add linting, formatting, Python and TypeScript type checks, frontend builds,
  integration tests, browser tests, and image builds to GitHub Actions.
- Verify the complete stack from a clean checkout.

### Phase 6: Authentication and authorization

- Add authentication after the core asynchronous workflow is stable.
- Define reviewer and administrator roles with least-privilege API policies.
- Protect review actions and retain an immutable audit trail.
- Avoid storing unnecessary personal information.

### Phase 7: Observability and analytics

- Emit structured logs containing evaluation, claim, model, worker, stage,
  duration, and outcome identifiers.
- Measure evaluation, retrieval, and NLI latency; queue depth; failures; retries;
  review volume; model abstention; and false-publish rate.
- Add health and readiness endpoints and basic operational dashboards.
- Add a SQL-backed analytics view for evaluation and benchmark trends.

### Phase 8: Benchmark quality and portfolio release

- Export de-identified system and reviewer disagreements.
- Expand to at least 100 examples drawn from real paper excerpts.
- Obtain independent labels for a subset and report inter-annotator agreement
  and confidence intervals.
- Test long passages, converted tables, numerical contradictions, subgroups,
  limitations, causal claims, and inconsistent headings.
- Add screenshots or a short demonstration, an end-to-end overstatement case,
  and visible limitations and responsible-use guidance.
- Create a versioned release after clean-environment verification.

### Phase 9: Optional deployment

- Deploy the containerized application to a suitable cloud platform.
- Document configuration, secrets, backups, rollback, and cost boundaries.
- Consider Kubernetes only after the Docker-based system is stable and there is
  a concrete orchestration requirement.

## Near-term definition of done

The architectural pivot is established when a user can submit an evaluation
through the REST API, receive an ID without waiting for inference, observe its
persisted state, and retrieve the worker-produced result from PostgreSQL. This
flow must run through Docker Compose and be covered by integration tests before
the React migration becomes the primary focus.

## Deliberate non-goals

Until the core asynchronous platform and independent benchmark are complete, do
not prioritize:

- multi-paper synthesis, vector databases, or general-purpose RAG;
- hosted LLM dependencies or training a large custom model;
- autonomous publication decisions;
- premature microservice decomposition;
- Kubernetes without a demonstrated operational need;
- features unrelated to paper-grounded evaluation and human review.
