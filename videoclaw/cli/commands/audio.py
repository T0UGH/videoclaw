"""audio 命令"""
from __future__ import annotations

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
