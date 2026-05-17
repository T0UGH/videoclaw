"""独立图生图命令"""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import get_image_backend


@click.command()
@click.option("--input", "-i", "input_path", required=True, help="输入图片路径")
@click.option("--prompt", "-p", required=True, help="生成提示词")
@click.option("--output", "-o", required=True, help="输出文件路径")
@click.option("--provider", default=None, help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--model", help="模型名称")
def i2i(input_path: str, prompt: str, output: str, provider: str | None, model: str | None):
    """图生图 - 独立命令"""
    config = Config()
    image_config = config.get_image_backend_config()
    backend_name = provider or image_config.get("backend", "codex-host-image")

    if not model:
        model = image_config.get("model")
        if not model:
            normalized = backend_name.replace("-image", "")
            model = config.get(f"models.{normalized}.image.model")
            if not model:
                model = config.get(f"{normalized}.model")

    backend = get_image_backend(backend_name, model or "", image_config)
    image_bytes = Path(input_path).read_bytes()
    result = backend.image_to_image(image_bytes, prompt)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(result.local_path, output_path)

    click.echo(f"Generated: {output}")
