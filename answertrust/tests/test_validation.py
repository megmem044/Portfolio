from src.models import EvaluationInput
from src.validation import validate_input


def test_validate_input_rejects_missing_question_and_answer():
    errors = validate_input(
        EvaluationInput(
            question="   ",
            reference="France's capital is Paris.",
            answer="",
        )
    )

    assert any("question" in error.lower() for error in errors)
    assert any("answer" in error.lower() for error in errors)


def test_validate_input_accepts_meaningful_text():
    errors = validate_input(
        EvaluationInput(
            question="What is the capital of France?",
            reference="France's capital is Paris.",
            answer="Paris is the capital of France.",
        )
    )

    assert errors == []


def test_validate_input_rejects_meaningless_text():
    errors = validate_input(
        EvaluationInput(
            question="!!!",
            reference="France's capital is Paris.",
            answer="???",
        )
    )

    assert any("question" in error.lower() for error in errors)
    assert any("answer" in error.lower() for error in errors)


def test_validate_input_rejects_oversized_text():
    long_text = "a" * 5001
    errors = validate_input(
        EvaluationInput(
            question=long_text,
            reference="France's capital is Paris.",
            answer="Paris is the capital of France.",
        )
    )

    assert any("question" in error.lower() for error in errors)
