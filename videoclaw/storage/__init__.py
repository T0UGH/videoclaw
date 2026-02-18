"""存储模块"""
from videoclaw.storage.base import StorageBackend, StorageResult
from videoclaw.storage.local import LocalStorage

__all__ = ["StorageBackend", "StorageResult", "LocalStorage"]
