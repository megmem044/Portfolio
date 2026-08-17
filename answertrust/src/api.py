"""HTTP API for AnswerTrust."""

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from src.auth import create_token, require_roles, verify_password
from src.analytics_repository import AnalyticsRepository
from src.evaluator import evaluate_answer
from src.benchmark_repository import BenchmarkRepository
from src.benchmark_service import run_publication_benchmark
from src.db import create_database_engine, create_session_factory, session_scope
from src.db_models import EvaluationRecord, UserRecord
from src.evaluation_repository import EvaluationRepository
from src.models import ClaimLabel, Decision, EvaluationInput, EvaluationResult
from src.job_queue import enqueue_evaluation
from src.observability import RequestObservabilityMiddleware, logger, metrics


app = FastAPI(title="AnswerTrust API", version="1.0.0")
app.add_middleware(RequestObservabilityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite is the local fallback; DATABASE_URL can point this at PostgreSQL.
engine = create_database_engine()
SessionFactory = create_session_factory(engine)

def get_session():
    """Provide one safe database session to an API request."""
    with session_scope(SessionFactory) as session:
        yield session


def get_evaluation_enqueuer():
    return enqueue_evaluation


@app.exception_handler(HTTPException)
def handle_http_error(request: Request, error: HTTPException) -> JSONResponse:
    """Return the same error shape for expected API errors."""
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": "NOT_FOUND" if error.status_code == 404 else "HTTP_ERROR",
                "message": str(error.detail),
            }
        },
    )


@app.exception_handler(RequestValidationError)
def handle_validation_error(
    request: Request, error: RequestValidationError
) -> JSONResponse:
    """Return a simple message when request data is missing or invalid."""
    first_error = error.errors()[0]
    field = str(first_error["loc"][-1])
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"Invalid value for {field}.",
            }
        },
    )


class EvaluationRequest(BaseModel):
    """Information required to evaluate an AI-generated answer."""

    question: str = Field(min_length=3)
    paper_text: str = Field(min_length=3)
    answer: str = Field(min_length=3)


class ReviewRequest(BaseModel):
    """A human review decision and its explanation."""

    decision: Literal["APPROVE", "REJECT"]
    notes: str = Field(min_length=3)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    user_id: str
    email: str
    role: Literal["REVIEWER", "ADMIN"]


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserResponse


class EvidenceResponse(BaseModel):
    section: str
    passage: str
    similarity: float


class ClaimResponse(BaseModel):
    claim: str
    label: ClaimLabel
    evidence: list[EvidenceResponse]
    explanation: str
    failure_types: list[str]
    nli_label: str | None = None
    nli_confidence: float | None = None


class DimensionResponse(BaseModel):
    name: str
    score: int
    explanation: str
    concerns: list[str]


class EvaluationResponse(BaseModel):
    evaluation_id: str
    timestamp: datetime
    overall_score: int
    final_decision: Decision
    claim_results: list[ClaimResponse]
    dimension_scores: list[DimensionResponse]
    main_concern: str
    explanation: str
    recommended_action: str
    total_latency_ms: int
    deterministic_latency_ms: int


class EvaluationSubmissionResponse(BaseModel):
    evaluation_id: str
    state: Literal["QUEUED"]


class EvaluationListItemResponse(BaseModel):
    question: str
    answer: str
    evaluation: EvaluationResponse
    reviewed: bool


class EvaluationListResponse(BaseModel):
    items: list[EvaluationListItemResponse]
    total: int
    offset: int
    limit: int


class ReviewResponse(BaseModel):
    evaluation_id: str
    system_decision: Decision
    reviewer_decision: Literal["APPROVE", "REJECT"]
    reviewer_notes: str


class BenchmarkResultResponse(BaseModel):
    example_id: str
    expected_label: str
    actual_label: str
    is_correct: bool
    details: dict


