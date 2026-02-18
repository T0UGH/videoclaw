"""阿里系 DashScope TTS 后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import AudioBackend, GenerationResult


class DashScopeTTS(AudioBackend):
    """阿里系 DashScope 语音合成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.api_key = config.get("api_key")

    def text_to_speech(self, text: str, voice: str = "xiaoyuan", **kwargs) -> GenerationResult:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(text.encode()).hexdigest()[:6]
        filename = f"tts_{timestamp}_{hash_suffix}.mp3"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 DashScope API
        local_path.write_bytes(b"mock_dashscope_tts")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "dashscope", "model": self.model, "voice": voice}
        )
