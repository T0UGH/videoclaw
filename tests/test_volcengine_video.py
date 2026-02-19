"""Tests for VolcEngine video backend"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from videoclaw.models.volcengine.seedance import VolcEngineSeedance


def test_volcengine_seedance_image_to_video():
    """Test Seedance image to video with mock"""
    backend = VolcEngineSeedance("doubao-seedance-1-5-pro-251215", {"api_key": "test-key"})

    # Mock the task creation response
    mock_task = MagicMock()
    mock_task.id = "cgt-test-123"
    mock_task.status = "succeeded"
    mock_task.video = MagicMock(url="https://example.com/video.mp4")

    with patch.object(backend.client.content_generation.tasks, 'create', return_value=mock_task):
        with patch.object(backend.client.content_generation.tasks, 'get', return_value=mock_task):
            with patch('requests.get') as mock_get:
                mock_get.return_value = MagicMock(content=b"fake_video_data")
                result = backend.image_to_video(b"fake_image_data", "宇航员走路")

    assert result.local_path.exists()
    assert result.local_path.suffix == ".mp4"
    assert result.metadata.get("provider") == "volcengine"
    assert result.metadata.get("model") == "doubao-seedance-1-5-pro-251215"


def test_volcengine_seedance_requires_api_key():
    """Test Seedance requires API key"""
    with pytest.raises(ValueError, match="ARK API Key is required"):
        VolcEngineSeedance("doubao-seedance-1-5-pro-251215", {})


def test_volcengine_seedance_with_env_api_key():
    """Test Seedance uses ARK_API_KEY from config"""
    backend = VolcEngineSeedance("doubao-seedance-1-5-pro-251215", {"api_key": "env-test-key"})
    assert backend.api_key == "env-test-key"
