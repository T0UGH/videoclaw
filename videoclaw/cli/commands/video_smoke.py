"""video 命令。"""
from __future__ import annotations

import base64
from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import get_video_backend


_MINIMAL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR42mNg+M/AAAMBAQAY3Y2xAAAAAElFTkSuQmCC"
)


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
    all_config = config.get_all()
    all_config.setdefault("ark", {})
    all_config["ark"]["api_key"] = config.get("ark.api_key")
    model = config.get("models.video.model") or ("doubao-seedance-2-0-260128" if backend == "volcengine" else "smoke-test")
    backend_impl = get_video_backend(backend, model, all_config)
    result = backend_impl.image_to_video(_MINIMAL_PNG, "smoke test video")
    click.echo(f"OK video smoke generated: {result.local_path}")
