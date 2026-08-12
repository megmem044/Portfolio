"""Retry rules for transient AnswerTrust evaluation failures."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.models import FailureType


DEFAULT_RETRYABLE_FAILURES = frozenset(
    {
        FailureType.MODEL_TIMEOUT,
        FailureType.EVALUATION_ERROR,
    }
)


@dataclass(frozen=True)
class RetryPolicy:
    """Decide whether another evaluation attempt should be made."""

    max_attempts: int = 2
    retryable_failures: frozenset[FailureType] = field(
        default_factory=lambda: DEFAULT_RETRYABLE_FAILURES
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

    def should_retry(
        self,
        failure_type: FailureType,
        completed_attempts: int,
    ) -> bool:
        """Return whether a failed attempt qualifies for another try."""
        return (
            failure_type in self.retryable_failures
            and completed_attempts < self.max_attempts
        )


DEFAULT_RETRY_POLICY = RetryPolicy()
