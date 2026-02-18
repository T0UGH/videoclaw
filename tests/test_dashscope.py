"""Tests for DashScope backends"""
import pytest
from pathlib import Path
from videoclaw.models.dashscope.t2i import DashScopeT2I
from videoclaw.models.dashscope.i2v import DashScopeI2V
from videoclaw.models.dashscope.tts import DashScopeTTS


def test_dashscope_t2i():
    """Test DashScope T2I"""
    backend = DashScopeT2I("wan2.6-t2i", {"api_key": "test"})
    result = backend.text_to_image("宇航员")

    assert result.local_path.exists()
    assert result.metadata.get("provider") == "dashscope"
    assert result.metadata.get("model") == "wan2.6-t2i"


def test_dashscope_i2v():
    """Test DashScope I2V"""
    backend = DashScopeI2V("wan2.6-i2v", {"api_key": "test"})
    result = backend.image_to_video(b"image_data", "宇航员走路")

    assert result.local_path.exists()
    assert result.local_path.suffix == ".mp4"
    assert result.metadata.get("provider") == "dashscope"


def test_dashscope_tts():
    """Test DashScope TTS"""
    backend = DashScopeTTS("cosyvoice-v2", {"api_key": "test"})
    result = backend.text_to_speech("你好", "xiaoyuan")

    assert result.local_path.exists()
    assert result.local_path.suffix == ".mp3"
    assert result.metadata.get("provider") == "dashscope"
    assert result.metadata.get("voice") == "xiaoyuan"
