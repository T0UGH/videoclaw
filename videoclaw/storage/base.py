"""存储抽象层"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class StorageResult:
    """存储结果"""
    local_path: Path
    cloud_url: Optional[str] = None  # Google Drive webViewLink
    file_id: Optional[str] = None   # Google Drive file_id


class StorageBackend(ABC):
    """存储后端基类"""

    @abstractmethod
    def save(self, data: bytes, path: str) -> StorageResult:
        """保存数据，返回本地路径和云端URL"""
        pass

    @abstractmethod
    def load(self, path: str) -> bytes:
        """加载数据"""
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """删除数据"""
        pass

    @abstractmethod
    def get_url(self, path: str) -> Optional[str]:
        """获取访问链接"""
        pass
