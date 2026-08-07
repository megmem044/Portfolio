"""Validate information submitted for an AnswerTrust evaluation."""

from src.config import MAX_INPUT_CHARS, MIN_MEANINGFUL_CHARS
from src.models import EvaluationInput


def _has_meaningful_content(text: str) -> bool:
    """Return True when text contains enough letters or numbers."""
    meaningful_characters = sum(
        character.isalnum() for character in text
    )
    return meaningful_characters >= MIN_MEANINGFUL_CHARS


def validate_input(evaluation_input: EvaluationInput) -> list[str]:
    """Check the user's input and return friendly messages for any problems."""
    errors: list[str] = []

    if not evaluation_input.question.strip():
        errors.append("Enter the question being answered.")
    elif not _has_meaningful_content(evaluation_input.question):
        errors.append(
            "Enter a meaningful question using letters or numbers."
        )

    if not evaluation_input.reference.strip():
        errors.append(
            "Add the reference information used to support the answer."
        )
    elif not _has_meaningful_content(evaluation_input.reference):
        errors.append(
            "Add meaningful reference information using letters or numbers."
        )

    if not evaluation_input.answer.strip():
        errors.append(
            "Enter the AI-generated answer you want to evaluate."
        )
    elif not _has_meaningful_content(evaluation_input.answer):
        errors.append(
            "Enter a meaningful answer using letters or numbers."
        )

    if len(evaluation_input.question) > MAX_INPUT_CHARS:
        errors.append(
            f"Keep the question under {MAX_INPUT_CHARS:,} characters."
        )

    if len(evaluation_input.reference) > MAX_INPUT_CHARS:
        errors.append(
            f"Keep the reference information under "
            f"{MAX_INPUT_CHARS:,} characters."
        )

    if len(evaluation_input.answer) > MAX_INPUT_CHARS:
        errors.append(
            f"Keep the AI-generated answer under "
            f"{MAX_INPUT_CHARS:,} characters."
        )

    return errors
