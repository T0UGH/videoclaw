"""状态管理"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StateManager:
    """项目状态管理器"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.state_file = project_path / ".videoclaw" / "state.json"
        self._state: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "project_id": self.project_path.name,
            "status": "initialized",
            "steps": {},
            "created_at": datetime.now().isoformat(),
        }

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self._state, f, indent=2)

    def get_status(self) -> str:
        return self._state.get("status", "unknown")

    def set_status(self, status: str):
        self._state["status"] = status
        self._state["updated_at"] = datetime.now().isoformat()
        self.save()

    def update_step(self, step: str, step_status: str, output: Any = None):
        if "steps" not in self._state:
            self._state["steps"] = {}

        self._state["steps"][step] = {
            "status": step_status,
            "updated_at": datetime.now().isoformat(),
        }
        if output:
            self._state["steps"][step]["output"] = output

        self.save()

    def get_step(self, step: str) -> Optional[Dict[str, Any]]:
        return self._state.get("steps", {}).get(step)
