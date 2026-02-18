"""Tests for config module"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from videoclaw.config import Config


def test_config_get_default():
    """Test getting config with default value"""
    with patch.object(Path, "home", return_value=Path(tempfile.gettempdir())):
        config = Config()
        # No config file, should return default
        result = config.get("storage.type", "local")
        assert result == "local"


def test_config_get_nested():
    """Test getting nested config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".videoclaw"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"

        import yaml
        config_data = {
            "storage": {
                "type": "oss",
                "config": {
                    "bucket": "my-bucket"
                }
            }
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        with patch.object(Path, "home", return_value=Path(tmpdir)):
            config = Config()
            assert config.get("storage.type") == "oss"
            assert config.get("storage.config.bucket") == "my-bucket"


def test_config_env_override():
    """Test that environment variables override config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".videoclaw"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"

        import yaml
        config_data = {"storage": {"type": "local"}}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        with patch.object(Path, "home", return_value=Path(tmpdir)):
            with patch.dict(os.environ, {"VIDEOCLAW_STORAGE_TYPE": "oss"}):
                config = Config()
                assert config.get("storage.type") == "oss"


def test_config_get_all():
    """Test getting all config"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".videoclaw"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"

        import yaml
        config_data = {"project": "test", "version": "1.0"}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        with patch.object(Path, "home", return_value=Path(tmpdir)):
            config = Config()
            all_config = config.get_all()
            assert all_config["project"] == "test"
            assert all_config["version"] == "1.0"
