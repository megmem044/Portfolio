"""Persistent evaluation execution with automatic retry."""

from pathlib import Path
from typing import Callable

from src import database
from src.evaluator import evaluate_answer
from src.models import Decision, EvaluationInput, EvaluationResult, FailureType, RunState
from src.retry_policy import DEFAULT_RETRY_POLICY, RetryPolicy

Evaluator=Callable[...,EvaluationResult]


def execute_evaluation_run(item: EvaluationInput, database_path: Path, evaluator: Evaluator=evaluate_answer, retry_policy: RetryPolicy=DEFAULT_RETRY_POLICY, **kwargs: object) -> tuple[str,EvaluationResult]:
    run_id=database.create_evaluation_run(item,database_path)
    for attempt in range(1,retry_policy.max_attempts+1):
        state=RunState.EVALUATING if attempt==1 else RunState.RETRYING
        database.update_evaluation_run_state(run_id,state,database_path,attempt_count=attempt)
        try:
            result=evaluator(item,**kwargs)
            database.save_evaluation(item,result,database_path)
            final={Decision.PUBLISH:RunState.APPROVED,Decision.REVIEW:RunState.HUMAN_REVIEW,Decision.REJECT:RunState.REJECTED}[result.final_decision]
            database.update_evaluation_run_state(run_id,final,database_path,evaluation_id=result.evaluation_id,attempt_count=attempt,system_decision=result.final_decision)
            return run_id,result
        except Exception as error:
            failure=FailureType.INVALID_INPUT if isinstance(error,ValueError) else (FailureType.MODEL_TIMEOUT if isinstance(error,TimeoutError) else FailureType.EVALUATION_ERROR)
            if retry_policy.should_retry(failure,attempt):
                database.update_evaluation_run_state(run_id,RunState.RETRYING,database_path,failure_type=failure,failure_message=str(error),attempt_count=attempt)
                continue
            database.update_evaluation_run_state(run_id,RunState.FAILED,database_path,failure_type=failure,failure_message=str(error),attempt_count=attempt)
            raise
    raise RuntimeError("Retry loop ended unexpectedly")
