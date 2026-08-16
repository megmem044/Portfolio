"""Run benchmarks and persist their complete lifecycle."""

from src.benchmark_repository import BenchmarkRepository
from src.experiments import run_experiment


def run_publication_benchmark(repository: BenchmarkRepository):
    """Run the publication-safety benchmark and save every result."""
    run = repository.start("publication-safety")
    try:
        rows, metrics = run_experiment(write_output=False)
        for row in rows:
            repository.add_result(
                run.run_id,
                row["id"],
                row["expected_decision"],
                row["actual_decision"],
                row,
            )
        repository.complete(run.run_id, metrics)
        return run
    except Exception as error:
        repository.fail(run.run_id, str(error))
        raise
