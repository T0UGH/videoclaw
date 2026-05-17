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
        "openai.api_key": "OPENAI_API_KEY",
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
        global_config = {}
        global_config_path = Path.home() / ".videoclaw" / "config.yaml"
        if global_config_path.exists():
            try:
                with open(global_config_path) as f:
                    global_config = yaml.safe_load(f) or {}
            except yaml.YAMLError:
                pass

        project_config = {}
        if self._project_path:
            project_config_path = self._project_path / ".videoclaw" / "config.yaml"
            if project_config_path.exists():
                try:
                    with open(project_config_path) as f:
                        project_config = yaml.safe_load(f) or {}
                except yaml.YAMLError:
                    pass

        self._config = Config._deep_merge(global_config, project_config)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if key in Config.ENV_MAPPINGS:
            env_key = Config.ENV_MAPPINGS[key]
            if env_key in os.environ:
                return os.environ[env_key]

        env_key = f"VIDEOCLAW_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]

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

    def get_image_backend_config(self) -> Dict[str, Any]:
        """获取图片后端配置"""
        backend = self.get("models.image.backend") or self.get("models.image.provider", "codex-host-image")
        model = self.get("models.image.model")
        auth = self.get("models.image.auth")
        codex_mode = self.get("models.image.codex_mode")

        provider_api_keys = {
            "google.api_key": self.get("google.api_key"),
            "openai.api_key": self.get("openai.api_key"),
            "dashscope.api_key": self.get("dashscope.api_key"),
            "ark.api_key": self.get("ark.api_key"),
        }

        return {
            "backend": backend,
            "model": model,
            "auth": auth,
            "codex_mode": codex_mode,
            **provider_api_keys,
        }
