"""i2v 命令"""
from __future__ import annotations

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
