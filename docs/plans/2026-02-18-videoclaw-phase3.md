# Phase 3: CLI Commands Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 实现完整的 CLI 命令体系，包括 analyze, assets, storyboard, i2v, audio, merge, preview, config

**Architecture:** 使用 Click 构建命令，每个命令对应一个独立模块

**Tech Stack:** Python 3.11+, Click, Pydantic

---

## Task 1: 状态管理模块

**Files:**
- Create: `videoclaw/state/__init__.py`
- Create: `videoclaw/state/manager.py`

**Step 1: 创建状态管理器**

```python
"""状态管理"""
import json
from pathlib import Path
from datetime import datetime
from typing import Any


class StateManager:
    """项目状态管理器"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.state_file = project_path / ".videoclaw" / "state.json"
        self._state = self._load()

    def _load(self) -> dict:
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

    def update_step(self, step: str, status: str, output: Any = None):
        if "steps" not in self._state:
            self._state["steps"] = {}

        self._state["steps"][step] = {
            "status": status,
            "updated_at": datetime.now().isoformat(),
        }
        if output:
            self._state["steps"][step]["output"] = output

        self.save()

    def get_step(self, step: str) -> dict | None:
        return self._state.get("steps", {}).get(step)
```

**Step 2: 创建 __init__.py**

```python
"""状态管理模块"""
from videoclaw.state.manager import StateManager

__all__ = ["StateManager"]
```

**Step 3: Commit**

```bash
git add videoclaw/state/
git commit -m "feat: 添加状态管理模块"
```

---

## Task 2: assets 命令（资产生成）

**Files:**
- Create: `videoclaw/cli/commands/assets.py`
- Modify: `videoclaw/cli/main.py`

**Step 1: 创建 assets 命令**

```python
"""assets 命令"""
import click
from pathlib import Path
from videoclaw.state import StateManager


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
def assets(project: str):
    """生成角色和场景图片资产"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    state = StateManager(project_path)

    # 检查上一步是否完成
    analyze_step = state.get_step("analyze")
    if not analyze_step or analyze_step.get("status") != "completed":
        click.echo("错误: 请先完成脚本分析", err=True)
        return

    state.set_status("generating_assets")
    state.update_step("assets", "in_progress")

    click.echo("生成资产...")
    # TODO: 调用 AI 模型生成图片

    result = {
        "characters": {},
        "scenes": {},
    }

    state.update_step("assets", "completed", result)
    state.set_status("assets_generated")

    click.echo("资产生成完成!")
```

**Step 2: 注册到 main.py**

```python
# 在 main.py 中添加
from videoclaw.cli.commands.assets import assets
main.add_command(assets)
```

**Step 3: 测试**

```bash
videoclaw assets --project my-test-project
```

**Step 4: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: 实现 assets 命令"
```

---

## Task 3: storyboard 命令

**Files:**
- Create: `videoclaw/cli/commands/storyboard.py`

**Step 1: 创建 storyboard 命令**

```python
"""storyboard 命令"""
import click
from pathlib import Path
from videoclaw.state import StateManager


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
def storyboard(project: str):
    """生成故事板帧图片"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    state = StateManager(project_path)

    # 检查上一步是否完成
    assets_step = state.get_step("assets")
    if not assets_step or assets_step.get("status") != "completed":
        click.echo("错误: 请先完成资产生成", err=True)
        return

    state.set_status("rendering_storyboard")
    state.update_step("storyboard", "in_progress")

    click.echo("生成故事板...")
    # TODO: 调用 AI 模型生成故事板图片

    result = {
        "frames": [],
    }

    state.update_step("storyboard", "completed", result)
    state.set_status("storyboard_rendered")

    click.echo("故事板生成完成!")
```

**Step 2: 注册命令**

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: 实现 storyboard 命令"
```

---

## Task 4: i2v 命令（图生视频）

**Files:**
- Create: `videoclaw/cli/commands/i2v.py`

**Step 1: 创建 i2v 命令**

```python
"""i2v 命令"""
import click
from pathlib import Path
from videoclaw.state import StateManager


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
def i2v(project: str):
    """图生视频"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    state = StateManager(project_path)

    # 检查上一步是否完成
    storyboard_step = state.get_step("storyboard")
    if not storyboard_step or storyboard_step.get("status") != "completed":
        click.echo("错误: 请先完成故事板生成", err=True)
        return

    state.set_status("generating_video")
    state.update_step("i2v", "in_progress")

    click.echo("生成视频...")
    # TODO: 调用 AI 模型生成视频

    result = {
        "videos": [],
    }

    state.update_step("i2v", "completed", result)
    state.set_status("video_generated")

    click.echo("视频生成完成!")