class BenchmarkRunResponse(BaseModel):
    run_id: str
    benchmark_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    metrics: dict | None
    error_message: str | None
    results: list[BenchmarkResultResponse] = []


class BenchmarkTrendResponse(BaseModel):
    run_id: str
    started_at: datetime
    decision_accuracy_pct: float
    false_publish_rate_pct: float


class AnalyticsResponse(BaseModel):
    total_evaluations: int
    average_evaluation_latency_ms: float
    open_reviews: int
    resolved_reviews: int
    decision_counts: dict[str, int]
    review_counts: dict[str, int]
    benchmark_history: list[BenchmarkTrendResponse]


@app.get("/api/v1/health", response_model=dict[str, str])
def health() -> dict[str, str]:
    """Confirm that the API server is running."""
    return {"status": "ok"}


@app.get("/api/v1/readiness", response_model=dict[str, str])
def readiness(session: Session = Depends(get_session)) -> dict[str, str]:
    """Confirm that the API can reach its database."""
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        logger.error("database_not_ready")
        raise HTTPException(status_code=503, detail="The database is unavailable.") from error
    return {"status": "ready", "database": "connected"}


@app.get("/api/v1/metrics", response_model=dict[str, int | float])
def operational_metrics(current_user: dict = Depends(require_roles("ADMIN"))):
    """Return non-sensitive process metrics to administrators."""
    return metrics.snapshot()


@app.get("/api/v1/analytics", response_model=AnalyticsResponse)
def analytics_dashboard(session: Session = Depends(get_session), current_user: dict = Depends(require_roles("ADMIN"))):
    """Return persistent evaluation, review, and benchmark trends."""
    return AnalyticsRepository(session).dashboard()


