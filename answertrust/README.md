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

The repository scaffold and initial project definitions are being prepared.
The evaluator, Streamlit pages, experiment dataset, and recorded metrics are
not implemented yet. This section will be updated as verified milestones are
completed.

## Project structure

The project separates the user interface, evaluation logic, saved data, and
tests. This makes it easier to understand, test, and improve one part without
unexpectedly changing another.

The tree below shows the planned finished structure. Some files will be added
as their development phase is completed.

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
|   |-- 1_Evaluate_Answer.py        # Submit and evaluate an answer
|   |-- 2_Evaluation_History.py     # Review and filter earlier evaluations
|   `-- 3_Quality_Dashboard.py      # View quality, safety, and speed summaries
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
    |-- test_clarity.py             # Length, repetition, and readability examples
    |-- test_uncertainty.py         # Confidence and insufficient-evidence cases
    |-- test_scoring.py             # Score calculation and boundary checks
    |-- test_decision_engine.py     # Publish, Review, and Reject rules
    `-- test_database.py            # Saving, reading, and filtering history
```

### Folder guide

- **`src/` — How AnswerTrust works:** Contains the five quality checks and the
  supporting code that turns them into one recommendation. Keeping this logic
  away from the visible pages makes it easier to explain and test.
- **`pages/` — What the user sees:** Contains the three Streamlit pages for
  evaluating an answer, reviewing history, and understanding quality trends.
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

The run and test commands will be documented once the corresponding components
have been implemented and verified.

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
