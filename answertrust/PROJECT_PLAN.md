# AnswerTrust Roadmap

This file tracks work that is finished, in progress, and still worth doing. It
is not a list of hypothetical features.

## Finished

### Evaluation

- Validate the question, reference, and answer.
- Score relevance, source support, completeness, clarity, and uncertainty.
- Calculate a weighted overall score.
- Return `PUBLISH`, `REVIEW`, or `REJECT` from visible decision rules.
- Report concerns, recommended action, and latency.

### Local model

- Support an optional cached `google/flan-t5-small` model.
- Keep deterministic scoring as the source of truth.
- Handle missing files, malformed output, and model errors without blocking the
  deterministic result.
- Compare baseline and safety prompts offline.

### Persistence and workflow

- Save evaluations in SQLite.
- Create a persistent run for each submission.
- Move runs through `RECEIVED`, `EVALUATING`, `APPROVED`, `HUMAN_REVIEW`,
  `REJECTED`, and `FAILED`.
- Store the evaluation linked to a run.
- Let a reviewer approve or reject runs in `HUMAN_REVIEW`.
- Classify failures and intervention reasons.
- Store failure type, failure message, and attempt count.
- Migrate existing local databases without deleting records.

### Interface and reporting

- Provide pages for new evaluations, human review, history, and quality metrics.
- Show workflow state and run ID in history.
- Show failure reasons and deterministic fallback use.
- Keep the interface usable when there is no saved data.

### Verification

- Maintain unit tests for scoring, decisions, persistence, workflow, review,
  failure classification, retry policy, experiments, and dashboard summaries.
- Maintain Streamlit interaction tests for each implemented page.
- Keep the core evaluator usable without network access or model files.

## In progress

### Automatic retry execution

The retry policy currently allows another attempt after `MODEL_TIMEOUT` or
`EVALUATION_ERROR`. The database can store attempt counts and the `RETRYING`
state exists. The workflow still needs to execute the second attempt.

Work remaining:

1. loop over attempts in `src/workflow.py`;
2. move the run to `RETRYING` before a later attempt;
3. save the final attempt count;
4. stop after the configured limit;
5. test recovery and exhausted retries.

## Next

### Run event history

The run table stores the latest state. Add an append-only event table so the
application can show how a run reached that state.

Suggested event fields:

- event ID;
- run ID;
- timestamp;
- previous and next state;
- attempt number;
- failure type; and
- short message.

### Review notes

Store the reviewer decision, note, and timestamp. Reviewer identity can remain
optional while the application is local and single-user.

### Operational dashboard

Add run-focused metrics:

- current state counts;
- review queue size;
- failed-run count;
- retry and recovery counts;
- failure-type distribution; and
- approval and rejection rates.

### Configurable rules

Move decision thresholds and retry limits into a small validated configuration
object. Show the active configuration in the interface, but do not allow silent
changes to old run results.

## Later improvements

- Filter history by workflow state and failure type.
- Add pagination once local history becomes large.
- Export selected run records without exposing the whole database.
- Add reviewer notes to the history view.
- Add structured logging for local debugging.
- Improve source-support checks for paraphrases and contradictions.
- Add more labelled examples around policy exceptions and multi-part answers.

## Release checks

Before calling a version complete:

- run the full test suite;
- open every Streamlit page;
- test a publish, review, reject, failure, retry, and fallback path;
- reproduce any metrics quoted in the README;
- confirm the evaluator works with model files removed;
- confirm an older database upgrades without data loss;
- check that local databases, cached models, virtual environments, and generated
  result files are not staged in Git; and
- follow the setup instructions from a clean Python 3.11 environment.

## Project boundary

AnswerTrust measures support against supplied reference material. It is not an
independent fact-checker or a production moderation service.
