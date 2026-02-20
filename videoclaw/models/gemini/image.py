"""Google Gemini 图像生成后端"""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from videoclaw.models.base import GenerationResult, ImageBackend
from videoclaw.utils.logging import get_logger

logger = get_logger(name="gemini.image")


class GeminiImageBackend(ImageBackend):
    """Google Gemini 图像生成后端"""

    SUPPORTED_MODELS = [
        "gemini-2.0-flash-exp-image-generation",
        "imagen-3.0-fast",
        "imagen-3.0-generate-002",
    ]

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        if model not in self.SUPPORTED_MODELS:
            logger.warning(
                f"Model {model} not in known supported models: {self.SUPPORTED_MODELS}"
            )

        # 支持多种配置格式：Config对象或普通字典
        # 首先检查环境变量 GOOGLE_API_KEY
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            # 然后检查 config 传入的 api_key
            if isinstance(config, dict):
                self.api_key = config.get("api_key")
            else:
                # Config object
                self.api_key = config.get("api_key")

        if not self.api_key:
            raise ValueError(
                "Google Gemini API key is required. "
                "Set via config or environment variable GOOGLE_API_KEY"
            )

        self._client = None

    @property
    def client(self):
        """Lazy-loaded Google Generative AI client"""
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        logger.info(f"开始生成图片，prompt: {prompt[:50]}...")

        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"gemini_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 调用 Gemini API
            response = self.client.models.generate_images(
                model=self.model,
                prompt=prompt,
            )

            # 获取生成的图片
            if response.generated_images:
                image_data = response.generated_images[0].image.image_bytes
                local_path.write_bytes(image_data)
                logger.info(f"图片生成成功: {local_path}")
            else:
                raise ValueError("No images generated")

        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            raise

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={
                "provider": "gemini",
                "model": self.model,
                "prompt": prompt,
            }
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        logger.info(f"开始图生图，prompt: {prompt[:50]}...")

        import base64

        # 将图片转换为 base64
        b64_image = base64.b64encode(image).decode('utf-8')

        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"gemini_i2i_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 调用 Gemini API 进行图生图
            response = self.client.models.generate_images(
                model=self.model,
                prompt=prompt,
                image=b64_image,
            )

            # 获取生成的图片
            if response.generated_images:
                image_data = response.generated_images[0].image.image_bytes
                local_path.write_bytes(image_data)
                logger.info(f"图生图成功: {local_path}")
            else:
                raise ValueError("No images generated")

        except Exception as e:
            logger.error(f"图生图失败: {e}")
            raise

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={
                "provider": "gemini",
                "model": self.model,
                "prompt": prompt,
            }
        )
