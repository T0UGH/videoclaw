"""阿里系 DashScope I2V 后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import GenerationResult, VideoBackend


class DashScopeI2V(VideoBackend):
    """阿里系 DashScope 图生视频"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("DashScope API key is required. Set via config or environment variable DASHSCOPE_API_KEY")

    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"i2v_{timestamp}_{hash_suffix}.mp4"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 DashScope API
        local_path.write_bytes(b"mock_dashscope_video")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "dashscope", "model": self.model}
        )
