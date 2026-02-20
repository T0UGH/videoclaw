"""存储上传工具"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from videoclaw.storage.factory import get_storage_backend
from videoclaw.config import Config


def upload_to_cloud(
    local_path: Path,
    remote_path: str,
    config: Config,
    project_name: str
) -> Optional[str]:
    """上传文件到云存储

    Args:
        local_path: 本地文件路径
        remote_path: 远程路径
        config: 配置对象
        project_name: 项目名称

    Returns:
        云盘链接，如果没有配置云存储则返回 None
    """
    storage_config = config.get_storage_config()
    provider = storage_config.get("provider", "local")

    # 如果是 local，不上传
    if provider == "local":
        return None

    # 如果不自动上传，也不上传
    if not storage_config.get("upload_on_generate", False):
        return None

    try:
        storage = get_storage_backend(provider, storage_config)

        # 上传文件
        result = storage.upload(local_path, remote_path)
        return result.cloud_url
    except Exception as e:
        # 上传失败不影响主流程
        import logging
        logging.warning(f"Upload to cloud failed: {e}")
        return None
