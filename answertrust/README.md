# AnswerTrust

AnswerTrust checks an AI-generated answer against a reference supplied by the
user. It scores the answer, decides whether it can be published, and keeps a
record of what happened during the evaluation.

The project is built around a simple constraint: an answer should not be
trusted just because it sounds confident. It should address the question, stay
within the supplied evidence, cover the important details, and acknowledge
uncertainty when the reference is incomplete.

AnswerTrust does not search the web or establish whether a statement is true in
the wider world. Its decision is only as reliable as the reference it receives.

## What it does

Each submission contains:

- the original question;
- trusted reference material; and
- the answer being checked.

The deterministic evaluator scores five areas:

1. relevance;
2. source support;
3. completeness;
4. clarity; and
5. uncertainty handling.

Those scores produce one of three evaluation decisions:

- `PUBLISH` for answers that meet the configured rules;
- `REVIEW` for answers that need human judgment; or
- `REJECT` for answers that are irrelevant or insufficiently supported.

## Run workflow

Every submission is stored as an evaluation run rather than an isolated score.
A run starts in `RECEIVED`, moves to `EVALUATING`, and finishes in one of these
states:

- `APPROVED`;
- `HUMAN_REVIEW`;
- `REJECTED`; or
- `FAILED`.

The Human Review page lists uncertain runs and lets a reviewer approve or
reject them. Evaluation History shows the current workflow state, run ID,
scores, concerns, and any recorded failure classification.

The current failure taxonomy is:

- `MODEL_UNAVAILABLE`;
- `MODEL_TIMEOUT`;
- `INVALID_OUTPUT`;
- `LOW_CONFIDENCE`;
- `INSUFFICIENT_SUPPORT`; and
- `EVALUATION_ERROR`.

Timeouts and unexpected evaluation errors are marked as retryable by the retry
policy. Attempt counts are stored in SQLite. Automatic retry execution is the
next workflow step and is not connected yet.

## Optional local model

The official score and decision always come from the deterministic evaluator.
An optional local `google/flan-t5-small` model can provide supplemental text,
but it cannot override the result.

If the model is missing, AnswerTrust completes the run with the deterministic
evaluator and records `MODEL_UNAVAILABLE`. No API key or hosted model service is
required.

## Project layout

```text
answertrust/
|-- app.py                         # New evaluation page
|-- pages/
|   |-- 1_Human_Review.py          # Manual approval and rejection queue
|   |-- 2_Evaluation_History.py    # Saved evaluations and run details
|   `-- 3_Quality_Dashboard.py     # Local quality and experiment metrics
|-- src/
|   |-- evaluator.py               # Evaluation pipeline
|   |-- workflow.py                # Persistent run orchestration
|   |-- database.py                # SQLite storage and migrations
|   |-- review.py                  # Human-review decisions
|   |-- failure_classifier.py      # Failure taxonomy mapping
|   |-- retry_policy.py            # Retry eligibility and attempt limits
|   |-- decision_engine.py         # Publish, review, and reject rules
|   |-- transformer_evaluator.py   # Optional local model wrapper
|   `-- ...                        # Individual scoring modules
|-- tests/                         # Unit and Streamlit interaction tests
|-- data/                          # Labelled examples and local database
`-- results/                       # Generated experiment output
```

## Setup

AnswerTrust targets Python 3.11. From the project directory in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the tests:

```powershell
$env:PYTHONPATH="."
python -m pytest -q
```

Start the app:

```powershell
python -m streamlit run app.py --browser.gatherUsageStats false
```

If Streamlit cannot write to `C:\Users\<name>\.streamlit`, give that process a
writable local profile:

```powershell
$streamlitProfile = Join-Path $PWD ".streamlit-profile"
New-Item -ItemType Directory -Force -Path $streamlitProfile
$env:USERPROFILE = $streamlitProfile
python -m streamlit run app.py --browser.gatherUsageStats false
```

Open `http://localhost:8501` if the browser does not open automatically.

## Using the app

1. Open **New evaluation**.
2. Enter the question, reference, and generated answer.
3. Submit the form.
4. Review the score, decision, and concerns.
5. If the run enters `HUMAN_REVIEW`, resolve it from the Human Review page.
6. Use Evaluation History to inspect earlier runs.

The SQLite database is created at `data/answertrust.db`. It stays on the local
computer and is excluded from Git.

## Offline experiment

The repository includes 30 self-authored labelled examples. Run them with:

```powershell
python -m src.experiments
```

The last recorded deterministic results were:

| Metric | Result |
|---|---:|
| Decision accuracy | 86.67% |
| False-publish rate | 0% |
| Unsupported-answer detection | 83.33% |
| Review rate | 43.33% |

These numbers describe this small dataset only. They are not a claim about
general model accuracy or production safety.

To download the optional model and compare its two prompt versions:

```powershell
python -m src.experiments --compare-prompts --allow-download
```

After the model is cached locally, use:

```powershell
python -m src.experiments --compare-prompts
```

Generated CSV files are written to `results/` and excluded from Git.

## Current limitations

- Source support is not the same as independent fact-checking.
- The scoring modules use transparent text heuristics and will miss some forms
  of meaning, contradiction, and omission.
- Human review decisions currently store the final state but not reviewer
  identity or notes.
- The retry policy exists, but automatic retry execution is not connected to
  the workflow yet.
- The application is a portfolio project, not a production moderation service.

## Privacy and licence

Inputs, results, and cached model files remain local unless the user moves them
elsewhere. Original project code is available under the MIT License. Package
licences and sources are listed in `THIRD_PARTY_NOTICES.md`.
