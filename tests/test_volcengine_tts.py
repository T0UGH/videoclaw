"""Tests for VolcEngine TTS backend"""
import pytest
from pathlib import Path
from videoclaw.models.volcengine.tts import VolcEngineTTS


def test_volcengine_tts_text_to_speech():
    """Test VolcEngine TTS"""
    backend = VolcEngineTTS("volcengine-tts", {"ak": "test", "sk": "test"})
    result = backend.text_to_speech("你好世界", "xiaoyuan")

    assert result.local_path.exists()
    assert result.local_path.suffix == ".mp3"
    assert result.metadata.get("provider") == "volcengine"
    assert result.metadata.get("voice") == "xiaoyuan"
