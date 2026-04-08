# ---- 빌드 스테이지: 의존성 설치 ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt


# ---- 런타임 스테이지: 최소 이미지 ----
FROM python:3.11-slim AS runtime

# 비루트 사용자 생성 (보안)
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# builder에서 설치된 패키지만 복사
COPY --from=builder /install /usr/local

# 앱 소스 복사
COPY --chown=appuser:appgroup app/ ./app/

USER appuser

EXPOSE 8000

# K8s readinessProbe와 연동되는 헬스체크
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
