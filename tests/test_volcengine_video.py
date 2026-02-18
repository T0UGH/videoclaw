"""Tests for VolcEngine video backend"""
import pytest
from pathlib import Path
from videoclaw.models.volcengine.seedance import VolcEngineSeedance


def test_volcengine_seedance_image_to_video():
    """Test Seedance image to video"""
    backend = VolcEngineSeedance("seedance-2.0", {"ak": "test", "sk": "test"})
    result = backend.image_to_video(b"fake_image", "宇航员走路")

    assert result.local_path.exists()
    assert result.local_path.suffix == ".mp4"
    assert result.metadata.get("provider") == "volcengine"
    assert result.metadata.get("model") == "seedance-2.0"
