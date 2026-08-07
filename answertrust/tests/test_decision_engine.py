from src.decision_engine import make_decision
from src.models import Decision, DimensionScore


def make_score(name: str, score: int) -> DimensionScore:
    return DimensionScore(
        name=name,
        score=score,
        explanation="Test score.",
        concerns=[],
    )


def complete_scores(
    relevance: int = 90,
    source_support: int = 90,
    completeness: int = 90,
    clarity: int = 90,
    uncertainty: int = 90,
) -> list[DimensionScore]:
    return [
        make_score("Relevance", relevance),
        make_score("Source support", source_support),
        make_score("Completeness", completeness),
        make_score("Clarity", clarity),
        make_score("Uncertainty handling", uncertainty),
    ]


def test_strong_scores_are_published():
    decision = make_decision(90, complete_scores())

    assert decision == Decision.PUBLISH


def test_score_below_publish_threshold_is_reviewed():
    decision = make_decision(79, complete_scores())

    assert decision == Decision.REVIEW


def test_low_source_support_is_rejected():
    scores = complete_scores(source_support=40)

    decision = make_decision(85, scores)

    assert decision == Decision.REJECT


def test_low_relevance_is_rejected():
    scores = complete_scores(relevance=40)

    decision = make_decision(85, scores)

    assert decision == Decision.REJECT


def test_weak_noncritical_dimension_requires_review():
    scores = complete_scores(clarity=55)

    decision = make_decision(82, scores)

    assert decision == Decision.REVIEW
