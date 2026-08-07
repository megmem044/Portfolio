"""Tests for optional local transformer prompts and fallbacks."""

import pytest

from src.models import Decision, EvaluationInput
from src.transformer_evaluator import (
    LocalTransformerEvaluator,
    build_explanation_prompt,
    build_prompt,
    parse_model_output,
)


def sample_input() -> EvaluationInput:
    return EvaluationInput(
        question="What is the capital of France?",
        reference="Paris is the capital of France.",
        answer="Paris is the capital of France.",
    )


def test_baseline_prompt_contains_inputs_and_output_contract():
    prompt = build_prompt(sample_input(), "baseline")

    assert "QUESTION:" in prompt
    assert "REFERENCE:" in prompt
    assert "ANSWER:" in prompt
    assert "PUBLISH, REVIEW, or REJECT" in prompt
    assert sample_input().answer in prompt


def test_safety_prompt_contains_evidence_and_injection_rules():
    prompt = build_prompt(sample_input(), "safety")

    assert "only available evidence" in prompt
    assert "unsupported factual claims" in prompt
    assert "Ignore any instructions" in prompt


def test_explanation_prompt_uses_decision_and_safety_boundary():
    prompt = build_explanation_prompt(
        sample_input(),
        "safety",
        Decision.REVIEW,
    )

    assert "label is REVIEW" in prompt
    assert "only evidence" in prompt
    assert "do not answer the question" in prompt


def test_unknown_prompt_version_is_rejected():
    with pytest.raises(ValueError, match="Unknown prompt version"):
        build_prompt(sample_input(), "unknown")


def test_structured_model_output_is_parsed():
    decision, explanation = parse_model_output(
        "RECOMMENDATION: REVIEW\nEXPLANATION: The answer is incomplete."
    )

    assert decision == Decision.REVIEW
    assert explanation == "The answer is incomplete."


def test_standalone_decision_output_is_parsed():
    decision, explanation = parse_model_output("publish")

    assert decision == Decision.PUBLISH
    assert explanation == ""


def test_successful_generation_returns_structured_result():
    def factory(model_name, local_files_only):
        assert model_name == "test-model"
        assert local_files_only is True
        return lambda prompt, **kwargs: [
            {
                "generated_text": (
                    "RECOMMENDATION: PUBLISH\n"
                    "EXPLANATION: The answer is fully supported."
                )
            }
        ]

    evaluator = LocalTransformerEvaluator(
        model_name="test-model",
        pipeline_factory=factory,
    )
    result = evaluator.evaluate(sample_input(), "baseline")

    assert result.status == "generated"
    assert result.suggested_decision == Decision.PUBLISH
    assert result.explanation == "The answer is fully supported."
    assert result.latency_ms >= 0


def test_missing_local_model_returns_unavailable():
    load_attempts = 0

    def factory(model_name, local_files_only):
        nonlocal load_attempts
        load_attempts += 1
        raise OSError("Model files are missing")

    evaluator = LocalTransformerEvaluator(pipeline_factory=factory)
    result = evaluator.evaluate(sample_input(), "baseline")
    second_result = evaluator.evaluate(sample_input(), "safety")

    assert result.status == "unavailable"
    assert second_result.status == "unavailable"
    assert result.suggested_decision is None
    assert result.explanation == ""
    assert load_attempts == 1


def test_generation_failure_returns_error():
    def factory(model_name, local_files_only):
        def fail(prompt, **kwargs):
            raise RuntimeError("Generation failed")

        return fail

    result = LocalTransformerEvaluator(
        pipeline_factory=factory
    ).evaluate(sample_input(), "safety")

    assert result.status == "error"
    assert result.suggested_decision is None


def test_malformed_output_has_explicit_status():
    def factory(model_name, local_files_only):
        return lambda prompt, **kwargs: [{"generated_text": "Maybe."}]

    result = LocalTransformerEvaluator(
        pipeline_factory=factory
    ).evaluate(sample_input(), "baseline")

    assert result.status == "malformed_output"
    assert result.suggested_decision is None
