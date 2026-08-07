from src.relevance import evaluate_relevance


def test_supported_short_answer_is_relevant():
    result = evaluate_relevance(
        "What is the capital of France?",
        "Paris",
        "Paris",
    )

    assert result.name == "Relevance"
    assert result.score >= 70
    assert result.concerns == []


def test_answer_with_question_overlap_is_relevant():
    result = evaluate_relevance(
        "Why do plants need sunlight?",
        "Plants use sunlight during photosynthesis.",
        "Plants need sunlight for photosynthesis.",
    )

    assert result.score >= 70


def test_unrelated_answer_has_low_relevance():
    result = evaluate_relevance(
        "What is the capital of France?",
        "France's capital is Paris.",
        "Whales live in the ocean.",
    )

    assert result.score < 50
    assert result.concerns