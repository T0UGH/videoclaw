"""Tests for VolcEngine image backend"""
import pytest
from pathlib import Path
from videoclaw.models.volcengine.seedream import VolcEngineSeedream


def test_volcengine_seedream_text_to_image():
    """Test Seedream text to image"""
    backend = VolcEngineSeedream("seedream-3.0", {"ak": "test", "sk": "test"})
    result = backend.text_to_image("宇航员在火星")

    assert result.local_path.exists()
    assert result.metadata.get("provider") == "volcengine"
    assert result.metadata.get("model") == "seedream-3.0"


def test_volcengine_seedream_image_to_image():
    """Test Seedream image to image"""
    backend = VolcEngineSeedream("seedream-3.0", {"ak": "test", "sk": "test"})
    result = backend.image_to_image(b"fake_image_data", "宇航员穿红色衣服")

    assert result.local_path.exists()
    assert result.metadata.get("provider") == "volcengine"
