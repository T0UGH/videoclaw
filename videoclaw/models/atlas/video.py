"""Atlas Cloud 视频生成后端"""
from __future__ import annotations

import base64
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List

from videoclaw.models.atlas.client import AtlasClient, resolve_api_key, resolve_base_url
from videoclaw.models.base import GenerationResult, VideoBackend
from videoclaw.utils.logging import get_logger

logger = get_logger(name="atlas.video")

DEFAULT_I2V_MODEL = "bytedance/seedance-2.0/image-to-video"


class AtlasVideoBackend(VideoBackend):
    """Atlas Cloud 视频生成（Seedance 2.0 等）"""

    backend_name = "atlas"
    auth_source = "api_key"
    execution_surface = "provider_api"
    billing_expectation = "api_billed"

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model or DEFAULT_I2V_MODEL
        api_key = resolve_api_key(config)
        if not api_key:
            raise ValueError(
                "Atlas Cloud API Key is required. "
                "Set via config (atlas.api_key) or environment variable ATLASCLOUD_API_KEY"
            )
        self.client = AtlasClient(api_key, resolve_base_url(config))

    def image_to_video(
        self,
        images: bytes | List[bytes],
        prompt: str,
        video_refs: list[str] = None,
        audio_refs: list[str] = None,
        **kwargs,
    ) -> GenerationResult:
        logger.info(f"开始生成视频，prompt: {prompt[:50]}...")
        if video_refs:
            # Atlas 的 images 字段只收图片，参考视频没有对应位置，宁可报错也不静默丢掉
            raise ValueError("Atlas backend does not accept video references (images field is image-only)")
        if audio_refs:
            raise ValueError("Atlas backend does not accept audio references (images field is image-only)")

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        local_path = Path.home() / "videoclaw-projects" / "temp" / f"atlas_i2v_{timestamp}_{hash_suffix}.mp4"
        local_path.parent.mkdir(parents=True, exist_ok=True)

        frames = images if isinstance(images, list) else [images]
        encoded = [
            f"data:image/png;base64,{base64.b64encode(frame).decode('utf-8')}" for frame in frames
        ]

        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            # 传空串会被接口拒掉，所以显式给值
            "shot_type": kwargs.get("shot_type", "single"),
            # Seedance 2.0 默认生成同步音频，配乐撞版权校验会让整条任务 failed，
            # 所以默认关掉，需要时显式打开
            "generate_audio": kwargs.get("generate_audio", False),
        }
        if encoded:
            # 多图用换行分隔，第一张是首帧
            payload["images"] = "\n".join(encoded)
        if kwargs.get("size"):
            size = kwargs["size"]
            payload["size"] = size.replace("x", "*") if "x" in size else size
        if kwargs.get("duration"):
            payload["duration"] = kwargs["duration"]
        if kwargs.get("seed") is not None:
            payload["seed"] = kwargs["seed"]

        try:
            saved = self.client.run("generateVideo", payload, local_path)
        except Exception as e:
            logger.error(f"视频生成失败: {e}")
            raise
        logger.info(f"视频生成成功: {saved}")
        return GenerationResult(
            local_path=saved,
            metadata={"model": self.model, "backend": self.backend_name, "prompt": prompt},
        )
