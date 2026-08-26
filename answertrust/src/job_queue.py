"""Redis queue connection and evaluation job submission."""

from redis import Redis
from rq import Queue, Retry

from src.config import MAX_QUEUED_EVALUATIONS, REDIS_URL


class QueueSaturatedError(RuntimeError):
    """Raised when accepting another job would exceed the configured backlog."""


def enqueue_evaluation(evaluation_id: str) -> None:
    from src.worker import process_evaluation

    connection = Redis.from_url(REDIS_URL)
    connection.ping()
    queue = Queue("evaluations", connection=connection)
    if queue.count >= MAX_QUEUED_EVALUATIONS:
        raise QueueSaturatedError("The evaluation queue is full.")
    queue.enqueue(
        process_evaluation,
        evaluation_id,
        job_id=evaluation_id,
        retry=Retry(max=2, interval=[2, 5]),
        job_timeout="10m",
        result_ttl=3600,
    )
