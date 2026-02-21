"""StateManager 选择记录测试"""
import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory


def test_state_manager_update_selection():
    """测试更新选择记录"""
    from videoclaw.state.manager import StateManager

    with TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test"
        project_path.mkdir(parents=True)
        (project_path / ".videoclaw").mkdir()

        manager = StateManager(project_path)

        manager.update_selection(
            "assets",
            chosen="assets/character_1.png",
            alternatives=[
                "assets/character_1.png",
                "assets/character_2.png",
                "assets/character_3.png",
                "assets/character_4.png"
            ]
        )

        selection = manager.get_selection("assets")
        assert selection["chosen"] == "assets/character_1.png"
        assert len(selection["alternatives"]) == 4


def test_state_manager_get_all_alternatives():
    """测试获取所有候选"""
    from videoclaw.state.manager import StateManager

    with TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test"
        project_path.mkdir(parents=True)
        (project_path / ".videoclaw").mkdir()

        manager = StateManager(project_path)

        manager.update_selection("assets", "a1.png", ["a1.png", "a2.png"])
        manager.update_selection("storyboard", "s1.png", ["s1.png", "s2.png"])

        all_alts = manager.get_all_alternatives()
        assert len(all_alts) == 4
        assert "a1.png" in all_alts
        assert "s1.png" in all_alts
