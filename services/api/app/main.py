from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.middleware.metrics import MetricsMiddleware
from app.routers import health, items

app = FastAPI(
  title="DevOps Starter API",
  version="1.0.0",
  description="DevOps/SRE Starter Kit - FastAPI 마이크로서비스",
)

# RED 메서드 계측 미들웨어
app.add_middleware(MetricsMiddleware)

# /metrics 엔드포인트 자동 노출 (Prometheus 스크레이핑)
Instrumentator().instrument(app).expose(app)

# 라우터 등록
app.include_router(health.router, prefix="/health")
app.include_router(items.router, prefix="/api/v1")


@app.get("/")
async def root():
  return {"service": "devops-starter-api", "version": "1.0.0", "docs": "/docs"}
