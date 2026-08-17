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
QUANTITY_WORDS = {
    "all": (1.0, 1.0), "every": (1.0, 1.0), "none": (0.0, 0.0),
    "most": (0.5, 1.0), "majority": (0.5, 1.0),
}
OPPOSITES = (
    ({"high", "higher", "large", "larger", "increased", "increase"}, {"low", "lower", "small", "smaller", "reduced", "decreased"}),
    ({"significant", "significantly"}, {"nonsignificant", "insignificant"}),
    ({"open", "open-source"}, {"closed", "closed-source"}),
)
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


def _numeric_contradiction(claim: str, passage: str) -> bool:
    """Catch transparent percentage, comparison, and significance reversals."""
    claim_words, passage_words = set(words(claim)), set(words(passage))
    percentages = [float(value) / 100 for value in re.findall(r"(\d+(?:\.\d+)?)\s*%", passage)]
    for word, (lower, upper) in QUANTITY_WORDS.items():
        if word in claim_words and percentages and not any(lower <= value <= upper for value in percentages):
            return True

    for left, right in OPPOSITES:
        if (claim_words & left and passage_words & right) or (claim_words & right and passage_words & left):
            return True

    if claim_words & {"significant", "significantly"}:
        p_values = [float(value) for value in re.findall(r"\bp\s*[=<>]\s*(0?\.\d+)", passage.lower())]
        if any(value >= 0.05 for value in p_values) or "not significantly" in passage.lower():
            return True

    comparison = re.search(r"(.+?)\b(larger|higher|greater|smaller|lower|less)\s+than\s+(.+)", claim.lower())
    if comparison:
        left_terms, direction, right_terms = comparison.groups()
        clauses = re.split(r"[;,]|\band\b", passage.lower())
        def value_for(terms: str) -> float | None:
            target = content_words(terms)
            ranked = sorted(clauses, key=lambda clause: len(target & content_words(clause)), reverse=True)
            match = re.search(r"\b\d+(?:\.\d+)?\b", ranked[0]) if ranked and target & content_words(ranked[0]) else None
            return float(match.group()) if match else None
        left_value, right_value = value_for(left_terms), value_for(right_terms)
        if left_value is not None and right_value is not None:
            expects_more = direction in {"larger", "higher", "greater"}
            if (expects_more and left_value <= right_value) or (not expects_more and left_value >= right_value):
                return True
    return False


def _numbers_are_compatible(claim: str, passage: str, claimed: set[str], evidenced: set[str]) -> bool:
    if claimed <= evidenced:
        return True
    claim_values = [float(value.rstrip("%")) for value in claimed]
    evidence_values = [float(value.rstrip("%")) for value in evidenced]
    if len(claim_values) == 1 and len(evidence_values) >= 2:
        differences = {round(abs(left-right), 6) for left in evidence_values for right in evidence_values}
        if round(claim_values[0], 6) in differences:
            return True
    threshold = re.search(r"\bp\s*<\s*(0?\.\d+)", claim.lower())
    observed = re.search(r"\bp\s*=\s*(0?\.\d+)", passage.lower())
    return bool(threshold and observed and float(observed.group(1)) < float(threshold.group(1)))


def evaluate_claim(claim: str, evidence: list[Evidence], paper_text: str) -> ClaimResult:
    best = evidence[0] if evidence else Evidence("UNKNOWN", "", 0.0)
    claim_words, evidence_words = set(words(claim)), set(words(best.passage))
    failures: list[str] = []
    contradictory = best.similarity >= 0.32 and _has_negation(claim) != _has_negation(best.passage)
    numbers_claimed = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", claim))
    numbers_evidenced = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", best.passage))
    if numbers_claimed and numbers_evidenced and not _numbers_are_compatible(claim, best.passage, numbers_claimed, numbers_evidenced):
        contradictory = True
    if _numeric_contradiction(claim, best.passage):
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

    if label == ClaimLabel.PARTIALLY_SUPPORTED and numbers_claimed and _numbers_are_compatible(claim, best.passage, numbers_claimed, numbers_evidenced) and best.similarity >= 0.45:
        label = ClaimLabel.SUPPORTED
        explanation = "The claim preserves the reported value and its surrounding result."

    if claim_words & UNIVERSAL and not evidence_words & UNIVERSAL:
        failures.append("OVERSTATED_CONCLUSION")
        if label == ClaimLabel.SUPPORTED:
            label = ClaimLabel.PARTIALLY_SUPPORTED
    if claim_words & CAUSAL and evidence_words & CORRELATIONAL and not evidence_words & CAUSAL:
        failures.append("CORRELATION_AS_CAUSATION")
        label = ClaimLabel.PARTIALLY_SUPPORTED
    population_terms = {"children", "women", "men", "elderly", "patients"}
    populations_outside_paper = (
        claim_words & population_terms
    ) - content_words(paper_text)
    if populations_outside_paper:
        failures.append("OUTSIDE_STUDIED_SCOPE")
    if best.section == "LIMITATIONS" or (claim_words & UNIVERSAL and not claim_words & QUALIFIERS):
        failures.append("MISSING_QUALIFICATION")
    if label == ClaimLabel.UNSUPPORTED:
        failures.append("UNSUPPORTED_CLAIM")
    return ClaimResult(claim, label, evidence, explanation, list(dict.fromkeys(failures)))


def section_counts(claims: list[ClaimResult]) -> Counter[str]:
    return Counter(claim.evidence[0].section for claim in claims if claim.evidence)
