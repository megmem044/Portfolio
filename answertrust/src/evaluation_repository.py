"""Database operations for evaluation records."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from src.db_models import ClaimRecord, EvaluationRecord, EvidencePassageRecord, ModelPredictionRecord, PaperRecord, ReviewRecord, ReviewTaskRecord
from src.models import Decision, EvaluationInput, EvaluationResult


class EvaluationRepository:
    """Save and read evaluations through one clear interface."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_queued(self, evaluation_id: str, item: EvaluationInput) -> EvaluationRecord:
        """Store a new evaluation before processing begins."""
        paper_hash = sha256(item.paper_text.encode("utf-8")).hexdigest()
        paper = self.session.scalar(
            select(PaperRecord).where(PaperRecord.content_hash == paper_hash)
        )
        if paper is None:
            paper = PaperRecord(
                paper_id=str(uuid4()),
                content_hash=paper_hash,
                paper_text=item.paper_text,
            )
            self.session.add(paper)
            self.session.flush()
        record = EvaluationRecord(
            evaluation_id=evaluation_id,
            paper_id=paper.paper_id,
            state="QUEUED",
            question=item.question,
            answer=item.answer,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get(self, evaluation_id: str) -> EvaluationRecord | None:
        """Find one evaluation by its ID."""
        return self.session.get(EvaluationRecord, evaluation_id)

    def start_attempt(self, evaluation_id: str) -> EvaluationRecord:
        record = self.get(evaluation_id)
        if record is None:
            raise KeyError(f"Unknown evaluation: {evaluation_id}")
        if record.state in {"COMPLETED", "REVIEW_REQUIRED", "APPROVED", "REJECTED"}:
            return record
        record.attempt_count += 1
        record.state = "PROCESSING" if record.attempt_count == 1 else "RETRYING"
        record.failure_message = None
        self.session.flush()
        return record

    def save_failure(self, evaluation_id: str, message: str, final: bool) -> None:
        record = self.get(evaluation_id)
        if record is None:
            raise KeyError(f"Unknown evaluation: {evaluation_id}")
        record.state = "FAILED" if final else "RETRYING"
        record.failure_message = message[:1000]
        self.session.flush()

    def evaluation_input(self, evaluation_id: str) -> EvaluationInput:
        record = self.get(evaluation_id)
        if record is None:
            raise KeyError(f"Unknown evaluation: {evaluation_id}")
        paper = self.session.get(PaperRecord, record.paper_id)
        if paper is None:
            raise KeyError(f"Paper missing for evaluation: {evaluation_id}")
        return EvaluationInput(record.question, paper.paper_text, record.answer)

    def save_result(self, result: EvaluationResult) -> EvaluationRecord:
        """Store a completed result and move it to the correct state."""
        record = self.get(result.evaluation_id)
        if record is None:
            raise KeyError(f"Unknown evaluation: {result.evaluation_id}")
        record.state = {
            Decision.PUBLISH: "COMPLETED",
            Decision.REVIEW: "REVIEW_REQUIRED",
            Decision.REJECT: "REJECTED",
        }[result.final_decision]
        record.overall_score = result.overall_score
        record.final_decision = result.final_decision.value
        record.dimension_scores = _json_safe(result.dimension_scores)
        record.main_concern = result.main_concern
        record.explanation = result.explanation
        record.recommended_action = result.recommended_action
        record.total_latency_ms = result.total_latency_ms
        if result.final_decision == Decision.REVIEW and self.get_review_task(result.evaluation_id) is None:
            self.session.add(
                ReviewTaskRecord(
                    task_id=str(uuid4()), evaluation_id=result.evaluation_id, status="OPEN"
                )
            )
        existing_claim_ids = list(
            self.session.scalars(
                select(ClaimRecord.claim_id).where(
                    ClaimRecord.evaluation_id == result.evaluation_id
                )
            )
        )
        if existing_claim_ids:
            self.session.execute(
                delete(ModelPredictionRecord).where(
                    ModelPredictionRecord.claim_id.in_(existing_claim_ids)
                )
            )
            self.session.execute(
                delete(EvidencePassageRecord).where(
                    EvidencePassageRecord.claim_id.in_(existing_claim_ids)
                )
            )
            self.session.execute(
                delete(ClaimRecord).where(
                    ClaimRecord.evaluation_id == result.evaluation_id
                )
            )
        for claim_position, claim in enumerate(result.claim_results):
            claim_id = str(uuid4())
            self.session.add(
                ClaimRecord(
                    claim_id=claim_id,
                    evaluation_id=result.evaluation_id,
                    position=claim_position,
                    claim_text=claim.claim,
                    label=claim.label.value,
                    explanation=claim.explanation,
                    failure_types=claim.failure_types,
                )
            )
            if claim.nli_label is not None and claim.nli_confidence is not None:
                self.session.add(
                    ModelPredictionRecord(
                        prediction_id=str(uuid4()),
                        claim_id=claim_id,
                        model_name="nli-classifier",
                        predicted_label=claim.nli_label,
                        confidence=claim.nli_confidence,
                    )
                )
            for evidence_position, evidence in enumerate(claim.evidence):
                self.session.add(
                    EvidencePassageRecord(
                        evidence_id=str(uuid4()),
                        claim_id=claim_id,
                        position=evidence_position,
                        section=evidence.section,
                        passage=evidence.passage,
                        similarity=evidence.similarity,
                    )
                )
        self.session.flush()
        return record

    def list(self, offset: int = 0, limit: int = 20, include_pending: bool = True) -> tuple[list[EvaluationRecord], int]:
        """Return one page of evaluations and the total count."""
        query = select(EvaluationRecord)
        count_query = select(func.count(EvaluationRecord.evaluation_id))
        if not include_pending:
            query = query.where(EvaluationRecord.final_decision.is_not(None))
            count_query = count_query.where(EvaluationRecord.final_decision.is_not(None))
        records = list(
            self.session.scalars(
                query
                .order_by(EvaluationRecord.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
        )
        total = self.session.scalar(count_query)
        return records, int(total or 0)

    def save_review(
        self, evaluation_id: str, decision: str, notes: str, reviewer_user_id: str | None = None
    ) -> ReviewRecord:
        """Save one human decision while preserving the system decision."""
        record = self.get(evaluation_id)
        if record is None:
            raise KeyError(f"Unknown evaluation: {evaluation_id}")
        if record.state != "REVIEW_REQUIRED":
            raise ValueError("Only evaluations awaiting review can be resolved.")
        task = self.get_review_task(evaluation_id)
        if task is None or task.status != "OPEN":
            raise ValueError("The evaluation has no open review task.")
        task.status = "RESOLVED"
        task.resolved_at = datetime.now(timezone.utc)
        review = ReviewRecord(
            evaluation_id=evaluation_id,
            task_id=task.task_id,
            reviewer_user_id=reviewer_user_id,
            reviewer_decision=decision,
            reviewer_notes=notes.strip(),
        )
        self.session.add(review)
        record.state = "APPROVED" if decision == "APPROVE" else "REJECTED"
        self.session.flush()
        return review

    def get_review(self, evaluation_id: str) -> ReviewRecord | None:
        """Return the human decision for an evaluation, when one exists."""
        return self.session.get(ReviewRecord, evaluation_id)

    def get_review_task(self, evaluation_id: str) -> ReviewTaskRecord | None:
        """Return the review task linked to an evaluation."""
        return self.session.scalar(
            select(ReviewTaskRecord).where(
                ReviewTaskRecord.evaluation_id == evaluation_id
            )
        )

    def list_pending_reviews(self) -> list[EvaluationRecord]:
        """Return evaluations whose human-review tasks are still open."""
        return list(
            self.session.scalars(
                select(EvaluationRecord)
                .join(ReviewTaskRecord, ReviewTaskRecord.evaluation_id == EvaluationRecord.evaluation_id)
                .where(ReviewTaskRecord.status == "OPEN")
                .order_by(ReviewTaskRecord.created_at)
            )
        )

    def claim_results(self, evaluation_id: str) -> list[dict]:
        """Rebuild ordered claim results from normalized database rows."""
        claims = list(
            self.session.scalars(
                select(ClaimRecord)
                .where(ClaimRecord.evaluation_id == evaluation_id)
                .order_by(ClaimRecord.position)
            )
        )
        results = []
        for claim in claims:
            evidence = list(
                self.session.scalars(
                    select(EvidencePassageRecord)
                    .where(EvidencePassageRecord.claim_id == claim.claim_id)
                    .order_by(EvidencePassageRecord.position)
                )
            )
            prediction = self.session.scalar(
                select(ModelPredictionRecord)
                .where(ModelPredictionRecord.claim_id == claim.claim_id)
                .order_by(ModelPredictionRecord.created_at.desc())
                .limit(1)
            )
            results.append(
                {
                    "claim": claim.claim_text,
                    "label": claim.label,
                    "evidence": [
                        {
                            "section": item.section,
                            "passage": item.passage,
                            "similarity": item.similarity,
                        }
                        for item in evidence
                    ],
                    "explanation": claim.explanation,
                    "failure_types": claim.failure_types,
                    "nli_label": prediction.predicted_label if prediction else None,
                    "nli_confidence": prediction.confidence if prediction else None,
                }
            )
        return results


def _json_safe(items: list) -> list[dict]:
    """Convert dataclasses and enums into values accepted by a JSON column."""
    return json.loads(json.dumps([asdict(item) for item in items], default=lambda item: item.value))
