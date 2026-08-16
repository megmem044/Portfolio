"""Complete research-grounded evaluation pipeline."""

from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from src.academic import content_words, extract_claims, split_sections
from src.classification import ClaimClassifier
from src.decision_engine import make_decision
from src.models import ClaimLabel, DimensionScore, EvaluationInput, EvaluationResult
from src.retrieval import EvidenceRetriever


class EvaluationPipeline:
    """Run evidence retrieval and claim classification from start to finish."""

    def __init__(self, evidence_retriever: EvidenceRetriever, claim_classifier: ClaimClassifier) -> None:
        self.evidence_retriever = evidence_retriever
        self.claim_classifier = claim_classifier

    def evaluate(self, item: EvaluationInput) -> EvaluationResult:
        started = perf_counter()
        if min(map(len, (item.question.strip(), item.paper_text.strip(), item.answer.strip()))) < 3:
            raise ValueError("Question, paper text, and answer are required.")
        sections = split_sections(item.paper_text)
        claims = extract_claims(item.answer)
        if not claims:
            raise ValueError("The answer contains no evaluable claims.")
        results = []
        for claim in claims:
            evidence = self.evidence_retriever.retrieve(claim, sections)
            results.append(self.claim_classifier.classify(claim, evidence, item.paper_text))
        supported = sum(result.label == ClaimLabel.SUPPORTED for result in results)
        support_score = round(100 * supported / len(results))
        question_terms, answer_terms = content_words(item.question), content_words(item.answer)
        relevance = round(100 * len(question_terms & answer_terms) / len(question_terms)) if question_terms else 100
        paper_terms = content_words(item.paper_text)
        grounded_terms = question_terms & paper_terms
        completeness = round(100 * len(question_terms & answer_terms & paper_terms) / len(grounded_terms)) if grounded_terms else support_score
        qualified = sum("MISSING_QUALIFICATION" not in result.failure_types for result in results)
        uncertainty = round(100 * qualified / len(results))
        dimensions = [
            DimensionScore("Claim support", support_score, f"{supported} of {len(results)} claims were fully supported.", [result.explanation for result in results if result.label != ClaimLabel.SUPPORTED]),
            DimensionScore("Relevance", relevance, "Overlap between the research question and answer.", [] if relevance >= 50 else ["The answer may not address the research question."]),
            DimensionScore("Completeness", completeness, "Coverage of question concepts grounded in the paper.", [] if completeness >= 75 else ["The answer may omit part of the question."]),
            DimensionScore("Uncertainty", uncertainty, "Checks for qualifications and bounded conclusions.", [failure for result in results for failure in result.failure_types]),
        ]
        decision = make_decision(results, completeness, relevance)
        concerns = [f"{result.label.value}: {result.claim}" for result in results if result.label != ClaimLabel.SUPPORTED]
        elapsed = round((perf_counter() - started) * 1000)
        return EvaluationResult(
            evaluation_id=str(uuid4()), timestamp=datetime.now(timezone.utc),
            overall_score=round(sum(score.score for score in dimensions) / len(dimensions)),
            final_decision=decision, claim_results=results, dimension_scores=dimensions,
            main_concern=concerns[0] if concerns else "No material concern detected.",
            explanation=f"Evaluated {len(results)} claims against {len(sections)} paper sections.",
            recommended_action={"PUBLISH":"Publish with the cited evidence.","REVIEW":"A human should inspect flagged claims and qualifications.","REJECT":"Do not publish without correcting contradicted or unsupported claims."}[decision.value],
            total_latency_ms=elapsed, deterministic_latency_ms=elapsed,
        )
