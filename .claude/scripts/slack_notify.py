#!/usr/bin/env python3
"""
Claude Code → Slack 알림 스크립트
사용법: python slack_notify.py [permission|complete]
stdin: Claude Code hook JSON 데이터
"""
import sys
import json
import os
import urllib.request
import urllib.error
from datetime import datetime


def _load_env_file() -> None:
    """프로젝트 루트의 .env 파일에서 환경변수를 로드한다."""
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    env_path = os.path.normpath(env_path)
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_env_file()
WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")


def send_slack(payload: dict) -> None:
    if not WEBHOOK_URL:
        sys.stderr.write("SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.\n")
        sys.exit(1)

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.URLError as e:
        sys.stderr.write(f"Slack 전송 실패: {e}\n")


def build_permission_message(hook_data: dict) -> dict:
    tool_name = hook_data.get("tool_name", "unknown")
    tool_input = hook_data.get("tool_input", {})
    cwd = hook_data.get("cwd", "")
    now = datetime.now().strftime("%H:%M:%S")

    detail = ""
    if isinstance(tool_input, dict):
        cmd = tool_input.get("command") or tool_input.get("file_path") or ""
        if cmd:
            detail = f"\n> `{str(cmd)[:120]}`"

    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🔐 Claude Code 권한 요청"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*도구*\n`{tool_name}`"},
                    {"type": "mrkdwn", "text": f"*시각*\n{now}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*경로*: `{cwd}`{detail}",
                },
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "Claude Code가 승인을 기다리고 있습니다."}
                ],
            },
        ]
    }


def build_complete_message(hook_data: dict) -> dict:
    cwd = hook_data.get("cwd", "")
    now = datetime.now().strftime("%H:%M:%S")

    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "✅ Claude Code 작업 완료"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*경로*\n`{cwd}`"},
                    {"type": "mrkdwn", "text": f"*시각*\n{now}"},
                ],
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "응답이 완료되어 입력을 기다립니다."}
                ],
            },
        ]
    }


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "complete"

    try:
        hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        hook_data = {}

    if mode == "permission":
        payload = build_permission_message(hook_data)
    else:
        payload = build_complete_message(hook_data)

    send_slack(payload)


if __name__ == "__main__":
    main()
