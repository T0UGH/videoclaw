# Phase 1: Project Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 建立 videoclaw CLI 工具的基础框架，包括项目结构、pyproject.toml、CLI 入口、配置管理

**Architecture:** 使用 Click 构建 CLI，uv 管理依赖，Pydantic 管理配置

**Tech Stack:** Python 3.11+, uv, Click, Pydantic, PyYAML

---

## Task 1: 创建项目结构和 pyproject.toml

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.gitignore`

**Step 1: 创建 pyproject.toml**

```toml
[project]
name = "videoclaw"
version = "0.1.0"
description = "AI 视频创作 CLI 工具，给 Claude Code 用"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
]

[project.scripts]
videoclaw = "videoclaw.cli:main"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["videoclaw*"]

[tool.ruff]
target-version = "py311"

[tool.black]
target-version = ["py311"]
```

**Step 2: 创建 README.md**

```markdown
# Videoclaw

AI 视频创作 CLI 工具，给 Claude Code 用。

## 安装

```bash
pip install -e .
```

## 使用

```bash
videoclaw --help
```
```

**Step 3: 创建 .gitignore**

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.env
.venv
env/
venv/
```

**Step 4: Commit**

```bash
git add pyproject.toml README.md .gitignore
git commit -m "chore: 初始化项目结构"
```

---

## Task 2: 创建 CLI 入口和基础命令

**Files:**
- Create: `videoclaw/__init__.py`
- Create: `videoclaw/cli/__init__.py`
- Create: `videoclaw/cli/main.py`

**Step 1: 创建 videoclaw/__init__.py**

```python
"""Videoclaw - AI 视频创作 CLI 工具"""

__version__ = "0.1.0"
```

**Step 2: 创建 videoclaw/cli/__init__.py**

```python
"""CLI 模块"""
```

**Step 3: 创建 videoclaw/cli/main.py**

```python
"""CLI 主入口"""
import click


@click.group()
@click.version_option()
def main():
    """Videoclaw - AI 视频创作 CLI 工具"""
    pass


@main.command()
def init():
    """初始化新的视频项目"""
    click.echo("初始化项目...")


if __name__ == "__main__":
    main()
```

**Step 4: 安装依赖并测试**

```bash
uv pip install -e ".[dev]"
videoclaw --help
```

**预期输出:**
```
Usage: videoclaw [OPTIONS] COMMAND [ARGS]...

  Videoclaw - AI 视频创作 CLI 工具

Options:
  --help  Show this message and exit.
```

**Step 5: Commit**

```bash
git add videoclaw/
git commit -m "feat: 添加 CLI 入口和基础命令"
```

---

## Task 3: 添加 init 和 status 命令

**Files:**
- Modify: `videoclaw/cli/main.py`

**Step 1: 添加完整命令**

```python
import click
import os
import json
from pathlib import Path


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.group()
@click.version_option()
def main():
    """Videoclaw - AI 视频创作 CLI 工具"""
    pass


@main.command()
@click.argument("project_name")
@click.option("--dir", "project_dir", default=None, help="项目目录路径")
def init(project_name: str, project_dir: str | None):
    """初始化新的视频项目"""
    projects_dir = Path(project_dir) if project_dir else DEFAULT_PROJECTS_DIR
    project_path = projects_dir / project_name

    if project_path.exists():
        click.echo(f"错误: 项目 {project_name} 已存在", err=True)
        return

    # 创建项目结构
    project_path.mkdir(parents=True)
    (project_path / ".videoclaw").mkdir()
    (project_path / "assets").mkdir()
    (project_path / "storyboard").mkdir()
    (project_path / "videos").mkdir()
    (project_path / "audio").mkdir()

    # 创建配置和状态文件
    config = {
        "project_name": project_name,
        "version": "0.1.0",
        "storage": {"type": "local"},
    }
    state = {
        "project_id": project_name,
        "status": "initialized",
        "steps": {},
    }

    import yaml
    with open(project_path / ".videoclaw" / "config.yaml", "w") as f:
        yaml.dump(config, f)

    with open(project_path / ".videoclaw" / "state.json", "w") as f:
        json.dump(state, f, indent=2)

    click.echo(f"项目 {project_name} 已创建于 {project_path}")


@main.command()
@click.argument("script_text", required=False)
@click.option("--project", "-p", help="项目名称")
def analyze(script_text: str | None, project: str | None):
    """分析脚本，提取角色、场景、帧"""
    click.echo("分析脚本...")


@main.command()
@click.option("--project", "-p", required=True, help="项目名称")
def status(project: str):
    """查看项目状态"""
    project_path = DEFAULT_PROJECTS_DIR / project / ".videoclaw" / "state.json"

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    with open(project_path) as f:
        state = json.load(f)

    click.echo(f"项目: {state['project_id']}")
    click.echo(f"状态: {state['status']}")
    click.echo("\n步骤状态:")
    for step, info in state.get("steps", {}).items():
        click.echo(f"  {step}: {info.get('status', 'unknown')}")
```

**Step 2: 测试命令**

```bash
videoclaw init my-test-project
videoclaw status --project my-test-project
```

**预期输出:**
```
项目 my-test-project 已创建于 ~/videoclaw-projects/my-test-project
项目: my-test-project
状态: initialized

步骤状态:
```

**Step 3: Commit**

```bash
git add videoclaw/
git commit -m "feat: 添加 init 和 status 命令"
```

---

## Task 4: 配置管理模块

**Files:**
- Create: `videoclaw/config/__init__.py`
- Create: `videoclaw/config/loader.py`

**Step 1: 创建配置加载器**

```python
"""配置管理模块"""
import os
import yaml
from pathlib import Path
from typing import Any


class Config:
    """配置管理类"""

    def __init__(self):
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self):
        # 1. 加载全局配置
        global_config_path = Path.home() / ".videoclaw" / "config.yaml"
        if global_config_path.exists():
            with open(global_config_path) as f:
                self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        # 检查环境变量
        env_key = f"VIDEOCLAW_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]

        # 返回配置值
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_all(self) -> dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
```

**Step 2: 创建 __init__.py**

```python
"""配置模块"""
from videoclaw.config.loader import Config

config = Config()

__all__ = ["Config", "config"]
```

**Step 3: 测试**

```python
# tests/test_config.py
from videoclaw.config import config


def test_config_get():
    assert config.get("storage.type") == "local"
```

**Step 4: Commit**

```bash
git add videoclaw/config/
git commit -m "feat: 添加配置管理模块"
```

---

## 下一步

Phase 1 完成后，继续 Phase 2 实现存储抽象层和模型抽象层。
