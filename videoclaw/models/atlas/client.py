"""Atlas Cloud 媒体接口客户端

图片和视频走的是同一个形状：POST 提交任务拿 prediction id，再轮询到
completed 取结果 URL。这里只用 requests，不引入新依赖。
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from videoclaw.utils.logging import get_logger

logger = get_logger(name="atlas.client")

DEFAULT_BASE_URL = "https://api.atlascloud.ai/api/v1/model"
DEFAULT_POLL_INTERVAL = 5
DEFAULT_TIMEOUT = 600
# api.atlascloud.ai 会用 403(error code 1010) 拒掉一些客户端的默认 User-Agent
USER_AGENT = "videoclaw/1"


def resolve_api_key(config: Any) -> Optional[str]:
    """从 dict 或 Config 对象里取 Atlas key，兼容两种配置写法。"""
    if isinstance(config, dict):
        return (
            config.get("atlas", {}).get("api_key")
            or config.get("atlascloud", {}).get("api_key")
            or config.get("api_key")
        )
    return (
        config.get("atlas.api_key")
        or config.get("atlascloud.api_key")
        or config.get("api_key")
    )


def resolve_base_url(config: Any) -> str:
    if isinstance(config, dict):
        value = config.get("atlas", {}).get("base_url") or config.get("base_url")
    else:
        value = config.get("atlas.base_url") or config.get("base_url")
    return (value or DEFAULT_BASE_URL).rstrip("/")


class AtlasClient:
    """提交任务 -> 轮询 -> 下载产物"""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL,
                 poll_interval: int = DEFAULT_POLL_INTERVAL, timeout: int = DEFAULT_TIMEOUT):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.timeout = timeout

    def _headers(self, json_body: bool = False) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {self.api_key}", "User-Agent": USER_AGENT}
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def submit(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """提交生成任务，返回 prediction id"""
        resp = requests.post(
            f"{self.base_url}/{endpoint}",
            headers=self._headers(json_body=True),
            json=payload,
            timeout=120,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Atlas 提交任务失败({resp.status_code}): {resp.text[:300]}")
        prediction_id = (resp.json().get("data") or {}).get("id")
        if not prediction_id:
            raise RuntimeError(f"Atlas 未返回任务 id: {resp.text[:300]}")
        return prediction_id

    def wait(self, prediction_id: str) -> str:
        """轮询到 completed，返回第一个产物 URL"""
        deadline = time.monotonic() + self.timeout
        while True:
            time.sleep(self.poll_interval)
            resp = requests.get(
                f"{self.base_url}/prediction/{prediction_id}",
                headers=self._headers(),
                timeout=120,
            )
            if resp.status_code >= 400:
                raise RuntimeError(f"Atlas 轮询失败({resp.status_code}): {resp.text[:300]}")
            data = resp.json().get("data") or {}
            status = data.get("status")
            if status == "completed":
                outputs = data.get("outputs") or []
                if not outputs:
                    raise RuntimeError("Atlas 任务完成但没有返回产物")
                return outputs[0]
            if status == "failed":
                raise RuntimeError(f"Atlas 生成失败: {data.get('error') or data}")
            if time.monotonic() > deadline:
                raise RuntimeError(f"Atlas 任务 {prediction_id} 超过 {self.timeout}s 仍为 {status}")

    def download(self, url: str, local_path: Path) -> Path:
        """产物 URL 有效期很短，拿到就立刻下载。按真实字节修正扩展名。"""
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=300)
        resp.raise_for_status()
        content = resp.content
        target = _fix_extension(local_path, content)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def run(self, endpoint: str, payload: Dict[str, Any], local_path: Path) -> Path:
        prediction_id = self.submit(endpoint, payload)
        logger.info(f"Atlas 任务已提交: {prediction_id}")
        return self.download(self.wait(prediction_id), local_path)


def _fix_extension(local_path: Path, content: bytes) -> Path:
    """Atlas 上的图片模型返回 JPEG（seedream-v4 实测如此），不要写成名不副实的 .png"""
    if content[:3] == b"\xff\xd8\xff":
        actual = ".jpg"
    elif content[:8] == b"\x89PNG\r\n\x1a\n":
        actual = ".png"
    elif content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        actual = ".webp"
    else:
        return local_path
    if local_path.suffix.lower() in (actual, ".jpeg" if actual == ".jpg" else actual):
        return local_path
    fixed = local_path.with_suffix(actual)
    logger.info(f"Atlas 返回 {actual[1:].upper()}，已存为 {fixed.name}")
    return fixed
