"""Tests for Google Gemini image backend"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_gemini_image_backend_init():
    """Test Gemini image backend initialization"""
    from videoclaw.models.gemini.image import GeminiImageBackend

    backend = GeminiImageBackend("gemini-2.0-flash-exp-image-generation", {"api_key": "test-key"})
    assert backend.model == "gemini-2.0-flash-exp-image-generation"
    assert backend.api_key == "test-key"


def test_gemini_image_backend_init_from_env():
    """Test reading API key from GOOGLE_API_KEY environment variable"""
    from videoclaw.models.gemini.image import GeminiImageBackend

    # Set the environment variable
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-test-key"}):
        backend = GeminiImageBackend("imagen-3.0-fast", {})
        assert backend.api_key == "env-test-key"


def test_text_to_image_requires_api_key():
    """Test error when no API key is provided"""
    from videoclaw.models.gemini.image import GeminiImageBackend

    with pytest.raises(ValueError, match="Google Gemini API key is required"):
        GeminiImageBackend("gemini-2.0-flash-exp-image-generation", {})
