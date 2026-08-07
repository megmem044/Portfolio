"""Evaluate whether confidence matches the available evidence."""

from src.models import DimensionScore
from src.source_support import evaluate_source_support


ABSOLUTE_TERMS = {
    "always",
    "certainly",
    "definitely",
    "guaranteed",
    "never",
    "proven",
}

CAUTIOUS_TERMS = {
    "appears",
    "could",
    "insufficient",
    "may",
    "might",
    "possibly",
    "suggests",
    "uncertain",
}


def evaluate_uncertainty(
    reference: str,
    answer: str,
) -> DimensionScore:
    """Return a deterministic uncertainty-handling score."""

    answer_words = set(answer.lower().split())
    source_support = evaluate_source_support(reference, answer)

    uses_absolute_language = bool(answer_words & ABSOLUTE_TERMS)
    uses_cautious_language = bool(answer_words & CAUTIOUS_TERMS)

    if source_support.score < 60 and uses_absolute_language:
        return DimensionScore(
            name="Uncertainty handling",
            score=20,
            explanation="The answer is more confident than the reference supports.",
            concerns=[
                "Strong certainty language is not supported by the reference."
            ],
        )

    if source_support.score < 60 and uses_cautious_language:
        return DimensionScore(
            name="Uncertainty handling",
            score=90,
            explanation="The answer appropriately acknowledges limited evidence.",
            concerns=[],
        )

    if source_support.score < 60:
        return DimensionScore(
            name="Uncertainty handling",
            score=55,
            explanation="The answer should acknowledge that support is limited.",
            concerns=[
                "The confidence level may not match the available evidence."
            ],
        )

    return DimensionScore(
        name="Uncertainty handling",
        score=100,
        explanation="The answer's confidence matches the available support.",
        concerns=[],
    )
