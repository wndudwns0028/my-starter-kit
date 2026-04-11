# GitHub MCP 서버 연동 과정 기록

## 1. 전체 흐름

### 목표
Claude Code에서 GitHub API를 직접 호출할 수 있도록 MCP(Model Context Protocol) 서버를 연동한다.
이를 통해 Issue 생성, PR 리뷰, 코드 검색 등을 Claude 대화 내에서 바로 수행할 수 있게 된다.

### 구성 요소

```
GitHub PAT (Personal Access Token)
  └─ Windows 사용자 환경변수에 등록
       └─ ~/.bashrc → GITHUB_PERSONAL_ACCESS_TOKEN export
            └─ Claude Code 실행 (환경변수 상속)
                 └─ .mcp.json 로드
                      └─ npx @modelcontextprotocol/server-github 실행 (환경변수 자동 상속)
                           └─ Claude가 GitHub API 도구 사용 가능
```

### 생성/수정된 파일

| 파일 | 역할 |
|------|------|
| `.mcp.json` | Claude Code가 시작 시 자동으로 읽는 MCP 서버 설정 파일 |
| `.env.example` | `GITHUB_PERSONAL_ACCESS_TOKEN` 발급 및 등록 가이드 추가 |
| `.claude/scripts/lint_check.py` | 오타 수정 (별도 작업 중 발생) |

### `.mcp.json` 최종 내용

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@modelcontextprotocol/server-github"
      ]
    }
  }
}
```

- `type: stdio` — npx 프로세스와 표준 입출력으로 통신
- `command: cmd /c npx` — Windows 환경에서 npx 실행을 위해 `cmd /c` 래퍼 사용
- `-y` — 패키지 설치 프롬프트 자동 승인

### GitHub PAT 등록 방법

```powershell
# PowerShell에서 Windows 사용자 환경변수로 등록
[System.Environment]::SetEnvironmentVariable(
  "GITHUB_PERSONAL_ACCESS_TOKEN",
  "ghp_xxx...",
  "User"
)
```

```bash
# ~/.bashrc에 추가 (Git Bash / WSL 환경)
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxx..."
```

**필요 권한 (Fine-grained token 기준):**
- Contents: Read
- Issues: Read & Write
- Pull requests: Read & Write
- Metadata: Read
- Actions: Read

---

## 2. 문제가 있었던 부분

### 문제 1 — `.mcp.json`에 `env` 블록 없이도 토큰이 인식되는가?

초기에 `.mcp.json`에 아래처럼 `env` 블록을 추가해야 하는지 불명확했다.

```json
// 이 방식이 필요한가?
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

**원인:** MCP 서버 프로세스(npx)가 부모 프로세스(Claude Code)의 환경변수를 상속받는 방식이
명확하지 않아 혼동이 발생했다.

---

### 문제 2 — Windows에서 `npx` 직접 실행 실패

`.mcp.json`에서 `command: "npx"`로 설정했을 때 Windows 환경에서 실행이 되지 않는 문제가 있었다.

```json
// 실패한 설정
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"]
}
```

**원인:** Windows에서는 `npx`가 `.cmd` 확장자를 통해 실행되므로 셸 없이 직접 바이너리를
호출하면 인식하지 못한다.

---

### 문제 3 — `lint_check.py` 오타 혼입

`.claude/scripts/lint_check.py` 14번째 줄에 한글 자모 `ㅁ`이 코드에 혼입됐다.

```python
# 오타가 포함된 상태
hook_data = json.load(sys.stdin)ㅁ
```

**원인:** 파일 편집 중 한영 전환 오류로 인해 자모가 삽입됐다.
Python 문법 오류를 유발하므로 hook 자체가 실행 불가 상태였다.

---

## 3. 수정 방법

### 해결 1 — `env` 블록 없이 환경변수 상속 활용

MCP 서버 프로세스는 Claude Code로부터 환경변수를 자동으로 상속받는다.
따라서 `.mcp.json`에 토큰을 하드코딩하는 `env` 블록은 불필요하며,
오히려 토큰이 파일에 노출되는 보안 위험이 생긴다.

**결론:** Windows 사용자 환경변수 또는 `~/.bashrc`에 등록하면 `.mcp.json`에는 별도 `env` 설정 없이 동작한다.

```
Windows 환경변수 등록
  → Claude Code 실행 시 환경변수 상속
    → npx 프로세스도 동일하게 상속
      → GITHUB_PERSONAL_ACCESS_TOKEN 자동 인식
```

---

### 해결 2 — `cmd /c npx`로 Windows 호환성 확보

Windows 환경에서 npx를 안정적으로 실행하기 위해 `cmd /c` 래퍼를 사용했다.

```json
// 수정 후 (.mcp.json)
{
  "command": "cmd",
  "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-github"]
}
```

`cmd /c`는 명령어 실행 후 셸을 종료하므로 MCP stdio 통신에 영향을 주지 않는다.

---

### 해결 3 — `lint_check.py` 오타 제거

Claude Code의 `Edit` 도구를 사용해 혼입된 `ㅁ` 문자를 제거했다.

```python
# 수정 전
hook_data = json.load(sys.stdin)ㅁ

# 수정 후
hook_data = json.load(sys.stdin)
```

git diff 상으로는 원본 상태로 복구된 것이므로 최종 커밋에서 변경 파일로 포함되지 않았다.

---

## 커밋 히스토리

```
47caeec feat(mcp): GitHub MCP 서버 설정 및 환경변수 예시 추가
a6ef9f9 feat(claude): Slack 알림 및 ruff lint 자동 검사 hook 추가
277bb4f feat(claude): SRE On-call Assistant 에이전트 추가
1e8fb5b feat(claude): DevOps/SRE 워크플로우 자동화 커맨드 3종 추가
90ecaa7 feat: DevOps/SRE Starter Kit 초기 구성
```
