# AnswerTrust

**AnswerTrust helps determine whether an AI-generated answer deserves the
user's trust.**

AnswerTrust is a local answer-quality evaluation and guardrail prototype for a
knowledge-sharing platform. Given a question, reference information, and an
AI-generated answer, it will assess whether the answer is relevant, supported,
clear, complete, and appropriately cautious before recommending that it be
published, reviewed, or rejected.

> AnswerTrust does not determine whether a statement is universally true. It
> evaluates whether an answer is supported by the reference information
> provided.

## Why this project matters

AI-generated answers can sound confident even when they are irrelevant,
incomplete, unclear, or unsupported. These failures can reduce trust in a
consumer knowledge product. AnswerTrust is designed to make those risks visible
through understandable scores, specific concerns, and transparent decision
rules.

This is a portfolio project demonstrating production-oriented evaluation
principles. It is not presented as a production-ready moderation system.

## Planned evaluation output

For each submitted answer, the completed application will return:

- An overall quality score from 0 to 100
- Relevance, source-support, clarity, completeness, and uncertainty-handling
  scores
- A final `PUBLISH`, `REVIEW`, or `REJECT` recommendation
- A concise explanation and detected concerns
- A recommended next action
- Evaluation latency information

## Evaluation approach

The deterministic evaluator will remain the official source of scores and
decisions. It will use transparent text signals and configurable thresholds so
that its recommendations can be inspected and tested.

A small local instruction-following transformer is planned as an optional
enhancement for concise explanations and prompt experiments. The application
will continue to work if that model is unavailable. No paid API, API key, or
cloud service is required.

## Quality dimensions

1. **Relevance** — Does the answer respond to the question?
2. **Source support** — Are important claims supported by the supplied
   reference?
3. **Completeness** — Does the answer address the central and multi-part
   request?
4. **Clarity** — Is the response readable, focused, and well structured?
5. **Appropriate uncertainty** — Does its confidence match the available
   evidence?

## Planned technology

- Python 3.11
- Streamlit
- scikit-learn
- pandas
- SQLite through Python's built-in `sqlite3`
- Hugging Face Transformers and PyTorch
- `google/flan-t5-small` or a similarly small local model
- pytest

The project will use only self-authored evaluation examples. It will not scrape
or copy questions or answers from Quora or another platform.

## Current status

The deterministic evaluation pipeline, main Streamlit evaluation page, local
SQLite history, Evaluation History page, labelled offline experiment, and
Quality Dashboard are implemented. AnswerTrust currently validates input,
scores all five quality dimensions, calculates a weighted overall score, and
returns a `PUBLISH`, `REVIEW`, or `REJECT` recommendation with concerns and a
recommended action. Valid evaluations are saved locally and can be reviewed or
filtered by decision.

The automated suite currently covers validation, individual quality checks,
score weighting, decision boundaries, evaluator integration, SQLite creation
and queries, labelled offline experiments, dashboard summaries, and Streamlit
interactions for all implemented pages. The optional local transformer remains
planned work.

## Project structure

The project separates the user interface, evaluation logic, saved data, and
tests. This makes it easier to understand, test, and improve one part without
unexpectedly changing another.

The tree below shows the planned finished structure. The evaluator, main
application, database, and history page are implemented; experiment, dashboard,
and optional model files will be added in later phases.

```text
answertrust/
|-- app.py                          # Application entry point
|-- README.md                       # Project overview and instructions
|-- PROJECT_PLAN.md                 # Short build and testing roadmap
|-- requirements.txt                # Python packages needed to run the project
|-- THIRD_PARTY_NOTICES.md           # Package purposes, licences, and sources
|-- LICENSE                         # MIT licence for original project code
|-- .gitignore                      # Files Git should leave on this computer
|
|-- data/                            # Examples and local evaluation history
|   |-- evaluation_examples.json    # Self-authored labelled test examples
|   `-- answertrust.db              # Generated local history; not committed
|
|-- results/                         # Outputs from repeatable experiments
|   `-- experiment_results.csv      # Measured evaluator and prompt results
|
|-- pages/                           # Pages a user opens in Streamlit
|   |-- 2_Evaluation_History.py     # Review and filter earlier evaluations
|   `-- 3_Quality_Dashboard.py      # Quality, safety, and speed summaries
|
|-- src/                             # Main evaluation and support code
|   |-- __init__.py                 # Marks src as the AnswerTrust code package
|   |-- config.py                   # Shared limits, score rules, and file paths
|   |-- models.py                   # Common shapes for inputs and results
|   |-- validation.py               # Checks that submitted text is usable
|   |-- relevance.py                # Checks if the answer addresses the question
|   |-- source_support.py           # Checks claims against the reference
|   |-- completeness.py             # Checks if the full request was answered
|   |-- clarity.py                  # Finds readability and writing concerns
|   |-- uncertainty.py              # Checks whether confidence fits the evidence
|   |-- scoring.py                  # Combines the five quality scores
|   |-- decision_engine.py          # Recommends Publish, Review, or Reject
|   |-- transformer_evaluator.py    # Optional local-model explanations
|   |-- database.py                 # Saves and retrieves evaluation history
|   |-- experiments.py              # Runs labelled examples and measures results
|   `-- utils.py                    # Small text helpers shared by several checks
|
`-- tests/                           # Automated checks for expected behaviour
    |-- test_validation.py          # Input validation examples
    |-- test_relevance.py           # Relevant and irrelevant answer examples
    |-- test_source_support.py      # Supported and unsupported claim examples
    |-- test_completeness.py        # Complete and partial answer examples
    |-- test_clarity.py             # Length, repetition, and readability examples
    |-- test_uncertainty.py         # Confidence and insufficient-evidence cases
    |-- test_scoring.py             # Score calculation and boundary checks
    |-- test_decision_engine.py     # Publish, Review, and Reject rules
    |-- test_evaluator.py           # Complete evaluation pipeline checks
    |-- test_database.py            # Saving, reading, and filtering history
    |-- test_app.py                 # Main Streamlit page interactions
    `-- test_history_page.py        # History page and filter interactions
```

