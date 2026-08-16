"""Backward-compatible entry point for answer evaluation."""

from src.classification import AcademicClaimClassifier, ClaimClassifier
from src.models import EvaluationInput, EvaluationResult
from src.nli import NLIClassifier
from src.pipeline import EvaluationPipeline
from src.retrieval import AcademicEvidenceRetriever, EvidenceRetriever
from src.semantic import SemanticMatcher


def evaluate_answer(
    evaluation_input: EvaluationInput,
    semantic_matcher: SemanticMatcher | None = None,
    nli_classifier: NLIClassifier | None = None,
    evidence_retriever: EvidenceRetriever | None = None,
    claim_classifier: ClaimClassifier | None = None,
    **_: object,
) -> EvaluationResult:
    """Build the default services and run the complete evaluation."""
    pipeline = EvaluationPipeline(
        evidence_retriever or AcademicEvidenceRetriever(semantic_matcher),
        claim_classifier or AcademicClaimClassifier(nli_classifier),
    )
    return pipeline.evaluate(evaluation_input)
