"""audio 命令"""
from __future__ import annotations

import click
import shutil
from pathlib import Path

from videoclaw.state import StateManager
from videoclaw.config import Config
from videoclaw.models.factory import get_audio_backend
from videoclaw.utils.logging import get_logger
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
def audio(project: str, provider: str):
    """生成音频（TTS、音效、背景音乐）"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始生成音频，项目: {project}")

    state = StateManager(project_path)
    config = Config(project_path)

    # 检查上一步是否完成
    i2v_step = state.get_step("i2v")
    if not i2v_step or i2v_step.get("status") != "completed":
        click.echo("错误: 请先完成视频生成", err=True)
        return

    # 获取分析数据用于对话
    analyze_step = state.get_step("analyze")
    analyze_data = analyze_step.get("output", {})

    state.set_status("generating_audio")
    state.update_step("audio", "in_progress")

    # 获取模型
    model = config.get("models.audio.model", "default")
    audio_backend = get_audio_backend(provider, model, config.get_all())

    audio_dir = project_path / "audio"
    audio_dir.mkdir(exist_ok=True)

    result = {
        "dialogues": [],
        "sfx": [],
        "bgm": None,
    }

    # 获取帧信息用于生成对话
    frames = analyze_data.get("frames", [])

    # 生成对话
    for frame in frames:
        frame_id = frame.get("frame_id", 0)
        frame_desc = frame.get("description", "")

        # 为每帧生成简短旁白
        text = f"第{frame_id}帧: {frame_desc}"
        click.echo(f"生成对话 {frame_id}: {text[:30]}...", nl=False)

        # 调用 TTS 生成语音
        gen_result = audio_backend.text_to_speech(text)

        # 保存到项目目录
        dest_path = audio_dir / f"dialogue_{frame_id:03d}.mp3"
        if gen_result.local_path:
            shutil.copy(gen_result.local_path, dest_path)
            result["dialogues"].append({
                "frame_id": frame_id,
                "path": str(dest_path),
                "text": text
            })
            click.echo(f" 已保存: {dest_path.name}")

            # 上传到云盘
            cloud_url = upload_to_cloud(
                dest_path,
                f"videoclaw/{project}/audio/{dest_path.name}",
                config,
                project
            )
            if cloud_url:
                click.echo(f" 云盘链接: {cloud_url}")

    # 生成背景音乐
    click.echo("\n生成背景音乐...", nl=False)
    bgm_result = audio_backend.generate_bgm("科幻 悬疑 友情", duration=30)

    if bgm_result and bgm_result.local_path:
        bgm_path = audio_dir / "bgm.mp3"
        shutil.copy(bgm_result.local_path, bgm_path)
        result["bgm"] = str(bgm_path)
        click.echo(f" 已保存: bgm.mp3")

        # 上传到云盘
        cloud_url = upload_to_cloud(
            bgm_path,
            f"videoclaw/{project}/audio/{bgm_path.name}",
            config,
            project
        )
        if cloud_url:
            click.echo(f" 云盘链接: {cloud_url}")

    state.update_step("audio", "completed", result)
    state.set_status("audio_generated")

    click.echo("\n音频生成完成!")
