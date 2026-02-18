"""Tests for mock backends"""
from pathlib import Path

from videoclaw.models.mock.video import MockVideoBackend
from videoclaw.models.mock.audio import MockAudioBackend


def test_mock_video_backend():
    """Test mock video backend"""
    backend = MockVideoBackend("mock-model", {})
    result = backend.image_to_video(b"fake image", "test prompt")

    assert result.local_path.exists()
    assert result.cloud_url is None
    assert result.metadata["duration"] == 5
    assert result.metadata["format"] == "mp4"


def test_mock_audio_backend():
    """Test mock audio backend"""
    backend = MockAudioBackend("mock-model", {})
    result = backend.text_to_speech("Hello world", "voice1")

    assert result.local_path.exists()
    assert result.cloud_url is None
    assert result.metadata["duration"] == 3
    assert result.metadata["format"] == "mp3"
    assert result.metadata["voice"] == "voice1"
