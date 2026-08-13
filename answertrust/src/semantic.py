"""Optional sentence-embedding support for semantic evidence matching."""

from __future__ import annotations

from collections.abc import Sequence
from math import sqrt
from typing import Protocol
import warnings

from src.config import MODEL_CACHE_DIR


class Encoder(Protocol):
    """Minimal interface shared by SentenceTransformer and test doubles."""

    def encode(self, sentences: str | Sequence[str], **kwargs: object): ...


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity without requiring NumPy in application code."""
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


class SemanticMatcher:
    """Rank passages with a locally loaded sentence-transformer model."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        encoder: Encoder | None = None,
        allow_download: bool = False,
    ) -> None:
        if encoder is None:
            from sentence_transformers import SentenceTransformer

            MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*clean_up_tokenization_spaces.*",
                    category=FutureWarning,
                )
                encoder = SentenceTransformer(
                    model_name,
                    cache_folder=str(MODEL_CACHE_DIR),
                    local_files_only=not allow_download,
                )
        self.encoder = encoder
        self.model_name = model_name

    def similarities(self, claim: str, passages: Sequence[str]) -> list[float]:
        """Calculate a semantic similarity score for every passage."""
        if not passages:
            return []
        embeddings = self.encoder.encode(
            [claim, *passages],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        claim_embedding = embeddings[0]
        return [
            max(0.0, min(1.0, float(cosine_similarity(claim_embedding, item))))
            for item in embeddings[1:]
        ]
