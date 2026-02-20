"""字节系 TTS 语音合成后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import AudioBackend, GenerationResult
from videoclaw.utils.logging import get_logger

logger = get_logger(name="volcengine.tts")


class VolcEngineTTS(AudioBackend):
    """字节系 TTS 语音合成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.ak = config.get("ak")
        self.sk = config.get("sk")
        self.region = config.get("region", "cn-beijing")
        if not self.ak or not self.sk:
            raise ValueError("VolcEngine AK/SK is required. Set via config or environment variables VOLCENGINE_AK/VOLCENGINE_SK")

    def text_to_speech(self, text: str, voice: str = "xiaoyuan", **kwargs) -> GenerationResult:
        logger.info(f"开始生成语音，text: {text[:50]}...")

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(text.encode()).hexdigest()[:6]
        filename = f"tts_{timestamp}_{hash_suffix}.mp3"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 VolcEngine TTS API
        local_path.write_bytes(b"mock_tts_audio")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "volcengine", "model": self.model, "voice": voice}
        )
