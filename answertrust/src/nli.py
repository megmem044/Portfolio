"""Optional natural-language inference for evidence/claim classification."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
import warnings
from pathlib import Path

from src.config import MODEL_CACHE_DIR, configure_model_cache
from src.models import ClaimLabel, ClaimResult

LABELS = ("contradiction", "entailment", "neutral")


@dataclass(frozen=True)
class NLIPrediction:
    label: str
    confidence: float


class NLIClassifier:
    """Classify whether an evidence passage entails or contradicts a claim."""

    def __init__(
        self,
        model_name: str = "cross-encoder/nli-MiniLM2-L6-H768",
        model: object | None = None,
        allow_download: bool = False,
    ) -> None:
        if model is None:
            configure_model_cache()
            from sentence_transformers import CrossEncoder

            model_source: str | Path = model_name
            if not allow_download:
                cached_root = MODEL_CACHE_DIR / (
                    "models--" + model_name.replace("/", "--")
                ) / "snapshots"
                snapshots = sorted(cached_root.glob("*"))
                if snapshots:
                    model_source = snapshots[-1]

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*clean_up_tokenization_spaces.*",
                    category=FutureWarning,
                )
                warnings.filterwarnings(
                    "ignore",
                    message=".*cache_dir.*deprecated.*",
                )
                model_kwargs = {"local_files_only": not allow_download}
                if allow_download:
                    model_kwargs["cache_folder"] = str(MODEL_CACHE_DIR)
                model = CrossEncoder(str(model_source), **model_kwargs)
        self.model = model
        self.model_name = model_name

    def predict(self, evidence: str, claim: str) -> NLIPrediction:
        scores = self.model.predict([(evidence, claim)])[0]
        probabilities = _softmax([float(score) for score in scores])
        index = max(range(len(probabilities)), key=probabilities.__getitem__)
        return NLIPrediction(LABELS[index], round(probabilities[index], 4))


def _softmax(scores: list[float]) -> list[float]:
    maximum = max(scores)
    exponentials = [exp(score - maximum) for score in scores]
    total = sum(exponentials)
    return [value / total for value in exponentials]


def apply_nli(
    result: ClaimResult,
    prediction: NLIPrediction,
    threshold: float = 0.65,
) -> ClaimResult:
    """Apply only confident NLI outcomes while retaining safety checks."""
    result.nli_label = prediction.label.upper()
    result.nli_confidence = prediction.confidence
    if prediction.confidence < threshold:
        return result
    if prediction.label == "contradiction":
        nli_only = result.label != ClaimLabel.CONTRADICTED
        result.label = ClaimLabel.CONTRADICTED
        if nli_only:
            if "NLI_ONLY_CONTRADICTION" not in result.failure_types:
                result.failure_types.append("NLI_ONLY_CONTRADICTION")
            result.explanation = (
                "The NLI model found a contradiction that the deterministic "
                "checks did not confirm; human review is required."
            )
        else:
            result.explanation = "The NLI model found that the evidence contradicts this claim."
    elif prediction.label == "entailment":
        result.label = (
            ClaimLabel.PARTIALLY_SUPPORTED
            if result.failure_types
            else ClaimLabel.SUPPORTED
        )
        result.explanation = "The NLI model found that the evidence entails this claim."
    elif prediction.label == "neutral" and result.label != ClaimLabel.CONTRADICTED:
        result.label = ClaimLabel.UNSUPPORTED
        if "UNSUPPORTED_CLAIM" not in result.failure_types:
            result.failure_types.append("UNSUPPORTED_CLAIM")
        result.explanation = "The NLI model found no entailment or contradiction in the evidence."
    return result
