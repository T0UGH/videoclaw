"""Tests for utils"""
import pytest
from pathlib import Path
from videoclaw.utils.helpers import generate_unique_filename, validate_project_name, ensure_directory


def test_generate_unique_filename():
    """Test unique filename generation"""
    import time
    time.sleep(0.01)  # Ensure different timestamps
    filename = generate_unique_filename("test", "png")
    assert filename.startswith("test_")
    assert filename.endswith(".png")
    assert "_" in filename


def test_validate_project_name():
    """Test project name validation"""
    assert validate_project_name("my-project") is True
    assert validate_project_name("my_project") is True
    assert validate_project_name("myproject123") is True
    assert validate_project_name("My Project!") is False
    assert validate_project_name("my project") is False
    assert validate_project_name("") is False


def test_ensure_directory(tmp_path):
    """Test ensure directory"""
    test_dir = tmp_path / "test" / "nested"
    result = ensure_directory(test_dir)
    assert result.exists()
    assert result.is_dir()