### Folder guide

- **`src/` — How AnswerTrust works:** Contains the five quality checks and the
  supporting code that turns them into one recommendation. Keeping this logic
  away from the visible pages makes it easier to explain and test.
- **`pages/` — What the user sees:** Contains the implemented history page and
  will later contain the quality dashboard. The main evaluation page is
  `app.py`.
- **`tests/` — Evidence that behavior is reliable:** Contains repeatable
  examples that check normal cases, decision boundaries, and expected failures.
  The main test collection will not require internet access or the local AI
  model.
- **`data/` — Examples and local history:** Holds the original labelled examples
  used to evaluate the project. It is also the location of the generated SQLite
  history database, which stays on the user's computer and out of Git.
- **`results/` — Measured performance:** Holds experiment tables such as
  decision accuracy, false-publish rate, and evaluation speed. Results will be
  generated by running the experiment rather than written by hand.

The root files provide the entry point, documentation, setup information, and
licensing details a reviewer needs before exploring the implementation.

## Local setup

AnswerTrust targets Python 3.11. After Python is installed, run the following
commands from the project root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Confirm the environment and run the complete automated suite:

```powershell
python --version
python -m pytest -q
```

Start the Streamlit application:

```powershell
python -m streamlit run app.py
```

If Streamlit cannot create its optional global onboarding folder, start it
without onboarding or automatic browser launch:

```powershell
python -m streamlit run app.py --server.headless true --browser.gatherUsageStats false
```

Then open `http://localhost:8501` in a browser.

## Using evaluation history

Submit a valid question, reference, and answer from the main page. After the
evaluation completes, AnswerTrust saves the input, decision, scores, concerns,
recommended action, and latency to `data/answertrust.db`.

Open **Evaluation History** from the Streamlit sidebar to:

- Review saved evaluations newest-first
- Inspect the original question, reference, and answer
- Review the overall and dimension scores
- Filter records by `PUBLISH`, `REVIEW`, or `REJECT`

The database is created automatically on first use. It is excluded by
`.gitignore` and should not be committed. Empty or invalid submissions are not
saved.

## Offline experiment

Run the repeatable labelled experiment from the project root:

```powershell
python -m src.experiments
```

The command evaluates 20 self-authored examples and writes per-example results
to `results/experiment_results.csv`. The current measured results are:

| Metric | Result |
|---|---:|
| Decision accuracy | 100% |
| False-publish rate | 0% |
| Unsupported-answer detection | 100% |
| Review rate | 40% |
| Labelled examples | 20 |

These measurements describe only the small, self-authored dataset included in
this repository. They do not establish general accuracy or production safety.
The result CSV is generated locally and excluded from Git so reported values
must be reproduced by running the command.

## Quality dashboard

Open **Quality Dashboard** from the Streamlit sidebar. It shows local evaluation
counts, average score, average latency, decision distribution, common concerns,
and the latest generated experiment metrics. If no result CSV exists, the page
shows the command required to generate it.

## Privacy and licensing

Evaluation inputs are intended to remain on the local computer. Project source
code is licensed under the MIT License. Major third-party packages, their
purposes, licences, and official sources are recorded in
`THIRD_PARTY_NOTICES.md`.

## Known limitations

- The project is currently under development.
- Reference support is not the same as universal factual correctness.
- Transparent text heuristics cannot capture every form of meaning or error.
- Local transformer output may vary and will not override the deterministic
  decision in the first complete version.

## License

The original AnswerTrust source code is available under the MIT License. See
`LICENSE` for details.
