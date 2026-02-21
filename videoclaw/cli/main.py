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


@main.command()
@click.argument("project_name")
@click.option("--dir", "project_dir", default=None, help="项目目录路径")
@click.option("--interactive/--no-interactive", default=True, help="交互式配置")
def init(project_name: str, project_dir: Optional[str], interactive: bool):
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

    # 创建配置
    if interactive:
        # 1. 选择图像提供商
        click.echo("\n选择图像生成提供商:")
        click.echo("  1) volcengine (火山引擎 Seedream)")
        click.echo("  2) dashscope (阿里云)")
        click.echo("  3) gemini (Google)")
        click.echo("  4) mock (测试用)")
        provider_map = {"1": "volcengine", "2": "dashscope", "3": "gemini", "4": "mock"}
        choice = click.prompt("请选择 (1-4)", type=str, default="1")
        image_provider = provider_map.get(choice, "volcengine")

        # 2. 选择视频提供商
        click.echo("\n选择视频生成提供商:")
        click.echo("  1) volcengine (火山引擎 Seedance)")
        click.echo("  2) dashscope (阿里云)")
        click.echo("  3) mock (测试用)")
        choice = click.prompt("请选择 (1-3)", type=str, default="1")
        video_provider = provider_map.get(choice, "volcengine")

        # 3. 选择存储方式
        click.echo("\n选择存储方式:")
        click.echo("  1) local (本地存储)")
        click.echo("  2) google_drive (上传到 Google Drive)")
        choice = click.prompt("请选择 (1-2)", type=str, default="1")
        storage_provider = "local" if choice == "1" else "google_drive"

        # 生成配置
        config = {
            "project_name": project_name,
            "version": "0.1.0",
            "models": {
                "image": {"provider": image_provider},
                "video": {"provider": video_provider},
            },
            "storage": {"provider": storage_provider}
        }
    else:
        config = {
            "project_name": project_name,
            "version": "0.1.0",
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
