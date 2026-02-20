"""assets 命令"""
from __future__ import annotations

import click
import json
from pathlib import Path

from videoclaw.state import StateManager
from videoclaw.config import Config
from videoclaw.models.factory import get_image_backend


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, mock")
def assets(project: str, provider: str):
    """生成角色和场景图片资产"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    state = StateManager(project_path)
    config = Config(project_path)

    # 检查上一步是否完成
    analyze_step = state.get_step("analyze")
    if not analyze_step or analyze_step.get("status") != "completed":
        click.echo("错误: 请先完成脚本分析", err=True)
        return

    state.set_status("generating_assets")
    state.update_step("assets", "in_progress")

    # 获取分析结果
    analyze_data = analyze_step.get("output", {})

    # 获取模型
    model = config.get("models.image.model", "")
    image_backend = get_image_backend(provider, model, config.get_all())

    assets_dir = project_path / "assets"
    assets_dir.mkdir(exist_ok=True)

    result = {
        "characters": {},
        "scenes": {},
    }

    # 生成角色图片
    characters = analyze_data.get("characters", [])
    for char in characters:
        char_name = char.get("name", "character")
        char_desc = char.get("description", "")

        click.echo(f"生成角色图片: {char_name}")
        prompt = f"宇航员角色，高清，{char_desc}"
        gen_result = image_backend.text_to_image(prompt)

        # 复制到项目目录
        dest_path = assets_dir / f"character_{char_name}.png"
        if gen_result.local_path:
            import shutil
            shutil.copy(gen_result.local_path, dest_path)
            result["characters"][char_name] = str(dest_path)
            click.echo(f"  已保存: {dest_path}")

    # 生成场景图片
    scenes = analyze_data.get("scenes", [])
    for scene in scenes:
        scene_name = scene.get("name", "scene")
        scene_desc = scene.get("description", "")

        click.echo(f"生成场景图片: {scene_name}")
        prompt = f"火星场景，{scene_desc}，高清，电影感"
        gen_result = image_backend.text_to_image(prompt)

        # 复制到项目目录
        dest_path = assets_dir / f"scene_{scene_name}.png"
        if gen_result.local_path:
            import shutil
            shutil.copy(gen_result.local_path, dest_path)
            result["scenes"][scene_name] = str(dest_path)
            click.echo(f"  已保存: {dest_path}")

    state.update_step("assets", "completed", result)
    state.set_status("assets_generated")

    click.echo("资产生成完成!")
