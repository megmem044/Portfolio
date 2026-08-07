from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput, TransformerResult


def test_evaluate_answer_publishes_exact_match():
    result = evaluate_answer(
        EvaluationInput(
            question="What is the capital of France?",
            reference="Paris",
            answer="Paris",
        )
    )

    assert result.final_decision == Decision.PUBLISH
    assert len(result.dimension_scores) == 5


def test_evaluate_answer_reviews_partial_match():
    result = evaluate_answer(
        EvaluationInput(
            question="What is the capital of France?",
            reference="France's capital is Paris.",
            answer="Paris",
        )
    )

    assert result.final_decision == Decision.REVIEW
    assert any(
        score.name == "Relevance"
        for score in result.dimension_scores
    )


def test_evaluate_answer_rejects_invalid_input():
    result = evaluate_answer(
        EvaluationInput(
            question="   ",
            reference="France's capital is Paris.",
            answer="",
        )
    )

    assert result.final_decision == Decision.REJECT
    assert result.dimension_scores[0].name == "Validation"


class FakeTransformer:
    def __init__(self, result: TransformerResult):
        self.result = result

    def evaluate(self, evaluation_input, prompt_version):
        return self.result


def test_transformer_explanation_does_not_override_official_decision():
    transformer = FakeTransformer(
        TransformerResult(
            explanation="The model recommends rejection.",
            suggested_decision=Decision.REJECT,
            prompt_version="safety",
            model_name="test-model",
            status="generated",
            latency_ms=12,
        )
    )
    result = evaluate_answer(
        EvaluationInput(
            question="What is the capital of France?",
            reference="Paris",
            answer="Paris",
            prompt_version="safety",
        ),
        transformer_evaluator=transformer,
    )

    assert result.final_decision == Decision.PUBLISH
    assert result.explanation == "The model recommends rejection."
    assert result.model_status == "generated"
    assert result.transformer_latency_ms == 12


def test_unavailable_transformer_falls_back_to_deterministic_explanation():
    transformer = FakeTransformer(
        TransformerResult(
            explanation="",
            suggested_decision=None,
            prompt_version="baseline",
            model_name="test-model",
            status="unavailable",
            latency_ms=3,
        )
    )
    result = evaluate_answer(
        EvaluationInput(
            question="What is the capital of France?",
            reference="Paris",
            answer="Paris",
        ),
        transformer_evaluator=transformer,
    )

    assert result.final_decision == Decision.PUBLISH
    assert result.explanation
    assert result.model_status == "unavailable"
    assert result.transformer_latency_ms == 3
