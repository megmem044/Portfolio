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

Integrate a natural-language-inference cross-encoder for entailment,
contradiction, and neutral predictions. Before it can affect publication
decisions, add a dedicated labelled benchmark, confidence thresholds, offline
fallback behavior, and comparison against the deterministic baseline.

## Boundary

Multi-paper synthesis, vector databases, RAG, cloud deployment, and a large
frontend remain intentionally out of scope.
