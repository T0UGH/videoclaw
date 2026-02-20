"""字节系 Seedream 图像生成后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from volcenginesdkarkruntime import Ark

from videoclaw.models.base import GenerationResult, ImageBackend
from videoclaw.utils.logging import get_logger

logger = get_logger(name="volcengine.seedream")


class VolcEngineSeedream(ImageBackend):
    """字节系 Seedream 图像生成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        # 支持多种配置格式：Config对象或普通字典
        # 字典格式: {'ark': {'api_key': ...}} 或 {'api_key': ...}
        if isinstance(config, dict):
            self.api_key = (
                config.get("ark", {}).get("api_key") or
                config.get("api_key") or
                config.get("ak")
            )
            self.region = config.get("ark", {}).get("region") or config.get("region", "cn-beijing")
        else:
            # Config object
            self.api_key = config.get("ark.api_key") or config.get("api_key") or config.get("ak")
            self.region = config.get("region", "cn-beijing")
        if not self.api_key:
            raise ValueError(
                "VolcEngine ARK API Key is required. "
                "Set via config or environment variable ARK_API_KEY"
            )

        # 初始化 SDK
        self.client = Ark(
            base_url=f"https://ark.{self.region}.volces.com/api/v3",
            api_key=self.api_key,
        )

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        logger.info(f"开始生成图片，prompt: {prompt[:50]}...")

        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"seedream_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 调用 Seedream API
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=kwargs.get("size", "2K"),
                response_format="url",
                watermark=kwargs.get("watermark", False),
            )

            # 下载图片
            image_url = response.data[0].url
            import requests
            image_data = requests.get(image_url).content
            local_path.write_bytes(image_data)

            logger.info(f"图片生成成功: {local_path}")
        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            raise

        return GenerationResult(
            local_path=local_path,
            cloud_url=image_url,
            metadata={
                "provider": "volcengine",
                "model": self.model,
                "prompt": prompt,
            }
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        # 临时保存输入图片
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image)
            tmp_path = tmp.name

        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                image=tmp_path,
                size=kwargs.get("size", "2K"),
                response_format="url",
                watermark=kwargs.get("watermark", False),
            )

            # 下载结果图片
            image_url = response.data[0].url
            import requests
            image_data = requests.get(image_url).content

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
            filename = f"seedream_i2i_{timestamp}_{hash_suffix}.png"
            local_path = Path.home() / "videoclaw-projects" / "temp" / filename
            local_path.write_bytes(image_data)

            return GenerationResult(
                local_path=local_path,
                cloud_url=image_url,
                metadata={
                    "provider": "volcengine",
                    "model": self.model,
                    "prompt": prompt,
                }
            )
        finally:
            os.unlink(tmp_path)
