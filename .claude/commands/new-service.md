새 FastAPI 마이크로서비스를 스캐폴딩해줘.

## 작업 순서

1. 사용자에게 서비스 이름을 물어봐 (예: `auth`, `payment`, `notification`)
2. `services/{서비스명}/` 디렉토리 아래 아래 구조로 파일을 생성해:

```
services/{서비스명}/
├── Dockerfile               # services/api/Dockerfile과 동일한 멀티스테이지 패턴
├── pyproject.toml
├── requirements.txt         # fastapi, uvicorn, prometheus-fastapi-instrumentator, pydantic-settings
└── app/
    ├── main.py              # FastAPI 앱 진입점 + Instrumentator + MetricsMiddleware
    ├── config.py            # Pydantic Settings
    ├── routers/
    │   ├── health.py        # /health/live, /health/ready, /health/startup (services/api 패턴 동일)
    │   └── {서비스명}.py    # 서비스별 기본 CRUD 엔드포인트
    ├── middleware/
    │   └── metrics.py       # RED 메서드 계측 (services/api/app/middleware/metrics.py 패턴 동일)
    └── models/
        └── {서비스명}.py    # Pydantic 모델
```

3. `kubernetes/base/` 에 해당 서비스용 K8s 매니페스트도 생성해:
   - `{서비스명}-deployment.yaml` — livenessProbe/readinessProbe/resources/securityContext 포함
   - `{서비스명}-service.yaml`
   - `kubernetes/monitoring/prometheus/{서비스명}-servicemonitor.yaml`

4. `docker-compose.yml`에 새 서비스 항목을 추가해 (기존 api 서비스 패턴 동일)

## 규칙
- `services/api/`의 코드 패턴을 반드시 참고해서 일관성 유지
- 들여쓰기 2칸 (Python은 4칸 예외)
- 한국어 주석
- 포트는 8000부터 +1씩 증가 (api=8000, 두 번째 서비스=8001, ...)
