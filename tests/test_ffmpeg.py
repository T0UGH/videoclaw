"""Tests for FFmpeg processor"""
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from videoclaw.ffmpeg.processor import FFmpegProcessor


def test_ffmpeg_processor_init():
    """Test FFmpegProcessor initialization"""
    processor = FFmpegProcessor()
    assert processor.ffmpeg_path == "ffmpeg"


def test_ffmpeg_processor_custom_path():
    """Test FFmpegProcessor with custom path"""
    processor = FFmpegProcessor("/usr/local/bin/ffmpeg")
    assert processor.ffmpeg_path == "/usr/local/bin/ffmpeg"
