"""doctor 命令。"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import normalize_image_backend

VIDEO_BACKEND_ALIASES = {
    "mock-video": "mock",
    "volcengine-video": "volcengine",
    "dashscope-video": "dashscope",
}


def has_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@click.command()
@click.option("--backend", required=True, help="要检查的 backend")
@click.option("--project", help="项目名称或项目路径")
def doctor(backend: str, project: str | None):
    """检查 backend 的本机环境与配置。"""
    project_path = None
    if project:
        candidate = Path(project).expanduser()
        project_path = candidate if candidate.exists() else Path.home() / "videoclaw-projects" / project

    config = Config(project_path)
    normalized = normalize_image_backend(backend)
    video_normalized = VIDEO_BACKEND_ALIASES.get(backend)

    if video_normalized == "mock":
        click.echo("OK mock video backend available")
        click.echo(f"{'OK' if has_ffmpeg() else 'FAIL'} ffmpeg available")
        return

    if video_normalized == "volcengine":
        api_key = config.get("ark.api_key")
        click.echo("OK ARK_API_KEY configured" if api_key else "FAIL ARK_API_KEY missing")
        click.echo(f"{'OK' if has_ffmpeg() else 'FAIL'} ffmpeg available")
        return

    if video_normalized == "dashscope":
        api_key = config.get("dashscope.api_key")
        click.echo("OK DASHSCOPE_API_KEY configured" if api_key else "FAIL DASHSCOPE_API_KEY missing")
        click.echo(f"{'OK' if has_ffmpeg() else 'FAIL'} ffmpeg available")
        return

    if backend == "codex-host-image":
        from videoclaw.models.codex_host_image import CodexHostImageBackend

        token = CodexHostImageBackend(model="gpt-image-2-medium", config={})._read_codex_access_token()
        click.echo(f"backend: {backend}")
        click.echo("auth: chatgpt_login")
        click.echo("transport: codex_oauth")
        click.echo(f"status: {'available' if token else 'unavailable'}")
        click.echo(f"token_source: {'~/.hermes/auth.json' if token else 'missing'}")
        click.echo("available_models: gpt-image-2-low, gpt-image-2-medium, gpt-image-2-high")
        click.echo("recommended_model: gpt-image-2-medium")
        return

    if backend == "openai-image":
        api_key = config.get("openai.api_key")
        if api_key:
            click.echo("OK OPENAI_API_KEY configured")
        else:
            click.echo("FAIL OPENAI_API_KEY missing")
        click.echo("INFO execution surface: openai_api")
        return

    if normalized == "gemini":
        api_key = config.get("google.api_key")
        click.echo("OK GOOGLE_API_KEY configured" if api_key else "FAIL GOOGLE_API_KEY missing")
        return

    if normalized == "volcengine":
        api_key = config.get("ark.api_key")
        click.echo("OK ARK_API_KEY configured" if api_key else "FAIL ARK_API_KEY missing")
        if "video" in backend or backend in {"volcengine-video", "volcengine"}:
            click.echo(f"{'OK' if has_ffmpeg() else 'FAIL'} ffmpeg available")
        return

    if normalized == "dashscope":
        api_key = config.get("dashscope.api_key")
        click.echo("OK DASHSCOPE_API_KEY configured" if api_key else "FAIL DASHSCOPE_API_KEY missing")
        if "video" in backend or backend in {"dashscope-video", "dashscope"}:
            click.echo(f"{'OK' if has_ffmpeg() else 'FAIL'} ffmpeg available")
        return

    if normalized == "mock":
        click.echo("OK mock backend available")
        if "video" in backend or backend == "mock-video":
            click.echo(f"{'OK' if has_ffmpeg() else 'FAIL'} ffmpeg available")
        return

    click.echo(f"FAIL unknown backend: {backend}")
