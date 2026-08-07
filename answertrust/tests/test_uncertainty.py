from src.uncertainty import evaluate_uncertainty


def test_supported_answer_scores_high():
    result = evaluate_uncertainty(
        "Paris is the capital of France.",
        "Paris is the capital of France.",
    )

    assert result.name == "Uncertainty handling"
    assert result.score >= 80
    assert result.concerns == []


def test_unsupported_certainty_scores_low():
    result = evaluate_uncertainty(
        "The study is preliminary.",
        "The treatment will definitely cure everyone.",
    )

    assert result.score < 50
    assert result.concerns


def test_cautious_language_handles_limited_evidence():
    result = evaluate_uncertainty(
        "The study is preliminary.",
        "The evidence may be insufficient to draw a conclusion.",
    )

    assert result.score >= 80
    assert result.concerns == []


def test_insufficient_information_phrase_handles_limited_evidence():
    result = evaluate_uncertainty(
        "The notice contains no vote totals.",
        "The result cannot be determined from the supplied reference.",
    )

    assert result.score >= 80
    assert result.concerns == []
