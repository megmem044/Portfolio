from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from src.api import app, get_session
from src.api_client import AnswerTrustAPIClient
from src.db import create_session_factory, session_scope
from src.db_models import Base
from src.models import Decision, EvaluationInput


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(test_engine)
api_session_factory = create_session_factory(test_engine)


def get_test_session():
    with session_scope(api_session_factory) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_react_development_origin_is_allowed():
    response = client.options(
        "/api/v1/evaluations",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_create_evaluation():
    response = client.post(
        "/api/v1/evaluations",
        json={
            "question": "Did treatment improve sleep?",
            "paper_text": "RESULTS\nTreatment improved sleep.",
            "answer": "Treatment improved sleep.",
        },
    )

    assert response.status_code == 200
    assert response.json()["final_decision"] == "PUBLISH"


def test_create_evaluation_rejects_missing_input():
    response = client.post(
        "/api/v1/evaluations",
        json={"question": "", "paper_text": "Paper text", "answer": "Answer text"},
    )

    assert response.status_code == 422


def test_get_evaluation_by_id():
    created = client.post(
        "/api/v1/evaluations",
        json={
            "question": "Did treatment improve sleep?",
            "paper_text": "RESULTS\nTreatment improved sleep.",
            "answer": "Treatment improved sleep.",
        },
    ).json()

    response = client.get(f"/api/v1/evaluations/{created['evaluation_id']}")

    assert response.status_code == 200
    assert response.json()["evaluation_id"] == created["evaluation_id"]


def test_get_unknown_evaluation_returns_not_found():
    response = client.get("/api/v1/evaluations/unknown-id")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "NOT_FOUND", "message": "Evaluation not found."}
    }


def test_list_evaluations_with_pagination():
    response = client.get("/api/v1/evaluations?offset=0&limit=1")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["total"] >= 1
    assert body["offset"] == 0
    assert body["limit"] == 1


def test_list_evaluations_rejects_invalid_limit():
    response = client.get("/api/v1/evaluations?limit=0")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_review_keeps_original_system_decision():
    created = client.post(
        "/api/v1/evaluations",
        json={
            "question": "Did treatment improve outcomes?",
            "paper_text": "RESULTS\nTreatment improved outcomes in some participants.",
            "answer": "Treatment improved outcomes for all participants.",
        },
    ).json()

    response = client.post(
        f"/api/v1/evaluations/{created['evaluation_id']}/review",
        json={"decision": "REJECT", "notes": "The answer overstates the result."},
    )

    assert response.status_code == 200
    assert response.json()["system_decision"] == "REVIEW"
    assert response.json()["reviewer_decision"] == "REJECT"


def test_review_unknown_evaluation_returns_not_found():
    response = client.post(
        "/api/v1/evaluations/unknown-id/review",
        json={"decision": "APPROVE", "notes": "The answer is acceptable."},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_pending_review_endpoint_removes_resolved_item():
    created = client.post(
        "/api/v1/evaluations",
        json={"question": "Did treatment improve outcomes?", "paper_text": "RESULTS\nTreatment improved outcomes in some participants.", "answer": "Treatment improved outcomes for all participants."},
    ).json()
    pending = client.get("/api/v1/reviews/pending").json()
    assert created["evaluation_id"] in {item["evaluation"]["evaluation_id"] for item in pending}
    client.post(
        f"/api/v1/evaluations/{created['evaluation_id']}/review",
        json={"decision": "APPROVE", "notes": "A reviewer accepts this wording."},
    )
    pending = client.get("/api/v1/reviews/pending").json()
    assert created["evaluation_id"] not in {item["evaluation"]["evaluation_id"] for item in pending}


def test_api_client_creates_evaluation():
    api_client = AnswerTrustAPIClient(
        base_url="/api/v1", client=client, request_timeout=None
    )

    result = api_client.create_evaluation(
        EvaluationInput(
            "Did treatment improve sleep?",
            "RESULTS\nTreatment improved sleep.",
            "Treatment improved sleep.",
        )
    )

    assert result.final_decision == Decision.PUBLISH
    assert result.claim_results[0].evidence[0].section == "RESULTS"


def test_api_client_lists_and_reviews_flagged_evaluation():
    api_client = AnswerTrustAPIClient(
        base_url="/api/v1", client=client, request_timeout=None
    )
    result = api_client.create_evaluation(
        EvaluationInput(
            "Did treatment improve outcomes?",
            "RESULTS\nTreatment improved outcomes in some participants.",
            "Treatment improved outcomes for all participants.",
        )
    )
    waiting = api_client.list_review_required()
    assert result.evaluation_id in {
        item["evaluation"]["evaluation_id"] for item in waiting
    }

    api_client.review_evaluation(
        result.evaluation_id, "REJECT", "The answer overstates the result."
    )
    waiting = api_client.list_review_required()
    assert result.evaluation_id not in {
        item["evaluation"]["evaluation_id"] for item in waiting
    }


def test_openapi_contains_evaluation_response_schema():
    schema = client.get("/openapi.json").json()

    assert "EvaluationResponse" in schema["components"]["schemas"]
    assert (
        schema["paths"]["/api/v1/evaluations"]["post"]["responses"]["200"]
        ["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/EvaluationResponse"
    )


def test_publication_benchmark_api_persists_run_and_results():
    response = client.post("/api/v1/benchmarks/publication")

    assert response.status_code == 200
    created = response.json()
    assert created["status"] == "COMPLETED"
    assert created["metrics"]["total_examples"] == 50
    assert len(created["results"]) == 50

    listed = client.get("/api/v1/benchmarks").json()
    assert created["run_id"] in {run["run_id"] for run in listed}

    detail = client.get(f"/api/v1/benchmarks/{created['run_id']}").json()
    assert len(detail["results"]) == 50
