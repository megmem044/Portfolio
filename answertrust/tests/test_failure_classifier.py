"""Tests for AnswerTrust's failure taxonomy classification."""

from dataclasses import replace

import pytest

from src.evaluator import evaluate_answer
from src.failure_classifier import classify_exception, classify_result
from src.models import (
    Decision,
    DimensionScore,
    EvaluationInput,
    FailureType,
)


def supported_result():
    evaluation_input = EvaluationInput(
        question="What is the capital of France?",
        reference="Paris is the capital of France.",
        answer="Paris is the capital of France.",
    )
    return evaluate_answer(evaluation_input)


def test_successful_result_has_no_failure_classification():
    assert classify_result(supported_result()) is None


def test_validation_result_is_invalid_output():
    result = evaluate_answer(EvaluationInput("", "", ""))

    assert classify_result(result) == FailureType.INVALID_OUTPUT


@pytest.mark.parametrize(
    ("model_status", "expected"),
    [
        ("unavailable", FailureType.MODEL_UNAVAILABLE),
        ("malformed_output", FailureType.INVALID_OUTPUT),
        ("error", FailureType.EVALUATION_ERROR),
    ],
)
def test_model_status_is_classified(model_status, expected):
    result = replace(supported_result(), model_status=model_status)

    assert classify_result(result) == expected


def test_review_decision_is_low_confidence():
    result = replace(
        supported_result(),
        final_decision=Decision.REVIEW,
    )

    assert classify_result(result) == FailureType.LOW_CONFIDENCE


def test_rejected_answer_with_weak_support_is_insufficient_support():
    result = replace(
        supported_result(),
        final_decision=Decision.REJECT,
        dimension_scores=[
            DimensionScore(
                name="Source support",
                score=25,
                explanation="The answer is not supported.",
                concerns=["Unsupported claim."],
            )
        ],
    )

    assert classify_result(result) == FailureType.INSUFFICIENT_SUPPORT


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (TimeoutError("deadline exceeded"), FailureType.MODEL_TIMEOUT),
        (OSError("model missing"), FailureType.MODEL_UNAVAILABLE),
        (FileNotFoundError("weights missing"), FailureType.MODEL_UNAVAILABLE),
        (ValueError("bad output"), FailureType.INVALID_OUTPUT),
        (RuntimeError("unexpected"), FailureType.EVALUATION_ERROR),
    ],
)
def test_exception_is_classified(error, expected):
    assert classify_exception(error) == expected