```

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: 实现 i2v 命令"
```

---

## Task 5: audio 命令

**Files:**
- Create: `videoclaw/cli/commands/audio.py`

**Step 1: 创建 audio 命令**

```python
"""audio 命令"""
import click
from pathlib import Path
from videoclaw.state import StateManager


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
def audio(project: str):
    """生成音频（TTS、音效、背景音乐）"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    state = StateManager(project_path)

    # 检查上一步是否完成
    i2v_step = state.get_step("i2v")
    if not i2v_step or i2v_step.get("status") != "completed":
        click.echo("错误: 请先完成视频生成", err=True)
        return

    state.set_status("generating_audio")
    state.update_step("audio", "in_progress")

    click.echo("生成音频...")
    # TODO: 调用 AI 模型生成音频

    result = {
        "dialogues": [],
        "sfx": [],
        "bgm": None,
    }

    state.update_step("audio", "completed", result)
    state.set_status("audio_generated")

    click.echo("音频生成完成!")
```

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: 实现 audio 命令"
```

---

## Task 6: merge 命令

**Files:**
- Create: `videoclaw/cli/commands/merge.py`

**Step 1: 创建 merge 命令**

```python
"""merge 命令"""
import click
from pathlib import Path
from videoclaw.state import StateManager


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
def merge(project: str):
    """合并视频片段"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    state = StateManager(project_path)

    # 检查上一步是否完成
    audio_step = state.get_step("audio")
    if not audio_step or audio_step.get("status") != "completed":
        click.echo("错误: 请先完成音频生成", err=True)
        return

    state.set_status("merging_video")
    state.update_step("merge", "in_progress")

    click.echo("合并视频...")
    # TODO: 使用 FFmpeg 合并视频

    result = {
        "output_file": str(project_path / "videos" / "final.mp4"),
    }

    state.update_step("merge", "completed", result)
    state.set_status("completed")

    click.echo("视频合并完成!")
```

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: 实现 merge 命令"
```

---

## Task 7: preview 命令

**Files:**
- Create: `videoclaw/cli/commands/preview.py`

**Step 1: 创建 preview 命令**

```python
"""preview 命令"""
import click
import subprocess
from pathlib import Path


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.argument("file_path")
@click.option("--project", "-p", help="项目名称")
def preview(file_path: str, project: str | None):
    """预览图片或视频"""
    path = Path(file_path)

    # 如果是相对路径，结合项目目录
    if project and not path.is_absolute():
        path = DEFAULT_PROJECTS_DIR / project / path

    if not path.exists():
        click.echo(f"错误: 文件 {path} 不存在", err=True)
        return

    # 使用系统默认应用打开
    try:
        subprocess.run(["open", str(path)], check=True)
        click.echo(f"已打开: {path}")
    except Exception as e:
        click.echo(f"打开失败: {e}", err=True)
```

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: 实现 preview 命令"
```

---

## Task 8: config 命令

**Files:**
- Create: `videoclaw/cli/commands/config.py`

**Step 1: 创建 config 命令**

```python
"""config 命令"""
import click
import yaml
from pathlib import Path


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", help="项目名称")
@click.option("--list", "list_config", is_flag=True, help="列出配置")
@click.option("--get", "get_key", help="获取配置值")
@click.option("--set", "set_key", help="设置配置值 (key=value)")
def config(project: str | None, list_config: bool, get_key: str | None, set_key: str | None):
    """管理配置"""
    if project:
        config_path = DEFAULT_PROJECTS_DIR / project / ".videoclaw" / "config.yaml"
    else:
        config_path = Path.home() / ".videoclaw" / "config.yaml"

    # 读取配置
    if config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = {}

    if list_config:
        click.echo(yaml.dump(cfg, default_flow_style=False))
    elif get_key:
        keys = get_key.split(".")
        value = cfg
        for k in keys:
            value = value.get(k)
        click.echo(value)
    elif set_key:
        key, value = set_key.split("=", 1)
        keys = key.split(".")
        d = cfg
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(cfg, f)
        click.echo(f"已设置: {key} = {value}")
    else:
        click.echo("用法: videoclaw config --list | --get key | --set key=value")
```

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: 实现 config 命令"
```

---

## 下一步

Phase 3 完成后，继续 Phase 4 实现 Skills 和厂商具体实现。
