"""独立文生图命令"""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import get_image_backend


@click.command()
@click.option("--prompt", "-p", required=True, help="生成提示词")
@click.option("--output", "-o", required=True, help="输出文件路径")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--model", help="模型名称")
def t2i(prompt: str, output: str, provider: str, model: str | None):
    """文生图 - 独立命令"""
    config = Config()

    # 获取模型名称
    if not model:
        model = config.get(f"models.{provider}.image.model")
        if not model:
            # 兼容旧配置
            model = config.get(f"{provider}.model")

    # 获取 API key
    api_key = config.get(f"{provider}.api_key")

    backend = get_image_backend(provider, model, {"api_key": api_key})

    result = backend.text_to_image(prompt)

    # 复制到目标路径
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(result.local_path, output_path)

    click.echo(f"Generated: {output}")
