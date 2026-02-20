"""Tests for VolcEngine image backend"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from videoclaw.models.volcengine.seedream import VolcEngineSeedream


def test_volcengine_seedream_text_to_image():
    """Test Seedream text to image with mock"""
    backend = VolcEngineSeedream("doubao-seedream-4-5-251128", {"api_key": "test-key"})

    # Mock the SDK response
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="https://example.com/image.png")]

    with patch.object(backend.client.images, 'generate', return_value=mock_response):
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(content=b"fake_image_data")
            result = backend.text_to_image("宇航员在火星")

    assert result.local_path.exists()
    assert result.local_path.suffix == ".png"
    assert result.metadata.get("provider") == "volcengine"
    assert result.metadata.get("model") == "doubao-seedream-4-5-251128"


def test_volcengine_seedream_image_to_image():
    """Test Seedream image to image with mock"""
    backend = VolcEngineSeedream("doubao-seedream-4-5-251128", {"api_key": "test-key"})

    # Mock the SDK response
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="https://example.com/image.png")]

    with patch.object(backend.client.images, 'generate', return_value=mock_response):
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(content=b"fake_image_data")
            result = backend.image_to_image(b"fake_input_image", "宇航员穿红色衣服")

    assert result.local_path.exists()
    assert result.local_path.suffix == ".png"
    assert result.metadata.get("provider") == "volcengine"


def test_volcengine_seedream_requires_api_key():
    """Test Seedream requires API key"""
    with pytest.raises(ValueError, match="ARK API Key is required"):
        VolcEngineSeedream("doubao-seedream-4-5-251128", {})


def test_volcengine_seedream_with_env_api_key():
    """Test Seedream uses ARK_API_KEY from config"""
    import os
    # Test that api_key can be passed via config
    backend = VolcEngineSeedream("doubao-seedream-4-5-251128", {"api_key": "env-test-key"})
    assert backend.api_key == "env-test-key"
