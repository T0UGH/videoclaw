"""assets 命令 num-variants 测试"""
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path

os.environ["VIDEOCLAW_MODELS_IMAGE_PROVIDER"] = "mock"


def test_assets_generates_multiple_variants():
    """测试 assets 命令生成多个候选"""
    from videoclaw.cli.commands.assets import assets
    from click.testing import CliRunner

    runner = CliRunner()

    with patch("videoclaw.cli.commands.assets.get_image_backend") as mock_get_backend:
        mock_backend = MagicMock()
        mock_result = MagicMock()
        mock_result.local_path = Path("/tmp/test.png")
        mock_result.metadata = {"provider": "mock"}

        # 模拟多次调用返回不同结果
        mock_backend.text_to_image = Mock(return_value=mock_result)
        mock_get_backend.return_value = mock_backend

        with patch("shutil.copy"):
            with patch("videoclaw.cli.commands.assets.StateManager") as mock_state:
                mock_state_instance = MagicMock()
                mock_state_instance.get_step.return_value = {
                    "status": "completed",
                    "output": {
                        "characters": [{"name": "astronaut", "description": "宇航员"}],
                        "scenes": []
                    }
                }
                mock_state.return_value = mock_state_instance

                result = runner.invoke(assets, [
                    "--project", "test",
                    "--num-variants", "3"
                ])

                # 验证 text_to_image 被调用 3 次
                assert mock_backend.text_to_image.call_count >= 3


def test_assets_default_num_variants_is_one():
    """测试默认 num-variants 为 1"""
    from videoclaw.cli.commands.assets import assets
    from click.testing import CliRunner

    runner = CliRunner()

    with patch("videoclaw.cli.commands.assets.get_image_backend") as mock_get_backend:
        mock_backend = MagicMock()
        mock_result = MagicMock()
        mock_result.local_path = Path("/tmp/test.png")
        mock_backend.text_to_image = Mock(return_value=mock_result)
        mock_get_backend.return_value = mock_backend

        with patch("shutil.copy"):
            with patch("videoclaw.cli.commands.assets.StateManager") as mock_state:
                mock_state_instance = MagicMock()
                mock_state_instance.get_step.return_value = {
                    "status": "completed",
                    "output": {
                        "characters": [{"name": "astronaut", "description": "宇航员"}],
                        "scenes": []
                    }
                }
                mock_state.return_value = mock_state_instance

                result = runner.invoke(assets, ["--project", "test"])

                # 验证 text_to_image 被调用 1 次
                assert mock_backend.text_to_image.call_count == 1
