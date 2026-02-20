"""assets 命令"""
from __future__ import annotations

import click
import json
import shutil
from pathlib import Path

from videoclaw.state import StateManager
from videoclaw.config import Config
from videoclaw.models.factory import get_image_backend
from videoclaw.utils.logging import get_logger


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


def ask_confirm(prompt: str) -> str:
    """Ask user for confirmation, return 'y' (yes), 'n' (no), 'r' (retry/adjust)"""
    while True:
        answer = input(f"{prompt} (y/n/r): ").strip().lower()
        if answer in ['y', 'n', 'r']:
            return answer
        click.echo("请输入 y (是), n (否), 或 r (调整)")


def generate_asset_with_confirm(image_backend, prompt: str, dest_path: Path, item_name: str, logger) -> tuple[bool, str]:
    """
    Generate an asset and ask for confirmation.
    Returns: (confirmed: bool, final_prompt: str)
    """
    while True:
        click.echo(f"生成中: {item_name}...")
        logger.info(f"生成 {item_name}, prompt: {prompt}")

        try:
            gen_result = image_backend.text_to_image(prompt)

            if gen_result.local_path:
                shutil.copy(gen_result.local_path, dest_path)
                logger.info(f"已保存: {dest_path}")
        except Exception as e:
            logger.error(f"生成失败: {e}")
            click.echo(f"生成失败: {e}")

        # Show result and ask
        click.echo(f"生成完成: {dest_path}")
        click.echo(f"提示词: {prompt}")

        answer = ask_confirm("这个可以吗？")

        if answer == 'y':
            # Confirmed
            return True, prompt
        elif answer == 'n':
            # Skip this item
            return False, prompt
        else:
            # Retry with adjusted prompt
            new_prompt = input("请输入调整后的提示词: ").strip()
            if new_prompt:
                prompt = new_prompt
                click.echo(f"调整提示词: {prompt}")
            # Loop to regenerate


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, mock")
@click.option("--yes", "-y", is_flag=True, help="跳过确认，直接使用生成的图片")
@click.option("--use-local", is_flag=True, help="使用本地图片，不调用T2I")
def assets(project: str, provider: str, yes: bool, use_local: bool):
    """生成角色和场景图片资产"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始生成资产，项目: {project}")

    state = StateManager(project_path)
    config = Config(project_path)

    # 检查上一步是否完成
    analyze_step = state.get_step("analyze")
    if not analyze_step or analyze_step.get("status") != "completed":
        logger.error("请先完成脚本分析")
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
    logger.info(f"开始生成 {len(characters)} 个角色图片")

    for char in characters:
        char_name = char.get("name", "character")
        char_desc = char.get("description", "")

        # 检查本地图片
        dest_path = assets_dir / f"character_{char_name}.png"

        if use_local and dest_path.exists():
            click.echo(f"使用本地图片: {dest_path}")
            result["characters"][char_name] = str(dest_path)
            continue

        if yes:
            # 自动模式：直接生成，不确认
            prompt = f"宇航员角色，高清，{char_desc}"
            try:
                gen_result = image_backend.text_to_image(prompt)
                if gen_result.local_path:
                    shutil.copy(gen_result.local_path, dest_path)
                    result["characters"][char_name] = str(dest_path)
                    click.echo(f"  已保存: {dest_path}")
            except Exception as e:
                logger.error(f"生成失败: {e}")
                click.echo(f"  生成失败: {e}")
        else:
            # 交互模式：生成后确认
            prompt = f"宇航员角色，高清，{char_desc}"
            confirmed, final_prompt = generate_asset_with_confirm(
                image_backend, prompt, dest_path, f"角色: {char_name}", logger
            )
            if confirmed:
                result["characters"][char_name] = str(dest_path)
            else:
                click.echo(f"跳过角色: {char_name}")

    # 生成场景图片
    scenes = analyze_data.get("scenes", [])
    logger.info(f"开始生成 {len(scenes)} 个场景图片")

    for scene in scenes:
        scene_name = scene.get("name", "scene")
        scene_desc = scene.get("description", "")

        # 检查本地图片
        dest_path = assets_dir / f"scene_{scene_name}.png"

        if use_local and dest_path.exists():
            click.echo(f"使用本地图片: {dest_path}")
            result["scenes"][scene_name] = str(dest_path)
            continue

        if yes:
            # 自动模式：直接生成，不确认
            prompt = f"火星场景，{scene_desc}，高清，电影感"
            try:
                gen_result = image_backend.text_to_image(prompt)
                if gen_result.local_path:
                    shutil.copy(gen_result.local_path, dest_path)
                    result["scenes"][scene_name] = str(dest_path)
                    click.echo(f"  已保存: {dest_path}")
            except Exception as e:
                logger.error(f"生成失败: {e}")
                click.echo(f"  生成失败: {e}")
        else:
            # 交互模式：生成后确认
            prompt = f"火星场景，{scene_desc}，高清，电影感"
            confirmed, final_prompt = generate_asset_with_confirm(
                image_backend, prompt, dest_path, f"场景: {scene_name}", logger
            )
            if confirmed:
                result["scenes"][scene_name] = str(dest_path)
            else:
                click.echo(f"跳过场景: {scene_name}")

    state.update_step("assets", "completed", result)
    state.set_status("assets_generated")

    logger.info(f"资产生成完成: {len(result['characters'])} 个角色, {len(result['scenes'])} 个场景")
    click.echo("资产生成完成!")
