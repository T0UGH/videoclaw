"""工具函数模块"""
from __future__ import annotations

import re
import hashlib
import time
from pathlib import Path


def generate_unique_filename(prefix: str, extension: str) -> str:
    """生成唯一文件名"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}.{extension}"


def validate_project_name(name: str) -> bool:
    """验证项目名称是否合法"""
    # 只允许字母、数字、连字符、下划线
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, name))


def ensure_directory(path: Path) -> Path:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path
