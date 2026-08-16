"""Service boundary for finding evidence in an academic paper."""

from __future__ import annotations

from typing import Protocol

from src.academic import match_evidence
from src.models import Evidence
from src.semantic import SemanticMatcher


class EvidenceRetriever(Protocol):
    """Anything that can find paper passages relevant to a claim."""

    def retrieve(
        self,
        claim: str,
        sections: dict[str, str],
        limit: int = 2,
    ) -> list[Evidence]: ...


class AcademicEvidenceRetriever:
    """Use the existing lexical and optional semantic evidence matching."""

    def __init__(self, semantic_matcher: SemanticMatcher | None = None) -> None:
        self.semantic_matcher = semantic_matcher

    def retrieve(
        self,
        claim: str,
        sections: dict[str, str],
        limit: int = 2,
    ) -> list[Evidence]:
        return match_evidence(
            claim,
            sections,
            limit=limit,
            semantic_matcher=self.semantic_matcher,
        )
