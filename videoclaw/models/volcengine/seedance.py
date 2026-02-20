"""字节系 Seedance 视频生成后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from volcenginesdkarkruntime import Ark

from videoclaw.models.base import GenerationResult, VideoBackend
from videoclaw.utils.logging import get_logger

logger = get_logger(name="volcengine.seedance")


class VolcEngineSeedance(VideoBackend):
    """字节系 Seedance 视频生成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        # 支持多种配置格式：Config对象或普通字典
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

        self.client = Ark(
            base_url=f"https://ark.{self.region}.volces.com/api/v3",
            api_key=self.api_key,
        )

    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        logger.info(f"开始生成视频，prompt: {prompt[:50]}...")

        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"seedance_{timestamp}_{hash_suffix}.mp4"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # 将图片转换为 base64 data URL
        import base64
        import io
        from PIL import Image

        # 读取图片并转换为 base64，确保尺寸足够
        img = Image.open(io.BytesIO(image))
        # 确保图片宽度至少 300px（API 要求）
        min_size = 300
        if img.width < min_size or img.height < min_size:
            # 放大图片
            scale = max(min_size / img.width, min_size / img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"图片尺寸已调整: {img.width}x{img.height}")
        buffered = io.BytesIO()
        img_format = img.format or "PNG"
        img.save(buffered, format=img_format)
        img_bytes = buffered.getvalue()
        b64_img = base64.b64encode(img_bytes).decode('utf-8')
        data_url = f"data:image/{img_format.lower()};base64,{b64_img}"

        try:
            # Step 1: 创建异步任务 (使用 base64 data URL)
            logger.debug(f"创建视频生成任务，model: {self.model}")
            response = self.client.content_generation.tasks.create(
                model=self.model,
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
                ratio=kwargs.get("ratio", "16:9"),
                # resolution 参数仅在文生视频时有效，图生视频时不传
                # resolution=kwargs.get("resolution"),
                duration=kwargs.get("duration", 5),
                watermark=kwargs.get("watermark", False),
                generate_audio=kwargs.get("generate_audio", False),
            )

            task_id = response.id
            logger.info(f"视频生成任务已创建，task_id: {task_id}")

            # Step 2: 轮询等待任务完成
            max_wait = kwargs.get("max_wait", 300)  # 默认 5 分钟
            poll_interval = kwargs.get("poll_interval", 5)

            import time as time_module
            start_time = time_module.time()

            while time_module.time() - start_time < max_wait:
                task = self.client.content_generation.tasks.get(task_id=task_id)
                logger.debug(f"任务状态: {task.status}")

                if task.status == "succeeded":
                    # 下载视频
                    video_url = task.content.video_url
                    logger.info(f"视频生成成功，下载视频...")
                    import requests
                    video_data = requests.get(video_url).content
                    local_path.write_bytes(video_data)

                    return GenerationResult(
                        local_path=local_path,
                        cloud_url=video_url,
                        metadata={
                            "provider": "volcengine",
                            "model": self.model,
                            "prompt": prompt,
                            "task_id": task_id,
                        }
                    )
                elif task.status == "failed":
                    error_msg = task.error.message if task.error else "Unknown error"
                    logger.error(f"视频生成失败: {error_msg}")
                    raise RuntimeError(f"Video generation failed: {error_msg}")
                else:
                    # queued 或 running，继续等待
                    logger.debug(f"等待视频生成中...")
                    time_module.sleep(poll_interval)

            logger.error(f"视频生成超时: {max_wait} 秒")
            raise TimeoutError(f"Video generation timeout after {max_wait} seconds")

        except Exception as e:
            logger.error(f"视频生成异常: {e}")
            raise
        finally:
            # 清理临时图片文件
            import os
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
