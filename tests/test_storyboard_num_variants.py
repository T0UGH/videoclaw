"""storyboard 命令 num-variants 测试"""
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path

os.environ["VIDEOCLAW_MODELS_IMAGE_PROVIDER"] = "mock"


def test_storyboard_generates_multiple_variants():
    """测试 storyboard 命令生成多个候选"""
    from videoclaw.cli.commands.storyboard import storyboard
    from click.testing import CliRunner

    runner = CliRunner()

    with patch("videoclaw.cli.commands.storyboard.get_image_backend") as mock_get_backend:
        mock_backend = MagicMock()
        mock_result = MagicMock()
        mock_result.local_path = Path("/tmp/test.png")
        mock_backend.text_to_image = Mock(return_value=mock_result)
        mock_get_backend.return_value = mock_backend

        with patch("shutil.copy"):
            with patch("videoclaw.cli.commands.storyboard.StateManager") as mock_state:
                mock_state_instance = MagicMock()
                mock_state_instance.get_step.side_effect = lambda step: {
                    "assets": {"status": "completed", "output": {"characters": {}}},
                    "analyze": {
                        "status": "completed",
                        "output": {
                            "frames": [{"frame_id": 1, "description": "test frame", "camera": "wide"}],
                            "characters": []
                        }
                    }
                }.get(step)
                mock_state.return_value = mock_state_instance

                result = runner.invoke(storyboard, [
                    "--project", "test",
                    "--num-variants", "4"
                ])

                assert mock_backend.text_to_image.call_count >= 4
