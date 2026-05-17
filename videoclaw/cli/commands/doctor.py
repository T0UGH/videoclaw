"""doctor 命令。"""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import normalize_image_backend


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

    if backend == "codex-host-image":
        codex_binary = config.get("models.image.codex_binary", "codex")
        resolved = shutil.which(codex_binary)
        if resolved:
            click.echo(f"OK codex binary: {resolved}")
        else:
            click.echo(f"FAIL codex binary not found: {codex_binary}")

        code_home = Path.home() / ".codex"
        click.echo(f"INFO codex home: {code_home}")
        click.echo("INFO auth source: chatgpt_login")
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
        return

    if normalized == "dashscope":
        api_key = config.get("dashscope.api_key")
        click.echo("OK DASHSCOPE_API_KEY configured" if api_key else "FAIL DASHSCOPE_API_KEY missing")
        return

    if normalized == "mock":
        click.echo("OK mock backend available")
        return

    click.echo(f"FAIL unknown backend: {backend}")
