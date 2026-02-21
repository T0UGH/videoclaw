"""独立文生图命令测试"""
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

os.environ["VIDEOCLAW_MODELS_IMAGE_PROVIDER"] = "mock"


def test_t2i_command_requires_prompt():
    """测试 t2i 命令缺少 prompt 参数"""
    from videoclaw.cli.commands.t2i import t2i
    runner = CliRunner()
    result = runner.invoke(t2i, ["--output", "test.png"])
    assert result.exit_code != 0


def test_t2i_command_requires_output():
    """测试 t2i 命令缺少 output 参数"""
    from videoclaw.cli.commands.t2i import t2i
    runner = CliRunner()
    result = runner.invoke(t2i, ["--prompt", "test"])
    assert result.exit_code != 0


def test_t2i_command_success():
    """测试 t2i 命令成功执行"""
    from videoclaw.cli.commands.t2i import t2i
    runner = CliRunner()

    with patch("videoclaw.cli.commands.t2i.get_image_backend") as mock_backend:
        mock_result = MagicMock()
        mock_result.local_path.__str__ = lambda: "/tmp/test.png"
        mock_backend.return_value.text_to_image.return_value = mock_result

        with patch("shutil.copy"):
            with patch("pathlib.Path.mkdir", MagicMock()):
                result = runner.invoke(t2i, ["--prompt", "astronaut", "--output", "/tmp/test.png"])
                assert "Generated:" in result.output or result.exit_code == 0
