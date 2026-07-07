"""Lightweight middleware to measure and log per-request latency.

Helps confirm in production (Azure Log stream) exactly which endpoints are slow
and adds an ``X-Response-Time`` header for quick inspection from the client.
"""

import logging
import time

logger = logging.getLogger("equiflow.request")

SLOW_REQUEST_THRESHOLD_S = 1.0


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration = time.monotonic() - start

        response["X-Response-Time"] = f"{duration:.3f}s"

        log = logger.warning if duration >= SLOW_REQUEST_THRESHOLD_S else logger.info
        log(
            "%s %s -> %s in %.3fs",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration,
        )
        return response
