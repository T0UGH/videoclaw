"""video 命令。"""
from __future__ import annotations

from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import get_video_backend


@click.command("smoke")
@click.option("--backend", required=True, help="要测试的视频 backend")
@click.option("--project", help="项目名称或项目路径")
def video_smoke(backend: str, project: str | None):
    """执行视频 backend 的最小 smoke 测试。"""
    project_path = None
    if project:
        candidate = Path(project).expanduser()
        project_path = candidate if candidate.exists() else Path.home() / "videoclaw-projects" / project

    config = Config(project_path)
    model = config.get("models.video.model") or "smoke-test"
    backend_impl = get_video_backend(backend, model, config.get_all())
    result = backend_impl.image_to_video(b"placeholder-image", "smoke test video")
    click.echo(f"OK video smoke generated: {result.local_path}")
