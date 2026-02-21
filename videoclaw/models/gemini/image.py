"""Google Gemini 图像生成后端"""
from __future__ import annotations

import base64
import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from videoclaw.models.base import GenerationResult, ImageBackend
from videoclaw.utils.logging import get_logger

logger = get_logger(name="gemini.image")


class GeminiImageBackend(ImageBackend):
    """Google Gemini 图像生成后端 (Nano Banana)"""

    DEFAULT_MODEL = "gemini-3-pro-image-preview"

    SUPPORTED_MODELS = [
        # Gemini 3 Pro Image (Nano Banana Pro) - 质量优先
        "gemini-3-pro-image-preview",
        # Gemini 2.5 Flash Image (Nano Banana) - 速度优先
        "gemini-2.5-flash-image",  # 正式版
        "gemini-2.5-flash-image-preview",  # 预览版
        # Imagen 4 系列
        "imagen-4.0-generate-preview-06-06",
        "imagen-4.0-ultra-generate-preview-06-06",
    ]

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model or self.DEFAULT_MODEL
        if self.model not in self.SUPPORTED_MODELS:
            logger.warning(
                f"Model {self.model} not in known supported models: {self.SUPPORTED_MODELS}"
            )

        # 支持多种配置格式：Config对象或普通字典
        # 首先检查环境变量 GOOGLE_API_KEY (最高优先级)
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            # 然后检查 config 传入的 api_key 或 google.api_key
            # 兼容两种格式: config.get("api_key") 或 config.get("google.api_key")
            self.api_key = config.get("api_key") or config.get("google.api_key")

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

    def _extract_image_from_response(self, response) -> Optional[bytes]:
        """从 Gemini 响应中提取图片数据"""
        try:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        return part.inline_data.data
        except Exception as e:
            logger.error(f"提取图片数据失败: {e}")
        return None

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        logger.info(f"开始生成图片，prompt: {prompt[:50]}...")

        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"gemini_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            from google.genai import types

            # 使用 generate_content API (Nano Banana)
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                )
            )

            # 获取生成的图片
            image_data = self._extract_image_from_response(response)
            if image_data:
                local_path.write_bytes(image_data)
                logger.info(f"图片生成成功: {local_path}")
            else:
                raise ValueError("No images generated in response")

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
        if not image:
            raise ValueError("image parameter cannot be empty")

        logger.info(f"开始图生图，prompt: {prompt[:50]}...")

        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"gemini_i2i_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            from google.genai import types

            # 构建多模态内容
            contents = [
                types.Part.from_bytes(data=image, mime_type="image/png"),
                types.Part.from_text(text=prompt)
            ]

            # 使用 generate_content API 进行图生图
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                )
            )

            # 获取生成的图片
            image_data = self._extract_image_from_response(response)
            if image_data:
                local_path.write_bytes(image_data)
                logger.info(f"图生图成功: {local_path}")
            else:
                raise ValueError("No images generated in response")

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
