# AnswerTrust

AnswerTrust is a research-grounded MVP for checking an AI-generated answer only against a paper supplied by the user. It decomposes the answer into claims, surfaces matching passages and paper sections, identifies academic failure modes, and routes the result to `PUBLISH`, `REVIEW`, or `REJECT`.

## Resume-ready scope

- Paper text, research question, and AI answer input
- Claim labels: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, and `INSUFFICIENT_EVIDENCE`
- Evidence passages tagged as Methods, Results, Discussion, Limitations, or another detected section
- Checks for overstatement, unsupported claims, missing qualifications, correlation-as-causation, and population/scope extrapolation
- SQLite workflow with automatic retry, original system decision, reviewer decision, notes, and timestamp
- 50 hand-labelled academic examples and reproducible metrics for decision accuracy, unsupported and contradiction detection, false-publish rate, and review rate
- Optional `all-MiniLM-L6-v2` sentence embeddings for paraphrase-aware evidence matching, with automatic keyword fallback

## Measured results

The deterministic safety benchmark contains 50 labelled examples:

| Metric | Result |
|---|---:|
| Overall decision accuracy | 100% |
| Unsupported-claim detection | 100% |
| Contradiction detection | 100% |
| False-publish rate | 0% |
| Human-review rate | 40% |

The separate 10-example paraphrase benchmark measures evidence retrieval:

| Matcher | Top-passage accuracy |
|---|---:|
| Keyword overlap | 0% |
| MiniLM semantic + section-aware ranking | 100% |

These results describe small, deliberately constructed project benchmarks and
must not be interpreted as general performance on academic literature.

The evaluator is deliberately deterministic and inspectable. It is a portfolio MVP, not a clinical fact-checker, and it makes no claims beyond the supplied paper.

## Run

```powershell
python -m pip install -r requirements.txt
.\setup_ml.ps1
python -m pytest -q
python -m src.experiments
python -m src.experiments --compare-matchers
.\run.ps1
```

The local database is created at `data/answertrust.db`; benchmark results are written to `results/experiment_results.csv`.
The matcher comparison uses ten deliberately paraphrased claims and reports
top-passage retrieval accuracy for lexical versus semantic matching.

The launcher uses a repository-local Streamlit profile. This avoids permission
errors when Streamlit cannot write to the Windows user profile and suppresses
its first-run email prompt.
The ML setup script downloads MiniLM once into the ignored `model_cache/`
directory so the app and matcher benchmark use the same writable cache.

## Architecture

```text
paper + question + AI answer
        -> section parsing
        -> claim extraction
        -> semantic evidence matching
           + academic section prior
           + keyword fallback
        -> academic-aware claim labels
        -> PUBLISH / REVIEW / REJECT
        -> reviewer audit trail
```

## Deliberate non-goals

No multi-paper synthesis, vector database, RAG, cloud deployment, hosted LLM
pipeline, or large frontend. Natural-language inference is the next measured
ML experiment, not an assumed production capability.
