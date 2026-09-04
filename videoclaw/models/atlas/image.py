"""Atlas Cloud 图像生成后端"""
from __future__ import annotations

import base64
import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.atlas.client import AtlasClient, resolve_api_key, resolve_base_url
from videoclaw.models.base import GenerationResult, ImageBackend
from videoclaw.utils.logging import get_logger

logger = get_logger(name="atlas.image")

DEFAULT_T2I_MODEL = "bytedance/seedream-v4"
# 图生图换任务后缀；调用名形如 厂商/模型/任务
I2I_SUFFIX = "/edit"


class AtlasImageBackend(ImageBackend):
    """Atlas Cloud 图像生成

    尺寸参数按模型而异（实测）：seedream 系列精确遵守 `size`（宽*高），
    nano-banana 系列忽略 `size`、只认 `aspect_ratio`，所以这里按模型名分流。
    """

    backend_name = "atlas"
    auth_source = "api_key"
    execution_surface = "provider_api"
    billing_expectation = "api_billed"

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model or DEFAULT_T2I_MODEL
        api_key = resolve_api_key(config)
        if not api_key:
            raise ValueError(
                "Atlas Cloud API Key is required. "
                "Set via config (atlas.api_key) or environment variable ATLASCLOUD_API_KEY"
            )
        self.client = AtlasClient(api_key, resolve_base_url(config))

    def _local_path(self, prompt: str, tag: str) -> Path:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"atlas_{tag}_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)
        return local_path

    def _size_payload(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        size = kwargs.get("size")
        aspect_ratio = kwargs.get("aspect_ratio")
        if "nano-banana" in self.model:
            # 实测该系列忽略 size，只认 aspect_ratio
            if size and not aspect_ratio:
                logger.info(f"{self.model} 忽略 size，改用 aspect_ratio")
            return {"aspect_ratio": aspect_ratio or "1:1"}
        payload: Dict[str, Any] = {}
        if size:
            # 兼容 1024x1024 写法：Atlas 要的是 宽*高
            payload["size"] = size.replace("x", "*") if "x" in size else size
        if aspect_ratio:
            payload["aspect_ratio"] = aspect_ratio
        return payload

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        logger.info(f"开始生成图片，prompt: {prompt[:50]}...")
        local_path = self._local_path(prompt, "t2i")
        payload = {"model": self.model, "prompt": prompt, **self._size_payload(kwargs)}
        try:
            saved = self.client.run("generateImage", payload, local_path)
        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            raise
        logger.info(f"图片生成成功: {saved}")
        return GenerationResult(
            local_path=saved,
            metadata={"model": self.model, "backend": self.backend_name, "prompt": prompt},
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        logger.info(f"开始图生图，prompt: {prompt[:50]}...")
        local_path = self._local_path(prompt, "i2i")
        model = kwargs.get("model") or self.model
        if not model.endswith(I2I_SUFFIX):
            # 文生图调用名换成对应的编辑任务
            model = model.rsplit("/", 1)[0] + I2I_SUFFIX
        # 输入图直接以 base64 data URI 传入 images 字段，多张用换行分隔
        encoded = base64.b64encode(image).decode("utf-8")
        payload = {
            "model": model,
            "prompt": prompt,
            "images": f"data:image/png;base64,{encoded}",
            **self._size_payload(kwargs),
        }
        try:
            saved = self.client.run("generateImage", payload, local_path)
        except Exception as e:
            logger.error(f"图生图失败: {e}")
            raise
        logger.info(f"图生图成功: {saved}")
        return GenerationResult(
            local_path=saved,
            metadata={"model": model, "backend": self.backend_name, "prompt": prompt},
        )
