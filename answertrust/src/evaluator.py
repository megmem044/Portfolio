"""Research-grounded claim evaluation pipeline."""

from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from src.academic import content_words, evaluate_claim, extract_claims, match_evidence, split_sections
from src.decision_engine import make_decision
from src.models import ClaimLabel, DimensionScore, EvaluationInput, EvaluationResult


def evaluate_answer(evaluation_input: EvaluationInput, **_: object) -> EvaluationResult:
    started = perf_counter()
    if min(map(len, (evaluation_input.question.strip(), evaluation_input.paper_text.strip(), evaluation_input.answer.strip()))) < 3:
        raise ValueError("Question, paper text, and answer are required.")
    sections = split_sections(evaluation_input.paper_text)
    extracted = extract_claims(evaluation_input.answer)
    if not extracted:
        raise ValueError("The answer contains no evaluable claims.")
    claim_results = [evaluate_claim(claim, match_evidence(claim, sections), evaluation_input.paper_text) for claim in extracted]
    supported = sum(item.label == ClaimLabel.SUPPORTED for item in claim_results)
    support_score = round(100 * supported / len(claim_results))
    question_terms = content_words(evaluation_input.question)
    answer_terms = content_words(evaluation_input.answer)
    relevance = round(100 * len(question_terms & answer_terms) / len(question_terms)) if question_terms else 100
    paper_terms = content_words(evaluation_input.paper_text)
    completeness = round(100 * len(question_terms & answer_terms & paper_terms) / len(question_terms & paper_terms)) if question_terms & paper_terms else support_score
    qualified = sum(not item.failure_types or "MISSING_QUALIFICATION" not in item.failure_types for item in claim_results)
    uncertainty = round(100 * qualified / len(claim_results))
    dimensions = [
        DimensionScore("Claim support", support_score, f"{supported} of {len(claim_results)} claims were fully supported.", [item.explanation for item in claim_results if item.label != ClaimLabel.SUPPORTED]),
        DimensionScore("Relevance", relevance, "Overlap between the research question and answer.", [] if relevance >= 50 else ["The answer may not address the research question."]),
        DimensionScore("Completeness", completeness, "Coverage of question concepts grounded in the paper.", [] if completeness >= 75 else ["The answer may omit part of the question."]),
        DimensionScore("Uncertainty", uncertainty, "Checks for qualifications and bounded conclusions.", [failure for item in claim_results for failure in item.failure_types]),
    ]
    decision = make_decision(claim_results, completeness, relevance)
    overall = round(sum(item.score for item in dimensions) / len(dimensions))
    concerns = [f"{item.label.value}: {item.claim}" for item in claim_results if item.label != ClaimLabel.SUPPORTED]
    return EvaluationResult(
        evaluation_id=str(uuid4()), timestamp=datetime.now(timezone.utc), overall_score=overall,
        final_decision=decision, claim_results=claim_results, dimension_scores=dimensions,
        main_concern=concerns[0] if concerns else "No material concern detected.",
        explanation=f"Evaluated {len(claim_results)} claims against {len(sections)} paper sections.",
        recommended_action={"PUBLISH":"Publish with the cited evidence.","REVIEW":"A human should inspect flagged claims and qualifications.","REJECT":"Do not publish without correcting contradicted or unsupported claims."}[decision.value],
        total_latency_ms=round((perf_counter()-started)*1000), deterministic_latency_ms=round((perf_counter()-started)*1000),
    )
