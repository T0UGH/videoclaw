"""上传文件到云盘命令"""
from __future__ import annotations

import click
from pathlib import Path

from videoclaw.config.loader import Config
from videoclaw.storage.factory import get_storage_backend


@click.command()
@click.option("--input", "-i", "input_path", required=True, help="本地文件路径")
@click.option("--remote", "-r", required=True, help="云盘目标路径，如 videoclaw/project/file.mp4")
@click.option("--provider", default="google_drive", help="云盘提供商: google_drive, local")
def upload(input_path: str, remote: str, provider: str):
    """上传文件到云盘

    示例:
        videoclaw upload -i video.mp4 -r videoclaw/my-project/video.mp4
    """
    input_path = Path(input_path)

    if not input_path.exists():
        click.echo(f"错误: 文件不存在: {input_path}", err=True)
        return

    # 加载配置
    config = Config()
    storage_config = config.get_storage_config()

    # 如果命令行指定了 provider，使用命令行的
    actual_provider = provider if provider != "local" else storage_config.get("provider", "local")

    try:
        # 获取存储后端
        storage = get_storage_backend(actual_provider, storage_config)

        click.echo(f"上传中: {input_path.name} -> {remote}")

        # 上传文件
        result = storage.upload(input_path, remote)

        if result.cloud_url:
            click.echo(f"上传成功!")
            click.echo(f"云盘链接: {result.cloud_url}")
        else:
            click.echo(f"上传成功!")

    except FileNotFoundError as e:
        click.echo(f"错误: {e}", err=True)
    except Exception as e:
        click.echo(f"上传失败: {e}", err=True)
