#!/usr/bin/env bash
# 로컬 DevOps Starter Kit 환경 원클릭 구성
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# 색상 출력 헬퍼
info()    { echo -e "\033[0;34m[INFO]\033[0m  $*"; }
success() { echo -e "\033[0;32m[OK]\033[0m    $*"; }
error()   { echo -e "\033[0;31m[ERROR]\033[0m $*" >&2; exit 1; }

echo ""
echo "=== DevOps Starter Kit - 로컬 환경 구성 ==="
echo ""

# ---- Step 1: 필수 도구 확인 ----
info "필수 도구 확인 중..."
for tool in docker kubectl helm; do
  if ! command -v "$tool" &>/dev/null; then
    error "$tool 가 설치되어 있지 않습니다. 설치 후 재실행하세요."
  fi
done
success "필수 도구 확인 완료"

# minikube 또는 kind 확인
if command -v minikube &>/dev/null; then
  K8S_TOOL="minikube"
elif command -v kind &>/dev/null; then
  K8S_TOOL="kind"
else
  error "minikube 또는 kind 가 필요합니다."
fi
info "K8s 도구: $K8S_TOOL"

# ---- Step 2: 로컬 K8s 클러스터 시작 ----
info "로컬 K8s 클러스터 시작 중..."
if [ "$K8S_TOOL" = "minikube" ]; then
  if ! minikube status | grep -q "Running"; then
    minikube start --cpus=4 --memory=8192 --driver=docker
    minikube addons enable ingress
    minikube addons enable metrics-server
    success "minikube 시작 완료"
  else
    success "minikube 이미 실행 중"
  fi
fi

# ---- Step 3: Helm 레포 추가 ----
info "Helm 레포지토리 추가 중..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo add argo https://argoproj.github.io/argo-helm 2>/dev/null || true
helm repo add kuberay https://ray-project.github.io/kuberay-helm/ 2>/dev/null || true
helm repo update
success "Helm 레포 업데이트 완료"

# ---- Step 4: Prometheus + Grafana 설치 ----
info "kube-prometheus-stack 설치 중 (약 2-3분 소요)..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
helm upgrade --install kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values "$ROOT_DIR/kubernetes/monitoring/prometheus/values.yaml" \
  --wait --timeout=5m
success "Prometheus + Grafana 설치 완료"

# ---- Step 5: ArgoCD 설치 ----
info "ArgoCD 설치 중..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --set server.service.type=ClusterIP \
  --wait --timeout=5m
success "ArgoCD 설치 완료"

# ---- Step 6: Ray Operator 설치 (선택) ----
read -r -p "Ray Operator를 설치하겠습니까? GPU 서빙 프로젝트용 (y/N): " install_ray
if [[ "$install_ray" =~ ^[Yy]$ ]]; then
  info "KubeRay Operator 설치 중..."
  helm upgrade --install kuberay-operator kuberay/kuberay-operator \
    --namespace ray-system --create-namespace \
    --wait --timeout=3m
  success "KubeRay Operator 설치 완료"
fi

# ---- Step 7: FastAPI 앱 빌드 및 로드 ----
info "FastAPI 이미지 빌드 중..."
docker build -t devops-starter-api:latest "$ROOT_DIR/services/api/"

if [ "$K8S_TOOL" = "minikube" ]; then
  info "minikube에 이미지 로드 중..."
  minikube image load devops-starter-api:latest
fi
success "이미지 빌드 완료"

# ---- Step 8: 앱 배포 ----
info "K8s 매니페스트 배포 중..."
kubectl apply -f "$ROOT_DIR/kubernetes/base/"
kubectl apply -f "$ROOT_DIR/kubernetes/monitoring/prometheus/servicemonitor.yaml"
kubectl rollout status deployment/devops-starter-api -n devops-starter --timeout=2m
success "앱 배포 완료"

echo ""
echo "======================================"
echo " 환경 구성 완료!"
echo " 포트포워딩 시작: ./scripts/port-forward.sh"
echo "======================================"
echo ""
