"""Evaluate whether an answer addresses its question."""

import re


from src.models import DimensionScore
from src.source_support import evaluate_source_support

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "for", "from", "how", "in", "is", "it", "of", "on",
    "or", "that", "the", "this", "to", "was", "were",
    "what", "when", "where", "which", "who", "why", "with",
}


def meaningful_words(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def evaluate_relevance(
    question: str,
    reference: str,
    answer: str,
) -> DimensionScore:
    """Return a deterministic relevance score."""

    question_words = meaningful_words(question)
    answer_words = meaningful_words(answer)

    shared_words = question_words & answer_words
    question_overlap = (
        len(shared_words) / len(question_words)
        if question_words
        else 0
    )

    source_support = evaluate_source_support(reference, answer)

    if source_support.score == 100:
        return DimensionScore(
            name="Relevance",
            score=90,
            explanation=(
                "The answer exactly matches the supplied reference and "
                "appears to address the question."
            ),
            concerns=[],
        )

    if question_overlap >= 0.5:
        return DimensionScore(
            name="Relevance",
            score=100,
            explanation="The answer directly overlaps with the question.",
            concerns=[],
        )

    if question_overlap > 0 or source_support.score >= 80:
        return DimensionScore(
            name="Relevance",
            score=75,
            explanation="The answer appears related to the question.",
            concerns=[],
        )

    return DimensionScore(
        name="Relevance",
        score=20,
        explanation="The answer does not appear to address the question.",
        concerns=["The answer may be irrelevant to the question."],
    )
