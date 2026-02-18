"""本地存储后端"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from videoclaw.storage.base import StorageBackend, StorageResult


class LocalStorage(StorageBackend):
    """本地文件系统存储"""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.home() / "videoclaw-projects"

    def save(self, data: bytes, path: str) -> StorageResult:
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)
        return StorageResult(
            local_path=full_path,
            cloud_url=None
        )

    def load(self, path: str) -> bytes:
        full_path = self.base_dir / path
        return full_path.read_bytes()

    def delete(self, path: str) -> None:
        full_path = self.base_dir / path
        if full_path.exists():
            full_path.unlink()

    def get_url(self, path: str) -> Optional[str]:
        # 本地存储没有云端URL
        return None
