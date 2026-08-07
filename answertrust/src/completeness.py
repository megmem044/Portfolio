"""Evaluate whether an answer addresses the complete request."""

from src.models import DimensionScore
from src.relevance import meaningful_words
from src.source_support import evaluate_source_support


def evaluate_completeness(
    question: str,
    reference: str,
    answer: str,
) -> DimensionScore:
    """Return a deterministic completeness score."""

    question_words = meaningful_words(question)
    answer_words = meaningful_words(answer)

    covered_words = question_words & answer_words
    coverage = (
        len(covered_words) / len(question_words)
        if question_words
        else 0
    )

    source_support = evaluate_source_support(reference, answer)

    multipart_question = (
        " and " in question.lower()
        or question.count("?") > 1
    )

    if coverage >= 0.6:
        return DimensionScore(
            name="Completeness",
            score=100,
            explanation="The answer covers most key parts of the question.",
            concerns=[],
        )

    if source_support.score >= 80 and not multipart_question:
        return DimensionScore(
            name="Completeness",
            score=85,
            explanation="The answer provides a supported response to the request.",
            concerns=[],
        )

    if coverage > 0 or source_support.score >= 60:
        return DimensionScore(
            name="Completeness",
            score=55,
            explanation="The answer addresses only part of the request.",
            concerns=["The answer may be incomplete."],
        )

    return DimensionScore(
        name="Completeness",
        score=20,
        explanation="The answer does not cover the requested information.",
        concerns=["Important parts of the question are missing."],
    )