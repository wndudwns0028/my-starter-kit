#!/usr/bin/env bash
# 로컬 환경 전체 정리
set -euo pipefail

info()    { echo -e "\033[0;34m[INFO]\033[0m  $*"; }
success() { echo -e "\033[0;32m[OK]\033[0m    $*"; }

echo ""
echo "=== DevOps Starter Kit - 환경 정리 ==="
echo ""

info "포트포워딩 프로세스 종료..."
pkill -f "kubectl port-forward" 2>/dev/null || true
success "포트포워딩 종료"

info "K8s 리소스 삭제..."
kubectl delete -f kubernetes/base/ --ignore-not-found=true
kubectl delete -f kubernetes/monitoring/prometheus/servicemonitor.yaml --ignore-not-found=true
success "앱 리소스 삭제 완료"

echo ""
read -r -p "Helm 릴리스(Prometheus, ArgoCD)도 삭제하겠습니까? (y/N): " delete_helm
if [[ "$delete_helm" =~ ^[Yy]$ ]]; then
  helm uninstall kube-prometheus-stack -n monitoring 2>/dev/null || true
  helm uninstall argocd -n argocd 2>/dev/null || true
  kubectl delete namespace monitoring argocd devops-starter --ignore-not-found=true
  success "Helm 릴리스 삭제 완료"
fi

echo ""
read -r -p "minikube 클러스터도 삭제하겠습니까? (y/N): " delete_minikube
if [[ "$delete_minikube" =~ ^[Yy]$ ]]; then
  minikube delete
  success "minikube 삭제 완료"
fi

echo ""
echo "정리 완료."
