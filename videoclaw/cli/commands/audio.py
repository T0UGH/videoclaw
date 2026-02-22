"""audio 命令"""
from __future__ import annotations

import click
import shutil
from pathlib import Path

from videoclaw.config import Config
from videoclaw.models.factory import get_audio_backend
from videoclaw.utils.logging import get_logger
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--text", "-t", multiple=True, help="TTS 文本内容（可多次指定）")
@click.option("--duration", default=30, help="背景音乐时长（秒）")
@click.option("--style", default="流行", help="背景音乐风格")
def audio(project: str, provider: str, text: tuple, duration: int, style: str):
    """生成音频（TTS、音效、背景音乐）"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始生成音频，项目: {project}")

    config = Config(project_path)

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

    # 生成对话（使用命令行传入的文本）
    text_list = list(text)
    if text_list:
        for i, t in enumerate(text_list):
            click.echo(f"生成对话 {i+1}: {t[:30]}...", nl=False)

            # 调用 TTS 生成语音
            gen_result = audio_backend.text_to_speech(t)

            # 保存到项目目录
            dest_path = audio_dir / f"dialogue_{i+1:03d}.mp3"
            if gen_result.local_path:
                shutil.copy(gen_result.local_path, dest_path)
                result["dialogues"].append({
                    "index": i + 1,
                    "path": str(dest_path),
                    "text": t
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
    else:
        click.echo("警告: 未提供文本内容，跳过对话生成")

    # 生成背景音乐
    click.echo(f"\n生成背景音乐 (风格: {style}, 时长: {duration}秒)...", nl=False)
    bgm_result = audio_backend.generate_bgm(style, duration=duration)

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

    click.echo("\n音频生成完成!")
