#!/usr/bin/env bash
# 로컬 서비스 포트포워딩 (백그라운드 실행)
set -euo pipefail

info() { echo -e "\033[0;34m[INFO]\033[0m  $*"; }

# 기존 포트포워딩 프로세스 정리
pkill -f "kubectl port-forward" 2>/dev/null || true
sleep 1

info "포트포워딩 시작 중..."

kubectl port-forward svc/kube-prometheus-stack-grafana 3001:80 \
  -n monitoring &>/tmp/pf-grafana.log &

kubectl port-forward svc/prometheus-operated 9090:9090 \
  -n monitoring &>/tmp/pf-prometheus.log &

kubectl port-forward svc/devops-starter-api 8000:80 \
  -n devops-starter &>/tmp/pf-api.log &

kubectl port-forward svc/argocd-server 8080:443 \
  -n argocd &>/tmp/pf-argocd.log &

sleep 2

echo ""
echo "======================================"
echo " 서비스 접근 주소"
echo "======================================"
echo "  API (Swagger):  http://localhost:8000/docs"
echo "  API (Health):   http://localhost:8000/health/live"
echo "  Prometheus:     http://localhost:9090"
echo "  Grafana:        http://localhost:3001  (admin / admin)"
echo "  ArgoCD:         https://localhost:8080"
echo ""
echo "  ArgoCD 초기 비밀번호:"
echo "  kubectl -n argocd get secret argocd-initial-admin-secret \\"
echo "    -o jsonpath='{.data.password}' | base64 -d"
echo "======================================"
echo ""
echo "종료: ./scripts/teardown.sh 또는 pkill -f 'kubectl port-forward'"
