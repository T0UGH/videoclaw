"""merge 命令"""
from __future__ import annotations

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
