import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(tags=["health"])

# 앱 초기화 완료 여부 (startupProbe용)
_startup_complete = False


@router.on_event("startup")  # type: ignore[attr-defined]
async def mark_startup_complete():
  global _startup_complete
  _startup_complete = True


@router.get("/live")
async def liveness():
  """K8s livenessProbe: 프로세스 생존 여부만 확인"""
  return {"status": "ok"}


@router.get("/ready")
async def readiness():
  """K8s readinessProbe: 의존성(Redis) 연결 확인"""
  try:
    client = aioredis.from_url(settings.redis_url, socket_connect_timeout=1)
    await client.ping()
    await client.aclose()
    return {"status": "ok", "dependencies": {"redis": "ok"}}
  except Exception as e:
    return JSONResponse(
      status_code=503,
      content={"status": "unavailable", "dependencies": {"redis": str(e)}},
    )


@router.get("/startup")
async def startup():
  """K8s startupProbe: 앱 초기화 완료 여부"""
  if not _startup_complete:
    return JSONResponse(status_code=503, content={"status": "starting"})
  return {"status": "ok"}
