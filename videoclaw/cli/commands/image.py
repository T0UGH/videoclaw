"""image 命令。"""
from __future__ import annotations

import click

from videoclaw.cli.commands.i2i import i2i
from videoclaw.cli.commands.t2i import t2i
from videoclaw.config.loader import Config
from videoclaw.models.factory import get_image_backend


@click.group()
def image():
    """管理图片生成与诊断"""
    pass


image.add_command(t2i, name="t2i")
image.add_command(i2i, name="i2i")


@image.command("smoke")
@click.option("--backend", required=True, help="要测试的图片 backend")
@click.option("--project", help="项目名称或项目路径")
def image_smoke(backend: str, project: str | None):
    """执行图片 backend 的最小 smoke 测试。"""
    from pathlib import Path

    project_path = None
    if project:
        candidate = Path(project).expanduser()
        project_path = candidate if candidate.exists() else Path.home() / "videoclaw-projects" / project

    config = Config(project_path)
    image_config = config.get_image_backend_config()
    image_config["backend"] = backend
    model = image_config.get("model") or "smoke-test"

    backend_impl = get_image_backend(backend, model, image_config)
    result = backend_impl.text_to_image("smoke test image")
    click.echo(f"OK image smoke generated: {result.local_path}")
