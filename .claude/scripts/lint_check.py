#!/usr/bin/env python3
"""
PostToolUse Hook: Python 파일 수정 후 ruff lint 자동 실행
Edit/Write 도구로 services/api/app/*.py 수정 시 ruff check 결과를 Claude에게 피드백한다.
"""
import sys
import json
import os
import subprocess


def main():
    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path = hook_data.get("tool_input", {}).get("file_path", "")

    # services/api/app/ 하위 .py 파일만 대상
    if not file_path.endswith(".py"):
        sys.exit(0)

    normalized = file_path.replace("\\", "/")
    if "services/api/app/" not in normalized:
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    result = subprocess.run(
        ["ruff", "check", file_path],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        sys.exit(0)

    # lint 오류가 있으면 Claude에게 결과 전달
    output = result.stdout.strip() or result.stderr.strip()
    feedback = {
        "additionalContext": f"ruff lint 오류가 발견됐습니다. 수정해주세요:\n{output}"
    }
    print(json.dumps(feedback))
    sys.exit(0)


if __name__ == "__main__":
    main()
