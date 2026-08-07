import pytest

from src.models import DimensionScore
from src.scoring import calculate_overall_score


def make_score(name: str, score: int) -> DimensionScore:
    return DimensionScore(
        name=name,
        score=score,
        explanation="Test score.",
        concerns=[],
    )


def test_equal_scores_produce_same_overall_score():
    scores = [
        make_score("Relevance", 80),
        make_score("Source support", 80),
        make_score("Completeness", 80),
        make_score("Clarity", 80),
        make_score("Uncertainty handling", 80),
    ]

    assert calculate_overall_score(scores) == 80


def test_source_support_has_larger_weight():
    scores = [
        make_score("Relevance", 100),
        make_score("Source support", 0),
        make_score("Completeness", 100),
        make_score("Clarity", 100),
        make_score("Uncertainty handling", 100),
    ]

    assert calculate_overall_score(scores) == 70


def test_missing_dimension_raises_error():
    scores = [
        make_score("Relevance", 80),
    ]

    with pytest.raises(ValueError, match="Missing dimension"):
        calculate_overall_score(scores)
