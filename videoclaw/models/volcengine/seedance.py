"""字节系 Seedance 视频生成后端"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict

from volcenginesdkarkruntime import Ark

from videoclaw.models.base import GenerationResult, VideoBackend


class VolcEngineSeedance(VideoBackend):
    """字节系 Seedance 视频生成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.api_key = config.get("api_key") or config.get("ak")
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
        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"seedance_{timestamp}_{hash_suffix}.mp4"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # 临时保存输入图片
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image)
            tmp_path = tmp.name

        try:
            # Step 1: 创建异步任务
            response = self.client.content_generation.tasks.create(
                model=self.model,
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": tmp_path}}
                ],
                ratio=kwargs.get("ratio", "adaptive"),
                duration=kwargs.get("duration", 5),
                watermark=kwargs.get("watermark", False),
                generate_audio=kwargs.get("generate_audio", False),
            )

            task_id = response.id

            # Step 2: 轮询等待任务完成
            max_wait = kwargs.get("max_wait", 300)  # 默认 5 分钟
            poll_interval = kwargs.get("poll_interval", 5)

            import time as time_module
            start_time = time_module.time()

            while time_module.time() - start_time < max_wait:
                task = self.client.content_generation.tasks.get(task_id=task_id)

                if task.status == "succeeded":
                    # 下载视频
                    video_url = task.video.url
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
                    raise RuntimeError(f"Video generation failed: {error_msg}")
                else:
                    # queued 或 running，继续等待
                    time_module.sleep(poll_interval)

            raise TimeoutError(f"Video generation timeout after {max_wait} seconds")

        finally:
            os.unlink(tmp_path)
