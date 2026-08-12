# AnswerTrust

AnswerTrust is a research-grounded MVP for checking an AI-generated answer only against a paper supplied by the user. It decomposes the answer into claims, surfaces matching passages and paper sections, identifies academic failure modes, and routes the result to `PUBLISH`, `REVIEW`, or `REJECT`.

## Resume-ready scope

- Paper text, research question, and AI answer input
- Claim labels: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT_EVIDENCE`
- Evidence passages tagged as Methods, Results, Discussion, Limitations, or another detected section
- Checks for overstatement, unsupported claims, missing qualifications, correlation-as-causation, and population/scope extrapolation
- SQLite workflow with automatic retry, original system decision, reviewer decision, notes, and timestamp
- 50 hand-labelled academic examples and reproducible metrics for decision accuracy, unsupported and contradiction detection, false-publish rate, and review rate

The evaluator is deliberately deterministic and inspectable. It is a portfolio MVP, not a clinical fact-checker, and it makes no claims beyond the supplied paper.

## Run

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.experiments
.\run.ps1
```

The local database is created at `data/answertrust.db`; benchmark results are written to `results/experiment_results.csv`.

The launcher uses a repository-local Streamlit profile. This avoids permission
errors when Streamlit cannot write to the Windows user profile and suppresses
its first-run email prompt.

## Architecture

```text
paper + question + AI answer
        -> section parsing
        -> claim extraction
        -> evidence matching
        -> academic-aware claim labels
        -> PUBLISH / REVIEW / REJECT
        -> reviewer audit trail
```

## Deliberate non-goals

No multi-paper synthesis, vector database, RAG, cloud deployment, hosted LLM pipeline, or large frontend. Those are stretch work after the measured MVP.
