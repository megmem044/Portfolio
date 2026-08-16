from sqlalchemy import create_engine, func, inspect, select

from src.db import database_url, create_database_engine, create_session_factory, session_scope
from src.db_models import Base, ClaimRecord, EvaluationRecord, EvidencePassageRecord, PaperRecord
from src.evaluation_repository import EvaluationRepository
from src.evaluator import evaluate_answer
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
        review = repository.save_review(
            result.evaluation_id, "REJECT", "The answer overstates the result."
        )

        saved = repository.get(result.evaluation_id)
        assert saved is not None
        assert saved.final_decision == "REVIEW"
        assert saved.state == "REJECTED"
        assert review.reviewer_decision == "REJECT"


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
