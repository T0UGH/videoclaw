"""Mock 图像后端"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import GenerationResult, ImageBackend


class MockImageBackend(ImageBackend):
    """用于测试的 Mock 图像后端"""

    backend_name = "mock"
    auth_source = "none"
    execution_surface = "local_mock"
    billing_expectation = "none"

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.config = config

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        path = Path(f"/tmp/mock_image_{hash(prompt)}.png")
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
            b"\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc``\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00"
            b"\x18\xdd\x8d\xb1"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        path.write_bytes(png_bytes)
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"width": 1, "height": 1, "format": "png"},
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        return self.text_to_image(prompt, **kwargs)
