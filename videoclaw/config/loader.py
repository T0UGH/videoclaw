"""配置管理模块"""
from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置管理类"""

    # 环境变量映射
    ENV_MAPPINGS = {
        "dashscope.api_key": "DASHSCOPE_API_KEY",
        "volcengine.ak": "VOLCENGINE_AK",
        "volcengine.sk": "VOLCENGINE_SK",
        "ark.api_key": "ARK_API_KEY",
        "google.api_key": "GOOGLE_API_KEY",
    }

    def __init__(self, project_path: Optional[Path] = None):
        self._config: Dict[str, Any] = {}
        self._project_path = project_path
        self._load()

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """深度合并两个字典，override 优先"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _load(self):
        # 1. 加载全局配置
        global_config = {}
        global_config_path = Path.home() / ".videoclaw" / "config.yaml"
        if global_config_path.exists():
            try:
                with open(global_config_path) as f:
                    global_config = yaml.safe_load(f) or {}
            except yaml.YAMLError:
                pass  # 忽略损坏的配置文件

        # 2. 加载项目配置
        project_config = {}
        if self._project_path:
            project_config_path = self._project_path / ".videoclaw" / "config.yaml"
            if project_config_path.exists():
                try:
                    with open(project_config_path) as f:
                        project_config = yaml.safe_load(f) or {}
                except yaml.YAMLError:
                    pass  # 忽略损坏的配置文件

        # 3. 合并：全局 + 项目（项目覆盖全局）
        self._config = Config._deep_merge(global_config, project_config)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 1. 检查环境变量 (最高优先级)
        # 映射常用环境变量
        if key in Config.ENV_MAPPINGS:
            env_key = Config.ENV_MAPPINGS[key]
            if env_key in os.environ:
                return os.environ[env_key]

        # 通用的环境变量映射
        env_key = f"VIDEOCLAW_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]

        # 2. 返回配置值
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

    def get_storage_config(self) -> Dict[str, Any]:
        """获取存储配置"""
        return {
            "provider": self.get("storage.provider", "local"),
            "upload_on_generate": self.get("storage.upload_on_generate", False),
            "credentials_path": self.get("storage.credentials_path"),
        }
