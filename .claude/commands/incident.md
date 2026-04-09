장애 runbook을 생성해줘.

## 작업 순서

1. 사용자에게 아래 정보를 물어봐:
   - 장애 제목 (예: "API 서버 응답 없음", "Error Rate 급등")
   - 심각도: P1(서비스 중단) / P2(성능 저하) / P3(일부 기능 오류)
   - 감지 방법: 알림(Alert) / 사용자 제보 / 모니터링 발견

2. 입력을 받으면 `docs/runbooks/` 디렉토리에 아래 형식으로 파일을 생성해:
   - 파일명: `YYYY-MM-DD-{제목을-kebab-case로}.md` (오늘 날짜 기준)

## Runbook 파일 형식

```markdown
# [P{심각도}] {장애 제목}

| 항목 | 내용 |
|------|------|
| 작성일 | {오늘 날짜} |
| 심각도 | P{번호} |
| 감지 방법 | {감지 방법} |
| 상태 | 🔴 진행 중 |

## 타임라인

| 시각 | 이벤트 |
|------|--------|
| HH:MM | 장애 감지 |
| HH:MM | (여기에 추가) |

## 영향 범위

- 영향받는 서비스:
- 영향받는 사용자 수 (추정):
- 비즈니스 임팩트:

## 원인 분석 (5 Whys)

1. Why: → 증상
2. Why: → 직접 원인
3. Why: → 근본 원인
4. Why:
5. Why:

**근본 원인 (Root Cause):**

## 대응 절차

### 즉각 조치 (Immediate Action)
```bash
# 현재 파드 상태 확인
kubectl get pods -n devops-starter

# 로그 확인
kubectl logs -n devops-starter deployment/devops-starter-api --tail=100

# 롤백 (필요시)
kubectl rollout undo deployment/devops-starter-api -n devops-starter
```

### 임시 조치 (Mitigation)
- [ ] 

### 근본 해결 (Resolution)
- [ ] 

## 재발 방지 (Action Items)

| 항목 | 담당 | 기한 | 상태 |
|------|------|------|------|
| | | | 🔲 |

## 사후 검토 (Postmortem)

- **잘된 점:**
- **개선할 점:**
- **모니터링 개선 필요 여부:**
```

3. 파일 생성 후 장애 유형에 맞는 Prometheus 쿼리도 제안해줘:
   - Error Rate: `sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`
   - p99 Latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
   - 파드 재시작 수: `kube_pod_container_status_restarts_total{namespace="devops-starter"}`

## 규칙
- `docs/runbooks/` 디렉토리가 없으면 생성해
- 파일 생성 후 경로를 알려줘
