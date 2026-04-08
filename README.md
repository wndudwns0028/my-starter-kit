# DevOps/SRE Starter Kit

저장소 URL: https://github.com/wndudwns0028/my-starter-kit

📦 Starter Kit 설명:
- **기술 스택**: Python/FastAPI + Kubernetes + Terraform + Prometheus/Grafana + GitHub Actions + ArgoCD + Ray Serve
- **주요 기능**: K8s 무중단 배포 및 HPA 오토스케일링, SLO 기반 Error Budget 모니터링 대시보드, GitOps CI/CD 파이프라인, Ray GPU 분산 추론 서버 + Vellum 프롬프트 버전관리
- **용도**: DevOps/Cloud/SRE 엔지니어 취업 포트폴리오. 로컬(minikube)에서 바로 실행하고 AWS(EKS)로 그대로 전환 가능

---

DevOps/Cloud/SRE 엔지니어 취업을 위한 포트폴리오 프로젝트 모음.

## 포함된 프로젝트

| 프로젝트 | 핵심 기술 | 직무 연관성 |
|---------|----------|-----------|
| K8s + Observability | Kubernetes, Prometheus, Grafana, SLO | SRE 핵심 |
| GitOps CI/CD | GitHub Actions, ArgoCD, Docker | DevOps 필수 |
| Ray GPU Serving | Ray Serve, Vellum, GPU 파드 | MLOps 차별화 |

## 빠른 시작

### 사전 요구사항

- Docker Desktop
- minikube 또는 kind
- kubectl, helm

### 로컬 환경 구성 (원클릭)

```bash
chmod +x scripts/*.sh
./scripts/setup-local.sh
```

### 서비스 접근

```bash
./scripts/port-forward.sh
```

| 서비스 | 주소 |
|--------|------|
| API (Swagger) | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 (admin/admin) |
| ArgoCD | https://localhost:8080 |

### Docker Compose로 빠른 테스트 (K8s 없이)

```bash
cp .env.example .env
docker compose up -d
```

## 디렉토리 구조

```
my-starter-kit/
├── services/api/          # FastAPI 마이크로서비스
├── kubernetes/            # K8s 매니페스트 + Ray 클러스터
├── terraform/             # IaC (로컬→AWS 전환 가능)
├── ci-cd/                 # GitHub Actions + ArgoCD
├── monitoring/            # Prometheus 규칙 + Grafana 대시보드
├── ray/                   # Ray Serve LLM 서빙 + Vellum 연동
└── scripts/               # 자동화 스크립트
```

## AWS 배포

```bash
cd terraform/environments/aws
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars 편집 후:
terraform init
terraform plan
terraform apply
```

EKS 생성 후 kubeconfig 업데이트:
```bash
aws eks update-kubeconfig --region ap-northeast-2 --name devops-starter-cluster
```

## ArgoCD 연동

`ci-cd/argocd/application.yaml`의 `repoURL`을 본인 레포지토리로 변경 후 적용:

```bash
kubectl apply -f ci-cd/argocd/application.yaml
```

이후 main 브랜치 머지 시 GitHub Actions → 이미지 빌드 → 태그 업데이트 → ArgoCD 자동 동기화.

## SLO 정책

| SLO | 목표 | 알림 조건 |
|-----|------|---------|
| Availability | 99.9% (월 43분) | Error Rate > 1.44% (Fast Burn) |
| Latency p99 | < 500ms | p99 > 500ms 5분 지속 |
