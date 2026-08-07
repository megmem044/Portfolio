"""Evaluate whether an answer is supported by its reference."""

from src.models import DimensionScore


def evaluate_source_support(
    reference: str,
    answer: str,
) -> DimensionScore:
    """Return a deterministic source-support score."""

    normalized_reference = reference.lower().strip()
    normalized_answer = answer.lower().strip()

    if normalized_answer == normalized_reference:
        return DimensionScore(
            name="Source support",
            score=100,
            explanation="The answer exactly matches the reference.",
            concerns=[],
        )

    if normalized_answer in normalized_reference:
        return DimensionScore(
            name="Source support",
            score=80,
            explanation="The answer appears within the reference.",
            concerns=[],
        )

    reference_words = set(normalized_reference.split())
    answer_words = set(normalized_answer.split())

    overlap = answer_words & reference_words
    overlap_ratio = len(overlap) / len(answer_words) if answer_words else 0

    if overlap_ratio >= 0.5:
        return DimensionScore(
            name="Source support",
            score=60,
            explanation="Part of the answer is supported by the reference.",
            concerns=["Some answer content may not be supported."],
        )

    return DimensionScore(
        name="Source support",
        score=20,
        explanation="The answer has little support in the reference.",
        concerns=["The answer may contain unsupported information."],
    )