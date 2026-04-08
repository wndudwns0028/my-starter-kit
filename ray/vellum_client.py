"""Vellum 프롬프트 버전관리 클라이언트."""

import os
from functools import lru_cache

import vellum  # pip install vellum-ai


class VellumPromptManager:
  """Vellum을 통한 LLM 프롬프트 버전관리 및 실행."""

  def __init__(self):
    api_key = os.environ.get("VELLUM_API_KEY")
    if not api_key:
      raise ValueError("VELLUM_API_KEY 환경변수가 설정되지 않았습니다.")
    self.client = vellum.Vellum(api_key=api_key)

  @lru_cache(maxsize=20)
  def get_deployment_info(self, deployment_name: str) -> dict:
    """배포된 프롬프트 정보 조회 (캐싱으로 반복 API 호출 방지)."""
    deployment = self.client.deployments.retrieve(deployment_name)
    return {
      "name": deployment.name,
      "status": deployment.status,
      "model": deployment.active_model_version_ids,
    }

  def execute(self, deployment_name: str, inputs: dict[str, str]) -> str:
    """Vellum 프롬프트 워크플로우 실행.

    Args:
      deployment_name: Vellum에 배포된 프롬프트 이름
      inputs: 프롬프트 변수 딕셔너리

    Returns:
      LLM 응답 텍스트
    """
    vellum_inputs = [
      vellum.StringInputRequest(name=k, value=v) for k, v in inputs.items()
    ]
    result = self.client.execute_prompt(
      prompt_deployment_name=deployment_name,
      inputs=vellum_inputs,
    )

    if result.state == "FULFILLED":
      # 첫 번째 OUTPUT 값 반환
      for output in result.outputs:
        if hasattr(output, "value"):
          return str(output.value)

    raise RuntimeError(f"Vellum 실행 실패: {result.state}")

  def execute_workflow(self, workflow_deployment_name: str, inputs: dict) -> dict:
    """Vellum 워크플로우 실행 (복잡한 멀티스텝 파이프라인용)."""
    result = self.client.execute_workflow(
      workflow_deployment_name=workflow_deployment_name,
      inputs=[
        {"name": k, "type": "STRING", "value": str(v)} for k, v in inputs.items()
      ],
    )
    return {"state": result.data.state, "outputs": result.data.outputs}
