import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.monitoring.logger import log_api_request, log_error, audit_log
from backend.monitoring.metrics import metrics
from backend.monitoring.tracing import request_id_var, trace_context, tracer
from backend.monitoring.security import rate_limiter, Sanitizer


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = uuid.uuid4().hex
        request_id_var.set(request_id)
        trace_id = tracer.start_trace(request_id)
        trace_context.set({"trace_id": trace_id, "request_id": request_id})

        user_id = request.headers.get("X-User-ID", request.client.host if request.client else "unknown")
        client_ip = request.client.host if request.client else None
        endpoint = request.url.path
        method = request.method

        rate_limit_key = f"{user_id}:{endpoint}"
        if endpoint.startswith("/api/chat") and not rate_limiter.is_allowed(rate_limit_key):
            log_api_request(endpoint, method, user_id, 429, 0, client_ip)
            return Response(
                content='{"error": "rate_limit_exceeded", "message": "Demasiadas solicitudes. Intenta de nuevo en 60 segundos."}',
                status_code=429,
                media_type="application/json",
            )

        start = time.perf_counter()
        try:
            response = await call_next(request)

            if hasattr(request, "_input_sanitized") and request._input_sanitized:
                pass

            duration = (time.perf_counter() - start) * 1000
            log_api_request(endpoint, method, user_id, response.status_code, duration, client_ip)

            if response.status_code >= 400:
                log_error(
                    error_type=f"http_{response.status_code}",
                    message=f"HTTP {response.status_code} on {method} {endpoint}",
                    endpoint=endpoint,
                    user_id=user_id,
                )

            if response.status_code < 400:
                audit_log(
                    action=f"{method}_{endpoint.replace('/', '_')}",
                    user_id=user_id,
                    resource=endpoint,
                    outcome="success",
                )

            return response

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            log_error(
                error_type=type(e).__name__,
                message=str(e),
                endpoint=endpoint,
                user_id=user_id,
            )
            log_api_request(endpoint, method, user_id, 500, duration, client_ip)
            raise


def setup_monitoring(app: FastAPI):
    app.add_middleware(ObservabilityMiddleware)

    @app.get("/api/metrics")
    async def get_metrics():
        return metrics.get_snapshot()

    @app.get("/api/health/detailed")
    async def detailed_health():
        return {
            "status": "ok",
            "metrics": metrics.get_snapshot(),
            "uptime": time.time(),
        }

    return app
