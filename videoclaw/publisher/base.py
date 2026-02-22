"""Publisher 基类"""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    video_url: Optional[str] = None
    error: Optional[str] = None


class Publisher(ABC):
    """Publisher 基类"""

    def __init__(self, cookie_dir: Path, headless: bool = True):
        self.cookie_dir = cookie_dir
        self.headless = headless

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名称"""
        pass

    @property
    @abstractmethod
    def creator_url(self) -> str:
        """创作者中心 URL"""
        pass

    @property
    @abstractmethod
    def upload_url(self) -> str:
        """上传页面 URL"""
        pass

    def get_cookie_path(self, account: str = "default") -> Path:
        """获取 cookie 文件路径"""
        return self.cookie_dir / f"{account}.json"

    def cookie_exists(self, account: str = "default") -> bool:
        """检查 cookie 是否存在"""
        return self.get_cookie_path(account).exists()

    @abstractmethod
    async def login(self, account: str = "default") -> bool:
        """登录账号"""
        pass

    @abstractmethod
    async def publish(
        self,
        video_path: Path,
        title: str,
        tags: list[str],
        cover_path: Optional[Path] = None,
        account: str = "default",
    ) -> PublishResult:
        """发布视频"""
        pass
