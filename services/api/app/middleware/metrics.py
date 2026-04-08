import time

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# RED 메서드: Rate, Error, Duration
REQUEST_COUNT = Counter(
  "http_requests_total",
  "전체 HTTP 요청 수",
  ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
  "http_request_duration_seconds",
  "HTTP 요청 처리 시간 (초)",
  ["method", "endpoint"],
  buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)


class MetricsMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    start_time = time.perf_counter()

    # /metrics, /health 경로는 계측 제외 (노이즈 방지)
    skip_paths = {"/metrics", "/health/live", "/health/ready", "/health/startup"}
    if request.url.path in skip_paths:
      return await call_next(request)

    response = await call_next(request)
    duration = time.perf_counter() - start_time

    endpoint = request.url.path
    REQUEST_COUNT.labels(
      method=request.method,
      endpoint=endpoint,
      status_code=str(response.status_code),
    ).inc()
    REQUEST_DURATION.labels(method=request.method, endpoint=endpoint).observe(duration)

    return response
