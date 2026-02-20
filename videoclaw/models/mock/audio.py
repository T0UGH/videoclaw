"""Mock 音频后端"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import AudioBackend, GenerationResult


class MockAudioBackend(AudioBackend):
    """用于测试的 Mock 音频后端"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.config = config

    def text_to_speech(self, text: str, voice: str = "default", **kwargs) -> GenerationResult:
        path = Path(f"/tmp/mock_audio_{hash(text)}.mp3")
        path.write_bytes(b"mock audio")
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"duration": 3, "format": "mp3", "voice": voice}
        )

    def generate_bgm(self, style: str = "ambient", duration: int = 30, **kwargs) -> GenerationResult:
        path = Path(f"/tmp/mock_bgm_{hash(style)}.mp3")
        path.write_bytes(b"mock bgm")
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"duration": duration, "format": "mp3", "style": style}
        )
