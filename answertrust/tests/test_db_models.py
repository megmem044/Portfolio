"""Persistence tests for evaluations, reviews, users, and benchmarks."""

from sqlalchemy import create_engine, func, inspect, select

from src.db import database_url, create_database_engine, create_session_factory, session_scope
from src.benchmark_repository import BenchmarkRepository
from src.db_models import Base, ClaimRecord, EvaluationRecord, EvidencePassageRecord, ModelPredictionRecord, PaperRecord
from src.evaluation_repository import EvaluationRepository
from src.evaluator import evaluate_answer
from src import database as legacy_database
from src.legacy_migration import migrate_legacy_sqlite
from src.models import Decision, RunState
from src.models import EvaluationInput


def test_evaluation_table_can_be_created():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("evaluations_v2")}

    assert {"evaluation_id", "paper_id", "state", "question", "answer"} <= columns
    assert "paper_text" not in columns
    assert {"created_at", "state"} <= {
        index["column_names"][0]
        for index in inspector.get_indexes("evaluations_v2")
    }


def test_session_scope_saves_evaluation(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    with session_scope(factory) as session:
        session.add(
            PaperRecord(
                paper_id="paper-1", content_hash="hash-1", paper_text="Paper text"
            )
        )
        session.add(
            EvaluationRecord(
                evaluation_id="evaluation-1",
                paper_id="paper-1",
                question="Did treatment help?",
                answer="Treatment helped.",
            )
        )

    with session_scope(factory) as session:
        saved = session.get(EvaluationRecord, "evaluation-1")
        assert saved is not None
        assert saved.state == "QUEUED"


def test_evaluation_attempt_moves_from_processing_to_retry(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/attempt.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        repository.save_queued("attempt-1", EvaluationInput("Question?", "Paper text", "Answer text"))
        assert repository.start_attempt("attempt-1").state == "PROCESSING"
        repository.save_failure("attempt-1", "Temporary failure", final=False)
    with session_scope(factory) as session:
        record = EvaluationRepository(session).get("attempt-1")
        assert record is not None
        assert record.state == "RETRYING"
        assert record.attempt_count == 1


def test_session_scope_rolls_back_failed_work(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    try:
        with session_scope(factory) as session:
            session.add(
                PaperRecord(
                    paper_id="paper-2", content_hash="hash-2", paper_text="Paper text"
                )
            )
            session.add(
                EvaluationRecord(
                    evaluation_id="evaluation-2",
                    paper_id="paper-2",
                    question="Did treatment help?",
                    answer="Treatment helped.",
                )
            )
            raise RuntimeError("stop")
    except RuntimeError:
        pass

    with session_scope(factory) as session:
        assert session.get(EvaluationRecord, "evaluation-2") is None


def test_evaluation_repository_saves_and_gets_record(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        repository.save_queued(
            "evaluation-3",
            EvaluationInput(
                "Did treatment help?",
                "RESULTS\nTreatment helped.",
                "Treatment helped.",
            ),
        )

    with session_scope(factory) as session:
        saved = EvaluationRepository(session).get("evaluation-3")
        assert saved is not None
        assert saved.state == "QUEUED"
        assert saved.question == "Did treatment help?"


def test_evaluation_repository_lists_with_total(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        for number in range(3):
            repository.save_queued(
                f"evaluation-{number}",
                EvaluationInput("Question text", "Paper text", "Answer text"),
            )

    with session_scope(factory) as session:
        records, total = EvaluationRepository(session).list(offset=1, limit=1)
        assert len(records) == 1
        assert total == 3


def test_evaluation_repository_saves_completed_result(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    item = EvaluationInput(
        "Did treatment improve outcomes?",
        "RESULTS\nTreatment improved outcomes in some participants.",
        "Treatment improved outcomes for all participants.",
    )
    result = evaluate_answer(item)

    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        repository.save_queued(result.evaluation_id, item)
        saved = repository.save_result(result)

        assert saved.state == "REVIEW_REQUIRED"
        assert saved.final_decision == "REVIEW"
        claims = repository.claim_results(result.evaluation_id)
        assert claims[0]["evidence"][0]["section"] == "RESULTS"
        assert session.scalar(select(func.count(ClaimRecord.claim_id))) == 1
        assert session.scalar(select(func.count(EvidencePassageRecord.evidence_id))) >= 1


def test_evaluation_repository_saves_review_without_changing_system_decision(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    item = EvaluationInput(
        "Did treatment improve outcomes?",
        "RESULTS\nTreatment improved outcomes in some participants.",
        "Treatment improved outcomes for all participants.",
    )
    result = evaluate_answer(item)

    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        repository.save_queued(result.evaluation_id, item)
        repository.save_result(result)
        task = repository.get_review_task(result.evaluation_id)
        assert task is not None
        assert task.status == "OPEN"
        review = repository.save_review(
            result.evaluation_id, "REJECT", "The answer overstates the result."
        )

        saved = repository.get(result.evaluation_id)
        assert saved is not None
        assert saved.final_decision == "REVIEW"
        assert saved.state == "REJECTED"
        assert review.reviewer_decision == "REJECT"
        assert review.task_id == task.task_id
        assert task.status == "RESOLVED"
        assert task.resolved_at is not None


def test_postgresql_url_uses_psycopg_driver(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql://answertrust:secret@localhost/answertrust"
    )

    url = database_url()
    engine = create_database_engine(url)

    assert url.startswith("postgresql+psycopg://")
    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "psycopg"


def test_repository_reuses_the_same_paper(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    item = EvaluationInput("Question text", "Shared paper text", "Answer text")

    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        first = repository.save_queued("evaluation-paper-1", item)
        second = repository.save_queued("evaluation-paper-2", item)

        assert first.paper_id == second.paper_id
        assert session.scalar(select(func.count(PaperRecord.paper_id))) == 1


def test_repository_saves_model_prediction_separately(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    item = EvaluationInput(
        "Did treatment improve sleep?",
        "RESULTS\nTreatment improved sleep.",
        "Treatment improved sleep.",
    )
    result = evaluate_answer(item)
    result.claim_results[0].nli_label = "entailment"
    result.claim_results[0].nli_confidence = 0.95

    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        repository.save_queued(result.evaluation_id, item)
        repository.save_result(result)

        assert session.scalar(select(func.count(ModelPredictionRecord.prediction_id))) == 1
        saved_claim = repository.claim_results(result.evaluation_id)[0]
        assert saved_claim["nli_label"] == "entailment"
        assert saved_claim["nli_confidence"] == 0.95


def test_publish_result_does_not_create_review_task(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    item = EvaluationInput(
        "Did treatment improve sleep?",
        "RESULTS\nTreatment improved sleep.",
        "Treatment improved sleep.",
    )
    result = evaluate_answer(item)

    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        repository.save_queued(result.evaluation_id, item)
        repository.save_result(result)

        assert repository.get_review_task(result.evaluation_id) is None


def test_benchmark_repository_completes_run_with_results(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    with session_scope(factory) as session:
        repository = BenchmarkRepository(session)
        run = repository.start("decision-safety")
        first = repository.add_result(
            run.run_id, "example-1", "REVIEW", "REVIEW", {"score": 72}
        )
        repository.add_result(run.run_id, "example-2", "REJECT", "REVIEW")
        completed = repository.complete(run.run_id, {"accuracy_pct": 50.0})

        assert first.is_correct is True
        assert completed.status == "COMPLETED"
        assert completed.metrics == {"accuracy_pct": 50.0}
        assert len(repository.results(run.run_id)) == 2


def test_benchmark_repository_records_failure(tmp_path):
    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/test.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    with session_scope(factory) as session:
        repository = BenchmarkRepository(session)
        run = repository.start("nli")
        failed = repository.fail(run.run_id, "Model unavailable")

        assert failed.status == "FAILED"
        assert failed.error_message == "Model unavailable"
        assert failed.completed_at is not None


def test_legacy_sqlite_import_preserves_review_audit(tmp_path):
    legacy_path = tmp_path / "legacy.db"
    item = EvaluationInput(
        "Did treatment improve outcomes?",
        "RESULTS\nTreatment improved outcomes in some participants.",
        "Treatment improved outcomes for all participants.",
    )
    result = evaluate_answer(item)
    run_id = legacy_database.create_evaluation_run(item, legacy_path)
    legacy_database.save_evaluation(item, result, legacy_path)
    legacy_database.update_evaluation_run_state(
        run_id,
        RunState.HUMAN_REVIEW,
        legacy_path,
        evaluation_id=result.evaluation_id,
        system_decision=Decision.REVIEW,
    )
    legacy_database.save_review(
        run_id, "REJECT", "The answer overstates the result.", legacy_path
    )

    engine = create_database_engine(f"sqlite:///{tmp_path.as_posix()}/target.db")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)
    summary = migrate_legacy_sqlite(legacy_path, factory)

    assert summary == {"migrated": 1, "skipped": 0, "reviews": 1}
    with session_scope(factory) as session:
        repository = EvaluationRepository(session)
        saved = repository.get(result.evaluation_id)
        review = repository.get_review(result.evaluation_id)
        assert saved is not None and saved.final_decision == "REVIEW"
        assert saved.state == "REJECTED"
        assert review is not None and review.reviewer_decision == "REJECT"

    repeated = migrate_legacy_sqlite(legacy_path, factory)
    assert repeated == {"migrated": 0, "skipped": 1, "reviews": 0}
