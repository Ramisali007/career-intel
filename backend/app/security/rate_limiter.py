"""
Rate Limiting Middleware (§74).
In-memory sliding-window rate limiter for API endpoints.
"""

import time
import logging
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory sliding window rate limiter.
    Returns clean 429 JSON response with CORS headers without crashing ASGI workers.
    """

    # Default limits: (max_requests, window_seconds)
    LIMITS = {
        # Heavy write / processing operations
        "/api/v1/analyses/multi-jd": (30, 60),     # 30 multi-JD per minute
        "/api/v1/documents/upload": (60, 60),      # 60 uploads per minute
        "/api/v1/exports/": (60, 60),              # 60 exports per minute

        # Auth (brute force protection)
        "/api/v1/auth/login": (30, 60),            # 30 login attempts per minute
        "/api/v1/auth/register": (20, 60),         # 20 registrations per minute

        # Default for all other API routes (reads, lists, dashboards)
        "_default_": (600, 60),                    # 600 requests per minute
    }

    def __init__(self, app):
        super().__init__(app)
        # { client_key: [(timestamp, ...)] }
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Never rate limit CORS preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Only rate limit API routes
        path = request.url.path
        if not path.startswith("/api/"):
            return await call_next(request)

        # In local development or debug mode, allow higher throughput
        if settings.ENVIRONMENT == "development" or settings.DEBUG:
            return await call_next(request)

        # Determine client key (prefer user token hash, fallback to IP)
        client_key = self._get_client_key(request)

        # Find matching rate limit
        max_requests, window = self._get_limit(path)

        # Clean old entries and check
        now = time.time()
        cutoff = now - window
        timestamps = self._requests[client_key]
        timestamps[:] = [t for t in timestamps if t > cutoff]

        if len(timestamps) >= max_requests:
            retry_after = int(window - (now - timestamps[0])) + 1
            logger.warning(f"Rate limit exceeded for {client_key} on {path}")
            origin = request.headers.get("origin", "")
            resp = JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. Try again in {retry_after} seconds."},
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(cutoff + window)),
                },
            )
            if origin:
                resp.headers["Access-Control-Allow-Origin"] = origin
                resp.headers["Access-Control-Allow-Credentials"] = "true"
            return resp

        timestamps.append(now)

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - len(timestamps)))
        response.headers["X-RateLimit-Reset"] = str(int(cutoff + window))

        return response

    def _get_client_key(self, request: Request) -> str:
        """Get rate limit key — user ID if authenticated, else IP."""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token_hash = str(hash(auth[7:40]))
            return f"user:{token_hash}"

        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host if request.client else 'unknown'}"

    def _get_limit(self, path: str) -> tuple[int, int]:
        """Find the most specific rate limit for a path."""
        for prefix, limit in self.LIMITS.items():
            if prefix != "_default_" and path.startswith(prefix):
                return limit
        return self.LIMITS["_default_"]

