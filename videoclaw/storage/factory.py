"""存储后端工厂函数"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any

from videoclass.storage.base import StorageBackend
from videoclass.storage.local import LocalStorage


def get_storage_backend(
    provider: str = "local",
    config: Optional[Dict[str, Any]] = None,
    base_dir: Optional[Path] = None
) -> StorageBackend:
    """获取存储后端实例

    Args:
        provider: 存储提供商 (local, google_drive, dropbox)
        config: 配置字典
        base_dir: 本地存储基础目录

    Returns:
        StorageBackend 实例
    """
    config = config or {}

    if provider == "local":
        base_dir = base_dir or Path.home() / "videoclaw-projects"
        return LocalStorage(base_dir)
    elif provider == "google_drive":
        from videoclass.storage.google_drive import GoogleDriveStorage
        credentials_path = config.get("credentials_path")
        return GoogleDriveStorage(credentials_path=credentials_path)
    elif provider == "dropbox":
        # TODO: 未来实现
        raise NotImplementedError("Dropbox storage not yet implemented")
    else:
        raise ValueError(f"Unknown storage provider: {provider}")
