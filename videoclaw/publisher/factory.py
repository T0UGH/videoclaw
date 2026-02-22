"""Publisher 工厂函数"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from videoclaw.publisher.base import Publisher
from videoclaw.publisher.douyin import DouYinPublisher
from videoclaw.publisher.kuaishou import KuaishouPublisher


def get_publisher(
    platform: str,
    cookie_dir: Optional[Path] = None,
    headless: bool = True,
) -> Publisher:
    """获取发布器实例

    Args:
        platform: 平台名称 (douyin, kuaishou)
        cookie_dir: cookie 目录
        headless: 是否使用 headless 模式

    Returns:
        发布器实例

    Raises:
        ValueError: 不支持的平台
    """
    if cookie_dir is None:
        cookie_dir = Path.home() / ".videoclaw" / "cookies" / platform

    if platform == "douyin":
        return DouYinPublisher(cookie_dir, headless)
    elif platform == "kuaishou":
        return KuaishouPublisher(cookie_dir, headless)
    else:
        raise ValueError(f"不支持的平台: {platform}")
