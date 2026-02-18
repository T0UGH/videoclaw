"""Tests for state manager"""
import tempfile
from pathlib import Path
from videoclaw.state import StateManager


def test_state_manager_init():
    """Test state manager initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        state = StateManager(project_path)
        assert state.get_status() == "initialized"
        assert "steps" in state._state


def test_state_manager_set_status():
    """Test setting status"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        state = StateManager(project_path)
        state.set_status("generating")

        assert state.get_status() == "generating"
        assert state.state_file.exists()


def test_state_manager_update_step():
    """Test updating step"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        state = StateManager(project_path)
        state.update_step("analyze", "completed", {"result": "ok"})

        step = state.get_step("analyze")
        assert step is not None
        assert step["status"] == "completed"
        assert step["output"]["result"] == "ok"
