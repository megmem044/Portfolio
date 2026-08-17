"""Transparent publication rules based on claim-level findings."""

from src.models import ClaimLabel, ClaimResult, Decision


def make_decision(claims: list[ClaimResult], completeness: int, relevance: int) -> Decision:
    labels = [claim.label for claim in claims]
    if not claims:
        return Decision.REJECT
    confirmed_contradictions = [
        claim
        for claim in claims
        if claim.label == ClaimLabel.CONTRADICTED
        and "NLI_ONLY_CONTRADICTION" not in claim.failure_types
    ]
    if confirmed_contradictions:
        return Decision.REJECT
    if any("NLI_ONLY_CONTRADICTION" in claim.failure_types for claim in claims):
        return Decision.REVIEW
    unsupported = labels.count(ClaimLabel.UNSUPPORTED)
    if unsupported and unsupported / len(labels) >= 0.5:
        return Decision.REJECT
    if any(label != ClaimLabel.SUPPORTED for label in labels) or completeness < 75:
        return Decision.REVIEW
    if any(claim.failure_types for claim in claims):
        return Decision.REVIEW
    if relevance < 35 or completeness < 75:
        return Decision.REVIEW
    return Decision.PUBLISH
