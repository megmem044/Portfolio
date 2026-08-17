"""Redis queue connection and evaluation job submission."""

from redis import Redis
from rq import Queue, Retry

from src.config import REDIS_URL


def enqueue_evaluation(evaluation_id: str) -> None:
    from src.worker import process_evaluation

    connection = Redis.from_url(REDIS_URL)
    connection.ping()
    Queue("evaluations", connection=connection).enqueue(
        process_evaluation,
        evaluation_id,
        job_id=evaluation_id,
        retry=Retry(max=2, interval=[2, 5]),
        job_timeout="10m",
        result_ttl=3600,
    )
