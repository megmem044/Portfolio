"""Service boundary for deciding how well evidence supports a claim."""

from __future__ import annotations

from typing import Protocol

from src.academic import evaluate_claim
from src.models import ClaimResult, Evidence
from src.nli import NLIClassifier, apply_nli


class ClaimClassifier(Protocol):
    """Anything that can classify a claim using retrieved evidence."""

    def classify(self, claim: str, evidence: list[Evidence], paper_text: str) -> ClaimResult: ...


class AcademicClaimClassifier:
    """Use the existing rules and optional NLI model to classify a claim."""

    def __init__(self, nli_classifier: NLIClassifier | None = None) -> None:
        self.nli_classifier = nli_classifier

    def classify(self, claim: str, evidence: list[Evidence], paper_text: str) -> ClaimResult:
        result = evaluate_claim(claim, evidence, paper_text)
        if self.nli_classifier is not None and evidence:
            try:
                return apply_nli(result, self.nli_classifier.predict(evidence[0].passage, claim))
            except Exception:
                pass
        return result
