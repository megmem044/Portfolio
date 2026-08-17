"""Background evaluation job executed by an RQ worker."""

from src.db import create_database_engine, create_session_factory, session_scope
from src.evaluation_repository import EvaluationRepository
from src.evaluator import evaluate_answer
from src.observability import logger, metrics


def process_evaluation(evaluation_id: str) -> None:
    factory = create_session_factory(create_database_engine())
    error: Exception | None = None
    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        record = repository.start_attempt(evaluation_id)
        if record.state in {"COMPLETED", "REVIEW_REQUIRED", "APPROVED", "REJECTED"}:
            return
        try:
            result = evaluate_answer(repository.evaluation_input(evaluation_id))
            result.evaluation_id = evaluation_id
            repository.save_result(result)
            metrics.increment("evaluations_total")
            metrics.increment(f"evaluation_outcome_{result.final_decision.value.lower()}")
            logger.info("evaluation_completed", extra={"evaluation_id": evaluation_id, "outcome": result.final_decision.value, "duration_ms": result.total_latency_ms})
        except Exception as problem:
            error = problem
            repository.save_failure(evaluation_id, str(problem), final=record.attempt_count >= 3)
            logger.error("evaluation_attempt_failed", extra={"evaluation_id": evaluation_id, "outcome": "FAILED"})
    if error is not None:
        raise error
