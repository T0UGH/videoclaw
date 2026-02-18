"""config 命令"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import click
import yaml

DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", help="项目名称")
@click.option("--list", "list_config", is_flag=True, help="列出配置")
@click.option("--get", "get_key", help="获取配置值")
@click.option("--set", "set_key", help="设置配置值 (key=value)")
def config(project: Optional[str], list_config: bool, get_key: Optional[str], set_key: Optional[str]):
    """管理配置"""
    if project:
        config_path = DEFAULT_PROJECTS_DIR / project / ".videoclaw" / "config.yaml"
    else:
        config_path = Path.home() / ".videoclaw" / "config.yaml"

    # 读取配置
    if config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
    else:
        cfg = {}

    if list_config:
        click.echo(yaml.dump(cfg, default_flow_style=False))
    elif get_key:
        keys = get_key.split(".")
        value = cfg
        for k in keys:
            value = value.get(k)
        click.echo(value)
    elif set_key:
        key, value = set_key.split("=", 1)
        keys = key.split(".")
        d = cfg
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(cfg, f)
        click.echo(f"已设置: {key} = {value}")
    else:
        click.echo("用法: videoclaw config --list | --get key | --set key=value")
