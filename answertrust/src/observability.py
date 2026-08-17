"""Small, dependency-free logging and metrics foundation."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import logging
from threading import Lock
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class JsonFormatter(logging.Formatter):
    """Write one machine-readable JSON object per log line."""

    def format(self, record: logging.LogRecord) -> str:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        for field in ("request_id", "method", "path", "status_code", "duration_ms", "evaluation_id", "outcome"):
            value = getattr(record, field, None)
            if value is not None:
                event[field] = value
        return json.dumps(event, separators=(",", ":"))


logger = logging.getLogger("answertrust")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


class Metrics:
    """Keep basic process-local counters without storing user content."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: Counter[str] = Counter()
        self._duration_total_ms = 0.0

    def record_request(self, status_code: int, duration_ms: float) -> None:
        with self._lock:
            self._counters["http_requests_total"] += 1
            self._counters[f"http_status_{status_code}"] += 1
            self._duration_total_ms += duration_ms

    def increment(self, name: str) -> None:
        with self._lock:
            self._counters[name] += 1

    def snapshot(self) -> dict:
        with self._lock:
            total = self._counters["http_requests_total"]
            return {
                **dict(self._counters),
                "average_http_duration_ms": round(self._duration_total_ms / total, 2) if total else 0.0,
            }


metrics = Metrics()


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        started = perf_counter()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration_ms = round((perf_counter() - started) * 1000, 2)
            metrics.record_request(status_code, duration_ms)
            logger.info("http_request", extra={"request_id": request_id, "method": request.method, "path": request.url.path, "status_code": status_code, "duration_ms": duration_ms})
        response.headers["X-Request-ID"] = request_id
        return response