@app.post("/api/v1/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Exchange an email and password for a short-lived signed token."""
    user = session.scalar(select(UserRecord).where(UserRecord.email == request.email.strip().lower()))
    if user is None or not user.is_active or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return {
        "access_token": create_token(user),
        "user": {"user_id": user.user_id, "email": user.email, "role": user.role},
    }


@app.post("/api/v1/evaluations", response_model=EvaluationSubmissionResponse, status_code=202)
def create_evaluation(request: EvaluationRequest, session: Session = Depends(get_session), enqueue=Depends(get_evaluation_enqueuer)):
    """Persist and enqueue an evaluation without waiting for inference."""
    evaluation_id = str(uuid4())
    repository = EvaluationRepository(session)
    repository.save_queued(evaluation_id, EvaluationInput(request.question, request.paper_text, request.answer))
    session.commit()
    try:
        enqueue(evaluation_id)
    except Exception as error:
        repository.save_failure(evaluation_id, "The evaluation queue is unavailable.", final=True)
        session.commit()
        raise HTTPException(status_code=503, detail="The evaluation queue is unavailable.") from error
    metrics.increment("evaluations_queued_total")
    return {"evaluation_id": evaluation_id, "state": "QUEUED"}


@app.get("/api/v1/evaluations/{evaluation_id}", response_model=None)
def get_evaluation(evaluation_id: str, session: Session = Depends(get_session)):
    """Return current status and the result when processing has finished."""
    record = EvaluationRepository(session).get(evaluation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    if record.state in {"QUEUED", "PROCESSING", "RETRYING", "FAILED"}:
        return {"evaluation_id": record.evaluation_id, "state": record.state, "attempt_count": record.attempt_count, "failure_message": record.failure_message}
    response = _record_response(record, EvaluationRepository(session))
    response["state"] = record.state
    response["attempt_count"] = record.attempt_count
    return response


@app.get("/api/v1/evaluations", response_model=EvaluationListResponse)
def list_evaluations(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Return a small page of completed evaluations."""
    records, total = EvaluationRepository(session).list(offset, limit, include_pending=False)
    items = [
        {
            "question": record.question,
            "answer": record.answer,
            "evaluation": _record_response(record, EvaluationRepository(session)),
            "reviewed": EvaluationRepository(session).get_review(record.evaluation_id) is not None,
        }
        for record in records
    ]
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@app.post(
    "/api/v1/evaluations/{evaluation_id}/review",
    response_model=ReviewResponse,
)
def review_evaluation(
    evaluation_id: str,
    request: ReviewRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_roles("REVIEWER", "ADMIN")),
):
    """Record a human decision without changing the system decision."""
    record = EvaluationRepository(session).get(evaluation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    saved_review = EvaluationRepository(session).save_review(
        evaluation_id, request.decision, request.notes, current_user["sub"]
    )
    metrics.increment("reviews_resolved_total")
    metrics.increment(f"review_outcome_{request.decision.lower()}")
    logger.info("review_resolved", extra={"evaluation_id": evaluation_id, "outcome": request.decision})
    review = {
        "evaluation_id": evaluation_id,
        "system_decision": record.final_decision,
        "reviewer_decision": saved_review.reviewer_decision,
        "reviewer_notes": saved_review.reviewer_notes,
    }
    return review


@app.get("/api/v1/reviews/pending", response_model=list[EvaluationListItemResponse])
def list_pending_reviews(session: Session = Depends(get_session), current_user: dict = Depends(require_roles("REVIEWER", "ADMIN"))):
    """Return evaluations waiting for a human review decision."""
    repository = EvaluationRepository(session)
    return [
        {"question": record.question, "answer": record.answer,
         "evaluation": _record_response(record, repository), "reviewed": False}
        for record in repository.list_pending_reviews()
    ]


@app.post("/api/v1/benchmarks/publication", response_model=BenchmarkRunResponse)
def create_publication_benchmark(session: Session = Depends(get_session), current_user: dict = Depends(require_roles("ADMIN"))):
    """Run and save the publication-safety benchmark."""
    repository = BenchmarkRepository(session)
    run = run_publication_benchmark(repository)
    metrics.increment("benchmark_runs_total")
    return _benchmark_response(run, repository)


@app.get("/api/v1/benchmarks", response_model=list[BenchmarkRunResponse])
def list_benchmark_runs(session: Session = Depends(get_session)):
    """List saved benchmark runs without their example details."""
    repository = BenchmarkRepository(session)
    return [_benchmark_response(run, repository, include_results=False) for run in repository.list()]


@app.get("/api/v1/benchmarks/{run_id}", response_model=BenchmarkRunResponse)
def get_benchmark_run(run_id: str, session: Session = Depends(get_session)):
    """Return one benchmark run and all of its example results."""
    repository = BenchmarkRepository(session)
    run = repository.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Benchmark run not found.")
    return _benchmark_response(run, repository)


def _record_response(
    record: EvaluationRecord, repository: EvaluationRepository
) -> dict:
    """Convert a saved row into the public API response shape."""
    return {
        "evaluation_id": record.evaluation_id,
        "timestamp": record.created_at,
        "overall_score": record.overall_score,
        "final_decision": record.final_decision,
        "claim_results": repository.claim_results(record.evaluation_id),
        "dimension_scores": record.dimension_scores,
        "main_concern": record.main_concern,
        "explanation": record.explanation,
        "recommended_action": record.recommended_action,
        "total_latency_ms": record.total_latency_ms,
        "deterministic_latency_ms": record.total_latency_ms,
    }


def _benchmark_response(run, repository: BenchmarkRepository, include_results: bool = True) -> dict:
    results = repository.results(run.run_id) if include_results else []
    return {
        "run_id": run.run_id,
        "benchmark_name": run.benchmark_name,
        "status": run.status,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "metrics": run.metrics,
        "error_message": run.error_message,
        "results": [
            {
                "example_id": result.example_id,
                "expected_label": result.expected_label,
                "actual_label": result.actual_label,
                "is_correct": result.is_correct,
                "details": result.details,
            }
            for result in results
        ],
    }
