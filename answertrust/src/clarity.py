"""Evaluate whether an answer is clear and readable."""

from src.models import DimensionScore
from src.relevance import meaningful_words


def evaluate_clarity(answer: str) -> DimensionScore:
    """Return a deterministic clarity score."""

    words = meaningful_words(answer)
    concerns: list[str] = []
    score = 100

    if len(words) > 200:
        score -= 30
        concerns.append("The answer may be unnecessarily long.")

    if answer.count("!") > 3:
        score -= 20
        concerns.append("Excessive punctuation reduces readability.")

    if len(answer) > 20 and answer.isupper():
        score -= 25
        concerns.append("Using all capital letters reduces readability.")

    if words:
        unique_ratio = len(words) / len(answer.lower().split())
        if unique_ratio < 0.4:
            score -= 30
            concerns.append("The answer contains excessive repetition.")

    return DimensionScore(
        name="Clarity",
        score=max(0, score),
        explanation=(
            "The score is based on length, punctuation, capitalization, "
            "and repetition."
        ),
        concerns=concerns,
    )
