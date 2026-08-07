from src.clarity import evaluate_clarity


def test_clear_answer_scores_high():
    result = evaluate_clarity(
        "Paris is the capital of France."
    )

    assert result.name == "Clarity"
    assert result.score >= 80
    assert result.concerns == []


def test_excessive_punctuation_reduces_clarity():
    result = evaluate_clarity(
        "Paris is definitely the answer!!!!!"
    )

    assert result.score < 100
    assert result.concerns


def test_long_answer_reduces_clarity():
    result = evaluate_clarity(
        "word " * 250
    )

    assert result.score < 80
    assert result.concerns
