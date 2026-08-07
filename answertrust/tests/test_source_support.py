from src.source_support import evaluate_source_support


def test_exact_match_receives_full_support():
    result = evaluate_source_support("Paris", "Paris")

    assert result.name == "Source support"
    assert result.score == 100
    assert result.concerns == []


def test_answer_inside_reference_is_supported():
    result = evaluate_source_support(
        "France's capital is Paris.",
        "Paris",
    )

    assert result.score == 80


def test_unsupported_answer_receives_low_score():
    result = evaluate_source_support(
        "France's capital is Paris.",
        "Berlin is the capital of France.",
    )

    assert result.score < 50
    assert result.concerns