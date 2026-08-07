"""Small deterministic evaluator for AnswerTrust."""

from __future__ import annotations

from src.models import Decision, EvaluationInput
from src.validation import validate_input


def evaluate_answer(evaluation_input: EvaluationInput) -> Decision:
    """Return a simple publish/review/reject decision for the input."""
    errors = validate_input(evaluation_input)
    if errors:
        return Decision.REJECT

    if evaluation_input.answer.lower().strip() == evaluation_input.reference.lower().strip():
        return Decision.PUBLISH

    if evaluation_input.answer.lower().strip() in evaluation_input.reference.lower().strip():
        return Decision.REVIEW

    return Decision.REJECT
