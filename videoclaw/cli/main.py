"""CLI 主入口"""
from __future__ import annotations

import click
import json
from pathlib import Path
from typing import Optional

from videoclaw.cli.commands.assets import assets
from videoclaw.cli.commands.storyboard import storyboard
from videoclaw.cli.commands.i2v import i2v
from videoclaw.cli.commands.i2v_from_storyboard import i2v_from_storyboard
from videoclaw.cli.commands.audio import audio
from videoclaw.cli.commands.merge import merge
from videoclaw.cli.commands.preview import preview
from videoclaw.cli.commands.config import config
from videoclaw.cli.commands.validate import validate
from videoclaw.cli.commands.t2i import t2i
from videoclaw.cli.commands.i2i import i2i
from videoclaw.cli.commands.upload import upload
from videoclaw.cli.commands.publish import publish


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.group()
@click.version_option()
def main():
    """Videoclaw - AI 视频创作 CLI 工具"""
    pass


# 注册子命令
main.add_command(assets)
main.add_command(storyboard)
main.add_command(i2v)
main.add_command(i2v_from_storyboard)
main.add_command(audio)
main.add_command(merge)
main.add_command(preview)
main.add_command(config)
main.add_command(validate)
main.add_command(t2i)
main.add_command(i2i)
main.add_command(upload)
main.add_command(publish)


@main.command()
@click.argument("project_name")
@click.option("--dir", "project_dir", default=None, help="项目目录路径")
@click.option("--interactive/--no-interactive", default=False, help="交互式配置")
def init(project_name: str, project_dir: Optional[str], interactive: bool):
    """初始化新的视频项目"""
    projects_dir = Path(project_dir) if project_dir else DEFAULT_PROJECTS_DIR
    project_path = projects_dir / project_name

    if project_path.exists():
        # 检查配置文件是否存在，不存在则创建
        config_file = project_path / ".videoclaw" / "config.yaml"
        if config_file.exists():
            click.echo(f"项目 {project_name} 已存在", err=True)
            return
        # 确保必要的子目录存在
        (project_path / ".videoclaw").mkdir(exist_ok=True)
        (project_path / "assets").mkdir(exist_ok=True)
        (project_path / "storyboard").mkdir(exist_ok=True)
        (project_path / "videos").mkdir(exist_ok=True)
        (project_path / "audio").mkdir(exist_ok=True)
    else:
        project_path.mkdir(parents=True)
        (project_path / ".videoclaw").mkdir()
        (project_path / "assets").mkdir()
        (project_path / "storyboard").mkdir()
        (project_path / "videos").mkdir()
        (project_path / "audio").mkdir()

    # 创建配置（默认非交互式）
    config = {
        "project_name": project_name,
        "version": "0.1.0",
        "models": {
            "image": {"provider": "volcengine"},
            "video": {"provider": "volcengine"},
        },
        "storage": {"provider": "local"}
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


if __name__ == "__main__":
    main()
