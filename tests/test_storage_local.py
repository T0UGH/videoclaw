"""Tests for local storage"""
import tempfile
from pathlib import Path

from videoclaw.storage.local import LocalStorage


def test_local_storage():
    """Test local storage save, load, delete"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(Path(tmpdir))
        data = b"hello world"

        result = storage.save(data, "test/file.txt")
        assert result.local_path.exists()
        assert result.cloud_url is None

        loaded = storage.load("test/file.txt")
        assert loaded == data

        storage.delete("test/file.txt")
        assert not result.local_path.exists()


def test_local_storage_get_url():
    """Test local storage returns None for URL"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(Path(tmpdir))
        assert storage.get_url("test.txt") is None
