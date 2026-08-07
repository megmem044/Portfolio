"""Convert evaluation scores into a publication decision."""

from src.models import Decision, DimensionScore


PUBLISH_THRESHOLD = 80
REJECT_DIMENSION_THRESHOLD = 50
PUBLISH_DIMENSION_MINIMUM = 80


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
    uncertainty = scores_by_name["Uncertainty handling"]

    # Irrelevant answers are rejected regardless of cautious wording.
    if relevance < REJECT_DIMENSION_THRESHOLD:
        return Decision.REJECT

    # Unsupported claims are rejected, while relevant answers that explicitly
    # acknowledge insufficient evidence are routed to human review.
    if source_support < REJECT_DIMENSION_THRESHOLD:
        if uncertainty >= 80:
            return Decision.REVIEW
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
