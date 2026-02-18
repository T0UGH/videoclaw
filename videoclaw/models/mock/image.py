"""Mock 图像后端"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict

from PIL import Image

from videoclaw.models.base import GenerationResult, ImageBackend


class MockImageBackend(ImageBackend):
    """用于测试的 Mock 图像后端"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.config = config

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        # 创建一个简单的测试图片
        img = Image.new("RGB", (1024, 576), color=(100, 150, 200))
        path = Path(f"/tmp/mock_image_{hash(prompt)}.png")
        img.save(path)
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"width": 1024, "height": 576, "format": "png"}
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        return self.text_to_image(prompt, **kwargs)
