"""阿里系 DashScope T2I 后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import GenerationResult, ImageBackend


class DashScopeT2I(ImageBackend):
    """阿里系 DashScope 文生图"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.api_key = config.get("api_key")

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"t2i_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 DashScope API
        local_path.write_bytes(b"mock_dashscope_image")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "dashscope", "model": self.model}
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        return self.text_to_image(prompt, **kwargs)
