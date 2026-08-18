from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

from src.auth import create_token, create_user
from src.api import app, get_evaluation_enqueuer, get_session
from src.api_client import AnswerTrustAPIClient
from src.db import create_session_factory, session_scope
from src.db_models import Base, UserRecord
from src.evaluation_repository import EvaluationRepository
from src.evaluator import evaluate_answer
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


def sync_enqueue(evaluation_id):
    with session_scope(api_session_factory) as session:
        repository = EvaluationRepository(session)
        result = evaluate_answer(repository.evaluation_input(evaluation_id))
        result.evaluation_id = evaluation_id
        repository.save_result(result)


app.dependency_overrides[get_evaluation_enqueuer] = lambda: sync_enqueue


def submit_and_get(payload):
    submitted = client.post("/api/v1/evaluations", json=payload)
    assert submitted.status_code == 202
    return client.get(f"/api/v1/evaluations/{submitted.json()['evaluation_id']}").json()


def auth_headers(role="REVIEWER"):
    email = f"{role.lower()}@example.com"
    with session_scope(api_session_factory) as session:
        user = session.scalar(select(UserRecord).where(UserRecord.email == email))
        if user is None:
            user = create_user(session, email, "secure-password", role)
        token = create_token(user)
    return {"Authorization": f"Bearer {token}"}


def test_login_returns_user_and_token():
    auth_headers()
    response = client.post("/api/v1/auth/login", json={"email": "reviewer@example.com", "password": "secure-password"})
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "REVIEWER"


def test_review_queue_requires_sign_in():
    response = client.get("/api/v1/reviews/pending")
    assert response.status_code == 401


def test_reviewer_cannot_run_administrator_benchmark():
    response = client.post("/api/v1/benchmarks/publication", headers=auth_headers())
    assert response.status_code == 403


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database_connection():
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "connected"}


def test_every_response_has_request_id():
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-request-123"})
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_metrics_are_admin_only_and_contain_request_counts():
    denied = client.get("/api/v1/metrics", headers=auth_headers())
    assert denied.status_code == 403
    response = client.get("/api/v1/metrics", headers=auth_headers("ADMIN"))
    assert response.status_code == 200
    assert response.json()["http_requests_total"] >= 1


def test_persistent_analytics_are_admin_only():
    denied = client.get("/api/v1/analytics", headers=auth_headers())
    assert denied.status_code == 403
    response = client.get("/api/v1/analytics", headers=auth_headers("ADMIN"))
    assert response.status_code == 200
    body = response.json()
    assert body["total_evaluations"] >= 0
    assert set(body["decision_counts"]) == {"PUBLISH", "REVIEW", "REJECT"}
    assert "benchmark_history" in body


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
    result = submit_and_get(
        {
            "question": "Did treatment improve sleep?",
            "paper_text": "RESULTS\nTreatment improved sleep.",
            "answer": "Treatment improved sleep.",
        },
    )

    assert result["final_decision"] == "PUBLISH"


def test_create_evaluation_rejects_missing_input():
    response = client.post(
        "/api/v1/evaluations",
        json={"question": "", "paper_text": "Paper text", "answer": "Answer text"},
    )

    assert response.status_code == 422


def test_get_evaluation_by_id():
    created = submit_and_get(
        {
            "question": "Did treatment improve sleep?",
            "paper_text": "RESULTS\nTreatment improved sleep.",
            "answer": "Treatment improved sleep.",
        },
    )

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
    created = submit_and_get(
        {
            "question": "Did treatment improve outcomes?",
            "paper_text": "RESULTS\nTreatment improved outcomes in some participants.",
            "answer": "Treatment improved outcomes for all participants.",
        },
    )

    response = client.post(
        f"/api/v1/evaluations/{created['evaluation_id']}/review",
        json={"decision": "REJECT", "notes": "The answer overstates the result."},
        headers=auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["system_decision"] == "REVIEW"
    assert response.json()["reviewer_decision"] == "REJECT"


def test_review_unknown_evaluation_returns_not_found():
    response = client.post(
        "/api/v1/evaluations/unknown-id/review",
        json={"decision": "APPROVE", "notes": "The answer is acceptable."},
        headers=auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_pending_review_endpoint_removes_resolved_item():
    created = submit_and_get({"question": "Did treatment improve outcomes?", "paper_text": "RESULTS\nTreatment improved outcomes in some participants.", "answer": "Treatment improved outcomes for all participants."})
    pending = client.get("/api/v1/reviews/pending", headers=auth_headers()).json()
    assert created["evaluation_id"] in {item["evaluation"]["evaluation_id"] for item in pending}
    client.post(
        f"/api/v1/evaluations/{created['evaluation_id']}/review",
        json={"decision": "APPROVE", "notes": "A reviewer accepts this wording."},
        headers=auth_headers(),
    )
    pending = client.get("/api/v1/reviews/pending", headers=auth_headers()).json()
    assert created["evaluation_id"] not in {item["evaluation"]["evaluation_id"] for item in pending}


def test_api_client_creates_evaluation():
    api_client = AnswerTrustAPIClient(
        base_url="/api/v1", client=client, request_timeout=None, access_token=auth_headers()["Authorization"].removeprefix("Bearer ")
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
        base_url="/api/v1", client=client, request_timeout=None,
        access_token=auth_headers()["Authorization"].removeprefix("Bearer "),
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


def test_openapi_contains_evaluation_submission_schema():
    schema = client.get("/openapi.json").json()

    assert "EvaluationSubmissionResponse" in schema["components"]["schemas"]
    assert (
        schema["paths"]["/api/v1/evaluations"]["post"]["responses"]["202"]
        ["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/EvaluationSubmissionResponse"
    )


def test_publication_benchmark_api_persists_run_and_results():
    response = client.post("/api/v1/benchmarks/publication", headers=auth_headers("ADMIN"))

    assert response.status_code == 200
    created = response.json()
    assert created["status"] == "COMPLETED"
    assert created["metrics"]["total_examples"] == 150
    assert len(created["results"]) == 150

    listed = client.get("/api/v1/benchmarks").json()
    assert created["run_id"] in {run["run_id"] for run in listed}

    detail = client.get(f"/api/v1/benchmarks/{created['run_id']}").json()
    assert len(detail["results"]) == 150
