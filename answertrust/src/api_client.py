"""Small Python client for communicating with the AnswerTrust API."""

from datetime import datetime
from time import monotonic, sleep

import httpx

from src.config import API_BASE_URL
from src.models import (
    ClaimLabel,
    ClaimResult,
    Decision,
    DimensionScore,
    EvaluationInput,
    EvaluationResult,
    Evidence,
)


class AnswerTrustAPIClient:
    """Send evaluation requests to the AnswerTrust API."""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        client=None,
        request_timeout: int | None = 120,
        access_token: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx
        self.request_timeout = request_timeout
        self.headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

    def create_evaluation(self, item: EvaluationInput) -> EvaluationResult:
        request_options = {
            "json": {
                "question": item.question,
                "paper_text": item.paper_text,
                "answer": item.answer,
            }
        }
        if self.request_timeout is not None:
            request_options["timeout"] = self.request_timeout
        response = self.client.post(f"{self.base_url}/evaluations", **request_options)
        response.raise_for_status()
        evaluation_id = response.json()["evaluation_id"]
        deadline = monotonic() + (self.request_timeout or 120)
        while monotonic() < deadline:
            result_response = self.client.get(f"{self.base_url}/evaluations/{evaluation_id}")
            result_response.raise_for_status()
            data = result_response.json()
            if "final_decision" in data:
                return _evaluation_result(data)
            if data["state"] == "FAILED":
                raise RuntimeError(data.get("failure_message") or "Evaluation failed.")
            sleep(0.05)
        raise TimeoutError("The evaluation did not finish in time.")

    def list_review_required(self) -> list[dict]:
        """Return evaluations waiting for a human decision."""
        options = {"params": {"offset": 0, "limit": 100}}
        if self.request_timeout is not None:
            options["timeout"] = self.request_timeout
        response = self.client.get(f"{self.base_url}/evaluations", **options)
        response.raise_for_status()
        return [
            item for item in response.json()["items"]
            if item["evaluation"]["final_decision"] == "REVIEW" and not item["reviewed"]
        ]

    def review_evaluation(self, evaluation_id: str, decision: str, notes: str) -> dict:
        """Send a human review decision to the API."""
        options = {"json": {"decision": decision, "notes": notes}, "headers": self.headers}
        if self.request_timeout is not None:
            options["timeout"] = self.request_timeout
        response = self.client.post(
            f"{self.base_url}/evaluations/{evaluation_id}/review", **options
        )
        response.raise_for_status()
        return response.json()

    def run_publication_benchmark(self) -> dict:
        """Run and save the publication-safety benchmark."""
        options = {"headers": self.headers}
        if self.request_timeout is not None:
            options["timeout"] = self.request_timeout
        response = self.client.post(
            f"{self.base_url}/benchmarks/publication", **options
        )
        response.raise_for_status()
        return response.json()

    def list_benchmarks(self) -> list[dict]:
        """Return saved benchmark runs."""
        options = {}
        if self.request_timeout is not None:
            options["timeout"] = self.request_timeout
        response = self.client.get(f"{self.base_url}/benchmarks", **options)
        response.raise_for_status()
        return response.json()


def _evaluation_result(data: dict) -> EvaluationResult:
    """Turn the API's JSON response back into application objects."""
    claims = [
        ClaimResult(
            claim=item["claim"],
            label=ClaimLabel(item["label"]),
            evidence=[Evidence(**evidence) for evidence in item["evidence"]],
            explanation=item["explanation"],
            failure_types=item["failure_types"],
            nli_label=item.get("nli_label"),
            nli_confidence=item.get("nli_confidence"),
        )
        for item in data["claim_results"]
    ]
    dimensions = [DimensionScore(**item) for item in data["dimension_scores"]]
    return EvaluationResult(
        evaluation_id=data["evaluation_id"],
        timestamp=datetime.fromisoformat(data["timestamp"]),
        overall_score=data["overall_score"],
        final_decision=Decision(data["final_decision"]),
        claim_results=claims,
        dimension_scores=dimensions,
        main_concern=data["main_concern"],
        explanation=data["explanation"],
        recommended_action=data["recommended_action"],
        total_latency_ms=data["total_latency_ms"],
        deterministic_latency_ms=data["deterministic_latency_ms"],
    )
