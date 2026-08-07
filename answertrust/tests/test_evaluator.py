from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput


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
