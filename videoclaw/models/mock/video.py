"""Mock 视频后端"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import GenerationResult, VideoBackend


class MockVideoBackend(VideoBackend):
    """用于测试的 Mock 视频后端"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.config = config

    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        path = Path(f"/tmp/mock_video_{hash(prompt)}.mp4")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=black:s=1280x720:d=1",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    str(path),
                ],
                capture_output=True,
                check=True,
            )
        except Exception:
            path.write_bytes(b"mock video")
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"duration": 1, "format": "mp4"},
        )
