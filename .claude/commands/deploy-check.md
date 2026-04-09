배포 전 체크리스트를 순서대로 실행하고 결과를 리포트해줘.

## 체크 항목

### 1. 코드 품질
- `services/` 아래 모든 Python 코드에 `ruff check` 실행
- `mypy` 타입 검사 실행
- 오류가 있으면 내용을 출력하고 중단하지 말고 계속 진행해 (전체 결과를 모아서 보고)

### 2. 테스트
- `services/` 아래 각 서비스의 pytest 실행
- 커버리지가 70% 미만이면 경고 표시

### 3. Docker 빌드 검증
- `services/` 아래 각 Dockerfile을 `docker build --no-cache` 로 빌드 시도
- 빌드 성공 여부와 이미지 크기 출력

### 4. Kubernetes 매니페스트 검증
- `kubectl apply --dry-run=client -f kubernetes/base/` 실행
- 오류가 있으면 어느 파일의 어느 부분인지 명시

### 5. 보안 체크
- `kubernetes/base/deployment.yaml` 파일들에서 아래 항목이 있는지 확인:
  - `runAsNonRoot: true`
  - `readOnlyRootFilesystem: true`
  - `resources.limits` 설정
  - `livenessProbe` / `readinessProbe`
- 누락된 항목은 경고로 표시

### 6. .env 파일 점검
- `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- `.env` 파일이 git에 스테이징되어 있지 않은지 확인

## 최종 리포트 형식

체크가 끝나면 아래 형식으로 요약해줘:

```
=== 배포 전 체크 결과 ===

✅ 통과 항목
- ...

⚠️ 경고 항목
- ...

❌ 실패 항목
- ...

배포 가능 여부: YES / NO (실패 항목이 없으면 YES)
```
