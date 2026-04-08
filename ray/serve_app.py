"""Ray Serve를 사용한 LLM 추론 서빙 앱."""

import os
from typing import Any

import ray
from fastapi import FastAPI
from ray import serve

from vellum_client import VellumPromptManager

app = FastAPI(title="Ray LLM Serving API")


@serve.deployment(
  name="llm-deployment",
  num_replicas=1,
  ray_actor_options={
    "num_gpus": 1,          # GPU 1개 요청 (로컬 GPU 또는 K8s GPU 노드)
    "num_cpus": 4,
    "memory": 8 * 1024**3,  # 8GB RAM
  },
  autoscaling_config={
    "min_replicas": 0,      # 트래픽 없을 때 0으로 스케일다운 (비용 절감)
    "max_replicas": 4,
    "target_num_ongoing_requests_per_replica": 5,
  },
)
@serve.ingress(app)
class LLMDeployment:
  """GPU 기반 LLM 추론 서버.

  Vellum으로 프롬프트 버전관리, Ray Serve로 GPU 분산 추론.
  """

  def __init__(self):
    self.vellum = VellumPromptManager()
    self._model = None
    self._load_model()

  def _load_model(self):
    """모델 로드 (HuggingFace Hub에서 다운로드 또는 로컬 경로)."""
    model_name = os.environ.get("MODEL_NAME", "microsoft/DialoGPT-small")
    try:
      from transformers import AutoModelForCausalLM, AutoTokenizer
      import torch

      device = "cuda" if torch.cuda.is_available() else "cpu"
      self._tokenizer = AutoTokenizer.from_pretrained(model_name)
      self._model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
      ).to(device)
      self._device = device
      print(f"모델 '{model_name}' 로드 완료 (device: {device})")
    except Exception as e:
      print(f"모델 로드 실패: {e}. Mock 모드로 실행합니다.")
      self._model = None

  @app.post("/generate")
  async def generate(self, request: dict[str, Any]) -> dict[str, Any]:
    """텍스트 생성 엔드포인트.

    Args:
      request: {"prompt": "질문", "vellum_deployment": "my-prompt-v1", "max_tokens": 200}
    """
    prompt_text = request.get("prompt", "")
    vellum_deployment = request.get("vellum_deployment")
    max_tokens = request.get("max_tokens", 200)

    # Vellum 프롬프트 템플릿 적용 (배포 이름이 있는 경우)
    if vellum_deployment:
      prompt_text = self.vellum.execute(
        deployment_name=vellum_deployment,
        inputs={"user_input": prompt_text},
      )

    # 모델 추론
    if self._model is None:
      # Mock 응답 (개발/테스트용)
      return {
        "generated_text": f"[Mock] 입력: {prompt_text[:50]}...",
        "model": "mock",
        "device": "cpu",
      }

    import torch

    inputs = self._tokenizer.encode(prompt_text, return_tensors="pt").to(self._device)
    with torch.no_grad():
      outputs = self._model.generate(
        inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        temperature=0.7,
        pad_token_id=self._tokenizer.eos_token_id,
      )
    generated = self._tokenizer.decode(outputs[0], skip_special_tokens=True)

    return {
      "generated_text": generated,
      "model": os.environ.get("MODEL_NAME", "unknown"),
      "device": self._device,
    }

  @app.get("/health")
  async def health(self) -> dict[str, str]:
    """서빙 헬스체크."""
    return {"status": "ok", "gpu_available": str(self._device if self._model else "N/A")}


# Ray Serve 배포 진입점
if __name__ == "__main__":
  ray.init(address=os.environ.get("RAY_ADDRESS", "auto"))
  serve.start(detached=True, http_options={"host": "0.0.0.0", "port": 8001})

  deployment = LLMDeployment.bind()
  serve.run(deployment, route_prefix="/")
  print("Ray Serve LLM 서빙 시작: http://0.0.0.0:8001")
