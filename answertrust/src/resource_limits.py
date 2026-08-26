"""Small process-local guards for public API resource boundaries."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RateLimiter:
    """A thread-safe sliding-window limiter keyed by client address."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self.limit:
                retry_after = max(1, int(requests[0] + self.window_seconds - now) + 1)
                return False, retry_after
            requests.append(now)
            return True, 0

    def reset(self) -> None:
        """Clear process-local counters (primarily useful for tests)."""
        with self._lock:
            self._requests.clear()


class EvaluationResourceLimitMiddleware(BaseHTTPMiddleware):
    """Reject oversized or overly frequent evaluation submissions early."""

    def __init__(self, app, max_body_bytes: int, limiter: RateLimiter):
        super().__init__(app)
        self.max_body_bytes = max_body_bytes
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.method != "POST" or request.url.path != "/api/v1/evaluations":
            return await call_next(request)

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_body_bytes:
                    return self._error(413, "REQUEST_TOO_LARGE", "Request body is too large.")
            except ValueError:
                return self._error(400, "MALFORMED_REQUEST", "Invalid Content-Length header.")

        # Also enforce the boundary when a client omits Content-Length.
        if len(await request.body()) > self.max_body_bytes:
            return self._error(413, "REQUEST_TOO_LARGE", "Request body is too large.")

        client_key = request.client.host if request.client else "unknown"
        allowed, retry_after = self.limiter.allow(client_key)
        if not allowed:
            return self._error(
                429,
                "RATE_LIMITED",
                "Too many evaluation requests. Try again later.",
                {"Retry-After": str(retry_after)},
            )
        return await call_next(request)

    @staticmethod
    def _error(status: int, code: str, message: str, headers=None) -> JSONResponse:
        return JSONResponse(
            status_code=status,
            headers=headers,
            content={"error": {"code": code, "message": message}},
        )
