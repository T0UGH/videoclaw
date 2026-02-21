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
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--model", help="模型名称")
def i2i(input_path: str, prompt: str, output: str, provider: str, model: str | None):
    """图生图 - 独立命令"""
    config = Config()

    # 获取模型名称
    if not model:
        model = config.get(f"models.{provider}.image.model")
        if not model:
            model = config.get(f"{provider}.model")

    # 获取 API key
    api_key = config.get(f"{provider}.api_key")

    backend = get_image_backend(provider, model, {"api_key": api_key})

    # 读取输入图片
    image_bytes = Path(input_path).read_bytes()

    result = backend.image_to_image(image_bytes, prompt)

    # 复制到目标路径
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(result.local_path, output_path)

    click.echo(f"Generated: {output}")
