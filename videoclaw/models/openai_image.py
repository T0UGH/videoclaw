"""OpenAI image backend."""
from __future__ import annotations

import base64
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict

import requests

from videoclaw.models.base import GenerationResult, ImageBackend


class OpenAIImageBackend(ImageBackend):
    """使用 OpenAI 图片 API 的正式 backend。"""

    backend_name = "openai-image"
    auth_source = "api_key"
    execution_surface = "openai_api"
    billing_expectation = "api_billed"

    DEFAULT_MODEL = "gpt-image-1"

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model or self.DEFAULT_MODEL
        self.config = config
        self.api_key = os.environ.get("OPENAI_API_KEY") or config.get("openai.api_key") or config.get("api_key")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY or openai.api_key")

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": kwargs.get("size", "1024x1024"),
        }
        image_bytes = self._request_image(payload)
        local_path = self._build_output_path(prompt, prefix="openai")
        local_path.write_bytes(image_bytes)
        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={
                "backend": self.backend_name,
                "model": self.model,
                "prompt": prompt,
            },
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "image": base64.b64encode(image).decode("utf-8"),
            "size": kwargs.get("size", "1024x1024"),
        }
        image_bytes = self._request_image(payload)
        local_path = self._build_output_path(prompt, prefix="openai_i2i")
        local_path.write_bytes(image_bytes)
        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={
                "backend": self.backend_name,
                "model": self.model,
                "prompt": prompt,
            },
        )

    def _request_image(self, payload: Dict[str, Any]) -> bytes:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        image_b64 = data["data"][0].get("b64_json")
        if not image_b64:
            raise ValueError("OpenAI image response did not include b64_json")
        return base64.b64decode(image_b64)

    def _build_output_path(self, prompt: str, prefix: str) -> Path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"{prefix}_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)
        return local_path
