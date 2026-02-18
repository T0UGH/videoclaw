"""配置管理模块"""
from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """配置管理类"""

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self):
        # 1. 加载全局配置
        global_config_path = Path.home() / ".videoclaw" / "config.yaml"
        if global_config_path.exists():
            with open(global_config_path) as f:
                self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 检查环境变量
        env_key = f"VIDEOCLAW_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]

        # 返回配置值
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
