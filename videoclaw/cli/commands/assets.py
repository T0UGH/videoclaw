"""assets 命令"""
from __future__ import annotations

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
