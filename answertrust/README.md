# AnswerTrust

AnswerTrust is a local, research-grounded system for evaluating an AI-generated
answer only against an academic paper supplied by the user. It decomposes the
answer into claims, retrieves the most relevant paper passages, checks whether
each claim is supported or contradicted, and routes the complete answer to
`PUBLISH`, `REVIEW`, or `REJECT`.

It does not search the web or treat outside knowledge as evidence.

## Current features

- Accepts a research question, paper text, and AI-generated answer.
- Detects common paper sections, including Methods, Results, Discussion, and
  Limitations.
- Extracts independently reviewable claims from an answer.
- Labels claims as `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`,
  `CONTRADICTED`, or `INSUFFICIENT_EVIDENCE`.
- Displays the passages and sections used as evidence.
- Detects overstatement, missing qualifications, correlation presented as
  causation, unsupported claims, and population/scope extrapolation.
- Uses `all-MiniLM-L6-v2` sentence embeddings for paraphrase-aware evidence
  retrieval, with keyword matching as an offline fallback.
- Uses a confidence-gated NLI cross-encoder for entailment, contradiction, and
  neutral classification, with deterministic fallback.
- Routes NLI-only contradictions to human `REVIEW`; independently confirmed
  contradictions remain automatic `REJECT` decisions.
- Stores evaluation runs, retries, system decisions, reviewer decisions, notes,
  and timestamps in SQLite.
- Includes a human-review queue and measured benchmark dashboard.

## Interface

The Streamlit interface uses an editorial research-tool design system inspired
by print style guides:

- ivory grid canvas and charcoal structure;
- Instrument Serif display headings with DM Sans controls;
- lemonade accents for Evaluation;
- lavender accents for Human Review;
- sky-blue accents for Benchmarks;
- midnight-blue primary actions;
- compact corners, fine borders, and offset shadows.

The application entry point is `Evaluation.py`. Use `run.ps1` rather than
calling Streamlit directly so its writable profile and local model cache are
configured consistently on Windows.

## Measured results

### Publication safety benchmark

Measured on 50 self-authored, paper-grounded examples:

| Metric | Result |
|---|---:|
| Decision accuracy | 100% |
| Unsupported-claim detection | 100% |
| Contradiction detection | 100% |
| False-publish rate | 0% |
| Human-review rate | 40% |

### Semantic retrieval benchmark

Measured on 10 deliberately paraphrased claim/evidence examples:

| Matcher | Top-passage accuracy |
|---|---:|
| Keyword overlap | 0% |
| MiniLM plus academic section ranking | 100% |
| Absolute improvement | +100 points |

### Natural-language-inference benchmark

Measured on 30 balanced entailment, contradiction, and neutral pairs:

| Metric | Result |
|---|---:|
| Overall accuracy | 93.33% |
| Confidence-threshold coverage | 93.33% |
| Abstention rate | 6.67% |
| Entailment recall | 100% |
| Contradiction recall | 100% |
| Neutral recall | 80% |
| False-entailment rate | 0% |
| False-contradiction rate | 10% |

These are small, deliberately constructed regression benchmarks. They are not
estimates of general performance across academic literature and do not make
AnswerTrust suitable for autonomous clinical or scientific decision-making.

## Setup and run

AnswerTrust targets Python 3.11. In PowerShell:

```powershell
python -m pip install -r requirements.txt
.\setup_ml.ps1
python -m pytest -q
.\run.ps1
```

The current verification baseline is:

```text
22 passed
```

The first ML setup downloads model files into the ignored `model_cache/`
directory. The application database is created at `data/answertrust.db`. Both
remain local and are excluded from Git.

## Reproduce the benchmarks

```powershell
python -m src.experiments
python -m src.experiments --compare-matchers
python -m src.experiments --benchmark-nli
python -m src.experiments --analyze-nli
```

The NLI analysis reports incorrect or below-threshold examples, false
entailments, false contradictions, and a confidence-threshold sweep.

## Architecture

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

## Project boundary

AnswerTrust intentionally does not include multi-paper synthesis, a vector
database, RAG, cloud deployment, or autonomous publication. Those are stretch
features only after the single-paper evaluation workflow is validated on
larger, independently labelled datasets.
