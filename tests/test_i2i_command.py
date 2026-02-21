"""独立图生图命令测试"""
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

os.environ["VIDEOCLAW_MODELS_IMAGE_PROVIDER"] = "mock"


def test_i2i_command_requires_input():
    """测试 i2i 命令缺少 input 参数"""
    from videoclaw.cli.commands.i2i import i2i
    runner = CliRunner()
    result = runner.invoke(i2i, ["--prompt", "test", "--output", "test.png"])
    assert result.exit_code != 0


def test_i2i_command_requires_prompt():
    """测试 i2i 命令缺少 prompt 参数"""
    from videoclaw.cli.commands.i2i import i2i
    runner = CliRunner()
    result = runner.invoke(i2i, ["--input", "test.png", "--output", "test2.png"])
    assert result.exit_code != 0


def test_i2i_command_success():
    """测试 i2i 命令成功执行"""
    from videoclaw.cli.commands.i2i import i2i
    runner = CliRunner()

    with patch("videoclaw.cli.commands.i2i.get_image_backend") as mock_backend:
        mock_result = MagicMock()
        mock_result.local_path.__str__ = lambda: "/tmp/test2.png"
        mock_backend.return_value.image_to_image.return_value = mock_result

        with patch("shutil.copy"):
            with patch("pathlib.Path.mkdir", MagicMock()):
                with patch("pathlib.Path.read_bytes", return_value=b"fake image"):
                    result = runner.invoke(i2i, [
                        "--input", "/tmp/test.png",
                        "--prompt", "穿红色制服",
                        "--output", "/tmp/test2.png"
                    ])
                    assert "Generated:" in result.output or result.exit_code == 0
