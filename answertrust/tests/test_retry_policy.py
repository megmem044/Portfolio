"""Tests for AnswerTrust retry-policy decisions."""

import pytest

from src.models import FailureType
from src.retry_policy import DEFAULT_RETRY_POLICY, RetryPolicy


@pytest.mark.parametrize(
    "failure_type",
    [FailureType.MODEL_TIMEOUT, FailureType.EVALUATION_ERROR],
)
def test_transient_failure_is_retried(failure_type):
    assert DEFAULT_RETRY_POLICY.should_retry(failure_type, 1) is True


@pytest.mark.parametrize(
    "failure_type",
    [
        FailureType.MODEL_UNAVAILABLE,
        FailureType.INVALID_OUTPUT,
        FailureType.LOW_CONFIDENCE,
        FailureType.INSUFFICIENT_SUPPORT,
    ],
)
def test_non_transient_failure_is_not_retried(failure_type):
    assert DEFAULT_RETRY_POLICY.should_retry(failure_type, 1) is False


def test_failure_is_not_retried_after_maximum_attempts():
    assert (
        DEFAULT_RETRY_POLICY.should_retry(
            FailureType.MODEL_TIMEOUT,
            2,
        )
        is False
    )


def test_custom_policy_supports_additional_attempts():
    policy = RetryPolicy(max_attempts=3)

    assert policy.should_retry(FailureType.MODEL_TIMEOUT, 2) is True
    assert policy.should_retry(FailureType.MODEL_TIMEOUT, 3) is False


def test_policy_requires_at_least_one_attempt():
    with pytest.raises(ValueError, match="at least 1"):
        RetryPolicy(max_attempts=0)
