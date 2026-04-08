# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개발 명령어

### 로컬 전체 스택 (Docker Compose)
```bash
cp .env.example .env
docker compose up -d          # API + Prometheus + Grafana + Redis 시작
docker compose logs -f api    # API 로그 확인
docker compose down           # 종료
```

### FastAPI 개발 서버 (직접 실행)
```bash
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 테스트
```bash
cd services/api
pytest                                    # 전체 테스트
pytest tests/test_health.py              # 단일 파일
pytest -k "test_create" -v               # 특정 테스트
pytest --cov=app --cov-report=term       # 커버리지 포함
```

### 린트 / 타입 검사
```bash
cd services/api
ruff check app/                  # 린트
ruff check app/ --fix            # 자동 수정
mypy app/ --ignore-missing-imports
```

### K8s 로컬 환경
```bash
./scripts/setup-local.sh    # 최초 환경 구성 (minikube + Prometheus + ArgoCD)
./scripts/port-forward.sh   # 서비스 포트포워딩
./scripts/teardown.sh       # 환경 정리

# 앱만 재배포
kubectl apply -f kubernetes/base/
kubectl rollout status deployment/devops-starter-api -n devops-starter
```

### Terraform
```bash
cd terraform/environments/aws
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## 아키텍처

### 전체 흐름
```
GitHub PR → ci.yml (lint/test/scan) → merge to main
  → cd-staging.yml (빌드 → ECR 푸시 → deployment.yaml 태그 업데이트 → git push)
  → ArgoCD (변경 감지 → K8s 자동 동기화)
```

GitOps 패턴: CD 파이프라인은 코드를 직접 배포하지 않고 `kubernetes/base/deployment.yaml`의 이미지 태그를 업데이트하면 ArgoCD가 감지하여 배포.

### FastAPI 서비스 (`services/api/`)
- `app/main.py` — 진입점. `MetricsMiddleware` 등록 후 `Instrumentator`로 `/metrics` 노출, 라우터 포함
- `app/middleware/metrics.py` — RED 메서드(Rate/Error/Duration) Counter + Histogram. `/health`, `/metrics` 경로는 계측 제외
- `app/routers/health.py` — K8s probe 3종: `/live`(프로세스 생존), `/ready`(Redis 연결 확인), `/startup`(초기화 완료)
- `app/config.py` — Pydantic Settings로 환경변수 관리

### K8s 매니페스트 (`kubernetes/`)
- `base/deployment.yaml` — `maxUnavailable: 0` 무중단 배포, probe 3종, `readOnlyRootFilesystem: true` 보안 설정, `/tmp`는 emptyDir 마운트 필요
- `monitoring/prometheus/servicemonitor.yaml` — `release: kube-prometheus-stack` 레이블 필수 (Prometheus Operator 자동 발견)
- `ray-cluster/ray-cluster.yaml` — GPU 워커는 `accelerator: nvidia-gpu` nodeSelector + `nvidia.com/gpu` taint toleration 필요

### 모니터링 (`monitoring/`)
- Prometheus 규칙: `slo.yaml`에서 Fast Burn(14.4× 에러율), Slow Burn(6×) 기반 SLO 알림. Error Budget = 0.1%
- Grafana 대시보드: `monitoring/grafana/dashboards/`에 JSON 저장 → `provisioning/dashboards/dashboards.yaml`로 자동 로드
- docker-compose 환경에서는 `monitoring/prometheus/prometheus.yml`이 스크레이핑 설정

### Ray GPU Serving (`ray/`)
- `serve_app.py` — `@serve.deployment(num_replicas=1, ray_actor_options={"num_gpus": 1})`. `MODEL_NAME` 환경변수로 HuggingFace 모델 지정. GPU 없으면 Mock 모드로 동작
- `vellum_client.py` — `VELLUM_API_KEY` 환경변수 필수. `get_deployment_info`는 `lru_cache`로 캐싱

### Terraform (`terraform/`)
- 모듈 구조: `modules/eks`, `modules/ecr` → `environments/aws/main.tf`에서 조합
- GPU 노드그룹은 `enable_gpu_nodegroup = true`로 활성화, 기본 비활성화(비용)
- S3 백엔드는 `main.tf`에 주석 처리됨 — 팀 협업 시 주석 해제

## 서비스 접근 주소 (포트포워딩 후)

| 서비스 | 주소 | 계정 |
|--------|------|------|
| API Swagger | http://localhost:8000/docs | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin / admin |
| ArgoCD | https://localhost:8080 | 초기 비밀번호: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' \| base64 -d` |
