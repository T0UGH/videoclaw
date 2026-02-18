"""preview 命令"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import click

DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.argument("file_path")
@click.option("--project", "-p", help="项目名称")
def preview(file_path: str, project: Optional[str]):
    """预览图片或视频"""
    path = Path(file_path)

    # 如果是相对路径，结合项目目录
    if project and not path.is_absolute():
        path = DEFAULT_PROJECTS_DIR / project / path

    if not path.exists():
        click.echo(f"错误: 文件 {path} 不存在", err=True)
        return

    # 使用系统默认应用打开
    try:
        subprocess.run(["open", str(path)], check=True)
        click.echo(f"已打开: {path}")
    except Exception as e:
        click.echo(f"打开失败: {e}", err=True)
