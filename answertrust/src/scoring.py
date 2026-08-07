"""Combine dimension scores into one overall quality score."""

from src.models import DimensionScore


SCORE_WEIGHTS = {
    "Relevance": 0.25,
    "Source support": 0.30,
    "Completeness": 0.20,
    "Clarity": 0.10,
    "Uncertainty handling": 0.15,
}


def calculate_overall_score(
    dimension_scores: list[DimensionScore],
) -> int:
    """Return a weighted overall score from 0 to 100."""

    scores_by_name = {
        dimension.name: dimension.score
        for dimension in dimension_scores
    }

    missing_dimensions = set(SCORE_WEIGHTS) - set(scores_by_name)

    if missing_dimensions:
        missing = ", ".join(sorted(missing_dimensions))
        raise ValueError(f"Missing dimension scores: {missing}")

    weighted_score = sum(
        scores_by_name[name] * weight
        for name, weight in SCORE_WEIGHTS.items()
    )

    return round(weighted_score)
