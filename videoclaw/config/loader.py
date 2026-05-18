"""配置管理模块"""
from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置管理类"""

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

    def _plotloom_fallback(self, key: str) -> Any:
        plotloom_path = Path.home() / ".plotloom" / ".env.toml"
        if not plotloom_path.exists():
            return None
        try:
            text = plotloom_path.read_text(encoding="utf-8")
        except OSError:
            return None

        if key == "ark.api_key":
            in_volcengine = False
            for line in text.splitlines():
                stripped = line.strip()
                if stripped == "[adapters.volcengine-seedance]":
                    in_volcengine = True
                    continue
                if stripped.startswith("[") and stripped != "[adapters.volcengine-seedance]":
                    in_volcengine = False
                if in_volcengine and stripped.startswith("ark_api_key"):
                    return stripped.split("=", 1)[1].strip().strip('"')
        return None

    def get(self, key: str, default: Any = None) -> Any:
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
                value = None
                break
        if value is not None:
            return value

        plotloom_value = self._plotloom_fallback(key)
        if plotloom_value is not None:
            return plotloom_value
        return default

    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()

    def get_storage_config(self) -> Dict[str, Any]:
        return {
            "provider": self.get("storage.provider", "local"),
            "upload_on_generate": self.get("storage.upload_on_generate", False),
            "credentials_path": self.get("storage.credentials_path"),
        }

    def get_image_backend_config(self) -> Dict[str, Any]:
        backend = self.get("models.image.backend") or self.get("models.image.provider", "codex-host-image")
        model = self.get("models.image.model")
        auth = self.get("models.image.auth")
        codex_mode = self.get("models.image.codex_mode")
        transport = self.get("models.image.transport", "codex_oauth")

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
            "transport": transport,
            **provider_api_keys,
        }
