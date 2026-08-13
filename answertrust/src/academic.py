"""Small, transparent NLP helpers for academic paper text."""

from __future__ import annotations

import re
from collections import Counter
from typing import TYPE_CHECKING

from src.models import ClaimLabel, ClaimResult, Evidence

if TYPE_CHECKING:
    from src.semantic import SemanticMatcher

SECTIONS = ("ABSTRACT", "INTRODUCTION", "METHODS", "RESULTS", "DISCUSSION", "LIMITATIONS", "CONCLUSION")
STOP = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "were", "with"}
NEGATIONS = {"no", "not", "never", "didn't", "doesn't", "without", "failed"}
CAUSAL = {"cause", "caused", "causes", "led", "leads", "resulted", "because", "effect"}
CORRELATIONAL = {"associated", "association", "correlated", "correlation", "observational"}
UNIVERSAL = {"all", "always", "everyone", "every", "entirely", "guarantees", "proves", "cures"}
QUALIFIERS = {"may", "might", "could", "suggests", "associated", "some", "among", "limited", "uncertain"}
SEMANTIC_SECTION_PRIORS = {
    "RESULTS": 0.18,
    "DISCUSSION": 0.05,
    "CONCLUSION": 0.05,
}


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text.lower())


def content_words(text: str) -> set[str]:
    return {word for word in words(text) if word not in STOP and len(word) > 2}


def split_sections(text: str) -> dict[str, str]:
    """Parse common headings; unheaded text is treated as UNKNOWN."""
    heading = re.compile(r"(?im)^\s*(?:#+\s*)?(" + "|".join(SECTIONS) + r")\s*:?\s*$")
    matches = list(heading.finditer(text))
    if not matches:
        return {"UNKNOWN": text.strip()}
    sections: dict[str, str] = {}
    if text[: matches[0].start()].strip():
        sections["UNKNOWN"] = text[: matches[0].start()].strip()
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).upper()] = text[match.end():end].strip()
    return sections


def sentences(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+|\n+", text) if len(item.strip()) > 2]


def extract_claims(answer: str) -> list[str]:
    """Split prose into independently reviewable declarative claims."""
    claims: list[str] = []
    for sentence in sentences(answer):
        parts = re.split(r"\s*;\s*|\s+(?:but|whereas|however)\s+", sentence, flags=re.I)
        claims.extend(part.strip(" -") for part in parts if len(content_words(part)) >= 2)
    return claims


def _similarity(left: str, right: str) -> float:
    a, b = content_words(left), content_words(right)
    return len(a & b) / len(a) if a else 0.0


def match_evidence(
    claim: str,
    sections: dict[str, str],
    limit: int = 2,
    semantic_matcher: "SemanticMatcher | None" = None,
) -> list[Evidence]:
    """Rank passages semantically when available, otherwise by word overlap."""
    passages = [
        (section, passage)
        for section, body in sections.items()
        for passage in sentences(body)
    ]
    lexical_scores = [_similarity(claim, passage) for _, passage in passages]
    scores = lexical_scores
    if semantic_matcher is not None:
        try:
            semantic_scores = semantic_matcher.similarities(
                claim, [passage for _, passage in passages]
            )
            # Meaning drives ranking. Academic outcome claims receive a visible
            # Results-section prior so subject overlap in Methods does not win.
            rank_scores = [
                semantic + SEMANTIC_SECTION_PRIORS.get(section, 0.0)
                for (section, _), semantic in zip(passages, semantic_scores)
            ]
            candidates = [
                Evidence(section, passage, max(lexical, semantic))
                for (section, passage), lexical, semantic in zip(
                    passages, lexical_scores, semantic_scores
                )
            ]
            return [
                candidate
                for _, candidate in sorted(
                    zip(rank_scores, candidates),
                    key=lambda item: item[0],
                    reverse=True,
                )[:limit]
            ]
        except Exception:
            scores = lexical_scores
    candidates = [
        Evidence(section, passage, score)
        for (section, passage), score in zip(passages, scores)
    ]
    return sorted(candidates, key=lambda item: item.similarity, reverse=True)[:limit]


def _has_negation(text: str) -> bool:
    return bool(set(words(text)) & NEGATIONS)


def evaluate_claim(claim: str, evidence: list[Evidence], paper_text: str) -> ClaimResult:
    best = evidence[0] if evidence else Evidence("UNKNOWN", "", 0.0)
    claim_words, evidence_words = set(words(claim)), set(words(best.passage))
    failures: list[str] = []
    contradictory = best.similarity >= 0.32 and _has_negation(claim) != _has_negation(best.passage)
    numbers_claimed = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", claim))
    numbers_evidenced = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", best.passage))
    if numbers_claimed and numbers_evidenced and not numbers_claimed <= numbers_evidenced:
        contradictory = True
    if contradictory:
        label = ClaimLabel.CONTRADICTED
        explanation = "The closest passage conflicts with the claim's negation or reported value."
    elif best.similarity < 0.35:
        label = ClaimLabel.INSUFFICIENT_EVIDENCE if claim_words & QUALIFIERS else ClaimLabel.UNSUPPORTED
        explanation = "No sufficiently similar passage was found in the supplied paper."
    elif best.similarity < 0.65:
        label = ClaimLabel.PARTIALLY_SUPPORTED
        explanation = "The paper overlaps with the claim but does not support its full wording."
    else:
        label = ClaimLabel.SUPPORTED
        explanation = "The claim closely matches the supplied passage."

    if claim_words & UNIVERSAL and not evidence_words & UNIVERSAL:
        failures.append("OVERSTATED_CONCLUSION")
        if label == ClaimLabel.SUPPORTED:
            label = ClaimLabel.PARTIALLY_SUPPORTED
    if claim_words & CAUSAL and evidence_words & CORRELATIONAL and not evidence_words & CAUSAL:
        failures.append("CORRELATION_AS_CAUSATION")
        label = ClaimLabel.PARTIALLY_SUPPORTED
    if any(term in claim.lower() for term in ("children", "women", "men", "elderly", "patients")) and not content_words(claim) <= content_words(paper_text):
        failures.append("OUTSIDE_STUDIED_SCOPE")
    if best.section == "LIMITATIONS" or (claim_words & UNIVERSAL and not claim_words & QUALIFIERS):
        failures.append("MISSING_QUALIFICATION")
    if label == ClaimLabel.UNSUPPORTED:
        failures.append("UNSUPPORTED_CLAIM")
    return ClaimResult(claim, label, evidence, explanation, list(dict.fromkeys(failures)))


def section_counts(claims: list[ClaimResult]) -> Counter[str]:
    return Counter(claim.evidence[0].section for claim in claims if claim.evidence)
