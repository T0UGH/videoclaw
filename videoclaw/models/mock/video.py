"""Mock 视频后端"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import GenerationResult, VideoBackend


class MockVideoBackend(VideoBackend):
    """用于测试的 Mock 视频后端"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.config = config

    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        # 创建一个空的测试视频文件
        path = Path(f"/tmp/mock_video_{hash(prompt)}.mp4")
        path.write_bytes(b"mock video")
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"duration": 5, "format": "mp4"}
        )
