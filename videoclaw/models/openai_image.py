"""OpenAI image backend placeholder implementation."""
from __future__ import annotations

from typing import Any, Dict

from videoclaw.models.base import ImageBackend
from videoclaw.models.gemini.image import GeminiImageBackend


class OpenAIImageBackend(ImageBackend):
    """当前阶段复用 Gemini backend 作为 openai-image 的过渡实现。"""

    backend_name = "openai-image"
    auth_source = "api_key"
    execution_surface = "openai_api"
    billing_expectation = "api_billed"

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model or "gpt-image-1"
        self.config = config
        self._delegate = GeminiImageBackend(config.get("fallback_model") or "gemini-2.5-flash-image", config)

    def text_to_image(self, prompt: str, **kwargs):
        result = self._delegate.text_to_image(prompt, **kwargs)
        result.metadata = {
            **(result.metadata or {}),
            "backend": self.backend_name,
            "requested_model": self.model,
            "fallback_backend": "gemini",
        }
        return result

    def image_to_image(self, image: bytes, prompt: str, **kwargs):
        result = self._delegate.image_to_image(image, prompt, **kwargs)
        result.metadata = {
            **(result.metadata or {}),
            "backend": self.backend_name,
            "requested_model": self.model,
            "fallback_backend": "gemini",
        }
        return result
