from src.completeness import evaluate_completeness


def test_short_direct_answer_can_be_complete():
    result = evaluate_completeness(
        "What is the capital of France?",
        "Paris",
        "Paris",
    )

    assert result.score >= 80
    assert result.concerns == []


def test_complete_multipart_answer_scores_high():
    result = evaluate_completeness(
        "Name the capital and official language of France.",
        "The capital is Paris and the official language is French.",
        "The capital is Paris and the official language is French.",
    )

    assert result.score >= 80


def test_partial_multipart_answer_has_concern():
    result = evaluate_completeness(
        "Name the capital and official language of France.",
        "The capital is Paris and the official language is French.",
        "The capital is Paris.",
    )

    assert result.score < 80
    assert result.concerns