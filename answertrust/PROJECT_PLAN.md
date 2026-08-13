# AnswerTrust ML roadmap

## Completed

- Paper-grounded claim pipeline and evidence display
- Academic section parsing and failure checks
- Reviewer audit trail and automatic retry
- 50-example deterministic safety benchmark
- MiniLM sentence embeddings with offline keyword fallback
- 10-example lexical-versus-semantic retrieval benchmark
- Section-aware ranking that prioritizes Results passages for outcome claims

Current verification baseline: 12 tests, 100% decision accuracy on the
50-example safety set, and 100% semantic top-passage accuracy on the targeted
10-example paraphrase set. These small self-authored datasets are regression
benchmarks, not estimates of general model performance.

## Next measured step

The confidence-gated natural-language-inference cross-encoder is integrated
with offline fallback. Its dedicated 30-pair balanced benchmark currently
measures 93.33% overall accuracy, 100% entailment recall, 100% contradiction
recall, 80% neutral recall, and 93.33% coverage at the 65% threshold. The next
step is error analysis and threshold calibration, especially for neutral pairs,
before expanding the model's authority.

The resulting safety policy routes NLI-only contradictions to `REVIEW` and
reserves automatic `REJECT` for contradictions independently confirmed by the
deterministic checks.

## Boundary

Multi-paper synthesis, vector databases, RAG, cloud deployment, and a large
frontend remain intentionally out of scope.
