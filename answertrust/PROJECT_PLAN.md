# AnswerTrust project plan

## Product goal

Build a resume-ready, research-grounded evaluation system that checks an
AI-generated answer only against a supplied academic paper, exposes evidence
for every claim-level decision, measures its behavior, and escalates uncertain
cases to a human reviewer.

## Completed

### Paper-grounded evaluation

- Accept paper text, a research question, and an AI-generated answer.
- Parse common academic sections.
- Extract answer claims.
- Retrieve and display evidence passages with section labels.
- Produce `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`,
  and `INSUFFICIENT_EVIDENCE` claim labels.
- Detect overstatement, unsupported claims, missing qualifications,
  correlation-as-causation, and population/scope extrapolation.
- Produce `PUBLISH`, `REVIEW`, and `REJECT` decisions.

### Machine-learning evaluation

- Add local MiniLM sentence embeddings for paraphrase-aware evidence matching.
- Add academic section priors so outcome claims prefer Results evidence over
  shallow subject overlap in Methods.
- Preserve keyword evidence matching as a fallback.
- Add a local NLI cross-encoder for entailment, contradiction, and neutral
  predictions.
- Apply a 65% confidence threshold and retain deterministic fallback.
- Route NLI-only contradictions to `REVIEW` because the measured benchmark
  shows a 10% false-contradiction rate.
- Keep independently confirmed contradictions as automatic `REJECT` outcomes.
- Configure Hugging Face to use the repository-local ignored model cache.

### Workflow and persistence

- Store evaluations and claim evidence in SQLite.
- Implement automatic retry for transient evaluation failures.
- Preserve the original system decision.
- Store reviewer approval or rejection, notes, and timestamps.
- Provide a persistent human-review queue.

### Measurement

- Maintain 50 labelled publication-safety examples.
- Maintain 10 paraphrase-aware evidence-retrieval examples.
- Maintain 30 balanced NLI examples.
- Report decision accuracy, unsupported and contradiction detection,
  false-publish rate, review rate, retrieval improvement, NLI accuracy,
  per-class recall, coverage, abstention, false entailment, and false
  contradiction.
- Provide an NLI confidence-threshold sweep and visible error analysis.

### Interface

- Replace the prototype UI with a responsive editorial design system.
- Use a shared theme across Evaluation, Human Review, and Benchmarks.
- Give each page a distinct palette treatment while keeping navigation
  consistent and accessible.
- Show verdicts, claim explanations, NLI confidence, academic failures, and
  evidence passages in structured cards.
- Provide a benchmark dashboard that runs ML measurements on demand.
- Use repository-local Windows launch and ML setup scripts.

### Verification baseline

- `22` automated tests pass.
- Publication decision accuracy: `100%` on 50 examples.
- False-publish rate: `0%` on the current safety set.
- Semantic top-passage accuracy: `100%` on 10 paraphrase examples.
- NLI accuracy: `93.33%` on 30 balanced pairs.
- NLI false-entailment rate: `0%`.
- NLI false-contradiction rate: `10%`.

These figures describe small self-authored regression sets and must not be
presented as general scientific-performance estimates.

## Next milestones

### 1. Reviewer-feedback dataset

- Export de-identified system and reviewer disagreements.
- Record whether the reviewer agreed with claim labels and evidence passages.
- Separate decision overrides from evidence-quality feedback.
- Use the collected feedback for error analysis before any retraining.

### 2. Larger independent benchmark

- Expand to 100 or more examples drawn from real paper excerpts.
- Have a second person label a subset independently.
- Measure inter-annotator agreement.
- Add harder partial-support, numerical, subgroup, limitation, and causal cases.
- Report confidence intervals instead of only point estimates.

### 3. Calibration and robustness

- Calibrate NLI confidence on held-out examples.
- Evaluate section priors on papers with inconsistent headings.
- Test long passages, tables converted to text, multiple claims per sentence,
  and explicit numerical contradictions.
- Measure latency and memory use with and without ML models.
- Add regression examples for every production bug found during manual testing.

### 4. Portfolio release

- Add screenshots or a short demonstration GIF.
- Document one end-to-end subgroup-overstatement case.
- Add a concise limitations and responsible-use section to the interface.
- Create a versioned release after clean-environment verification.

## Deliberate non-goals

Until the milestones above are complete, do not prioritize:

- multi-paper synthesis;
- vector databases or RAG;
- cloud deployment;
- hosted LLM dependencies;
- autonomous publication decisions;
- training a large custom language model;
- a frontend rewrite outside Streamlit.

The project should remain focused on measurable, explainable single-paper
evaluation and human review.
