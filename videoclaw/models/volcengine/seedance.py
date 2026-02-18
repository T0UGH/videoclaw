"""字节系 Seedance 视频生成后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import GenerationResult, VideoBackend


class VolcEngineSeedance(VideoBackend):
    """字节系 Seedance 视频生成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.ak = config.get("ak")
        self.sk = config.get("sk")
        self.region = config.get("region", "cn-beijing")
        if not self.ak or not self.sk:
            raise ValueError("VolcEngine AK/SK is required. Set via config or environment variables VOLCENGINE_AK/VOLCENGINE_SK")

    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"seedance_{timestamp}_{hash_suffix}.mp4"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 VolcEngine Seedance API
        local_path.write_bytes(b"mock_seedance_video")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "volcengine", "model": self.model, "prompt": prompt}
        )
