"""Convert evaluation scores into a publication decision."""

from src.models import Decision, DimensionScore


PUBLISH_THRESHOLD = 80
REJECT_DIMENSION_THRESHOLD = 50
PUBLISH_DIMENSION_MINIMUM = 60


def make_decision(
    overall_score: int,
    dimension_scores: list[DimensionScore],
) -> Decision:
    """Return a decision using transparent score thresholds."""

    scores_by_name = {
        dimension.name: dimension.score
        for dimension in dimension_scores
    }

    relevance = scores_by_name["Relevance"]
    source_support = scores_by_name["Source support"]

    # Serious relevance or support problems prevent publication.
    if (
        relevance < REJECT_DIMENSION_THRESHOLD
        or source_support < REJECT_DIMENSION_THRESHOLD
    ):
        return Decision.REJECT

    # Publishing requires a strong overall result with no weak dimension.
    if (
        overall_score >= PUBLISH_THRESHOLD
        and all(
            score >= PUBLISH_DIMENSION_MINIMUM
            for score in scores_by_name.values()
        )
    ):
        return Decision.PUBLISH

    return Decision.REVIEW
