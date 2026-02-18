"""storyboard 命令"""
from __future__ import annotations

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
