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
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--use-local", is_flag=True, help="使用本地图片，不调用T2I")
@click.option("--num-variants", "-n", default=1, type=int, help="生成候选数量 (默认1)")
def assets(project: str, provider: str, use_local: bool, num_variants: int):
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

        # 生成多个变体
        variants = []
        chosen_path = None

        for i in range(num_variants):
            # 构建 variant 文件名
            if num_variants > 1:
                dest_path = assets_dir / f"character_{char_name}_{i+1}.png"
            else:
                dest_path = assets_dir / f"character_{char_name}.png"

            # 检查本地图片（只检查第一个）
            if i == 0 and dest_path.exists():
                click.echo(f"使用本地图片: {dest_path}")
                result["characters"][char_name] = str(dest_path)
                variants.append(str(dest_path))
                chosen_path = str(dest_path)
                break

            # AI 生成
            prompt = char_desc
            try:
                gen_result = image_backend.text_to_image(prompt)
                if gen_result.local_path:
                    shutil.copy(gen_result.local_path, dest_path)
                    variants.append(str(dest_path))
                    logger.info(f"已保存: {dest_path}")
                    click.echo(f"  已保存: {dest_path}")

                    # 第一个变体作为默认选择
                    if i == 0:
                        chosen_path = str(dest_path)
                        result["characters"][char_name] = chosen_path

                        # 上传到云盘
                        cloud_url = upload_to_cloud(
                            dest_path,
                            f"videoclaw/{project}/assets/{dest_path.name}",
                            config,
                            project
                        )
                        if cloud_url:
                            click.echo(f"  云盘链接: {cloud_url}")
            except Exception as e:
                logger.error(f"生成失败: {e}")
                click.echo(f"  生成失败: {e}")

        # 记录所有变体到结果中
        if num_variants > 1 and variants:
            result["characters"][char_name] = {
                "chosen": chosen_path,
                "variants": variants
            }

    # 生成场景图片
    scenes = analyze_data.get("scenes", [])
    logger.info(f"开始生成 {len(scenes)} 个场景图片")

    for scene in scenes:
        scene_name = scene.get("name", "scene")
        scene_desc = scene.get("description", "")

        # 生成多个变体
        variants = []
        chosen_path = None

        for i in range(num_variants):
            # 构建 variant 文件名
            if num_variants > 1:
                dest_path = assets_dir / f"scene_{scene_name}_{i+1}.png"
            else:
                dest_path = assets_dir / f"scene_{scene_name}.png"

            # 检查本地图片（只检查第一个）
            if i == 0 and dest_path.exists():
                click.echo(f"使用本地图片: {dest_path}")
                result["scenes"][scene_name] = str(dest_path)
                variants.append(str(dest_path))
                chosen_path = str(dest_path)
                break

            # AI 生成
            prompt = scene_desc
            try:
                gen_result = image_backend.text_to_image(prompt)
                if gen_result.local_path:
                    shutil.copy(gen_result.local_path, dest_path)
                    variants.append(str(dest_path))
                    logger.info(f"已保存: {dest_path}")
                    click.echo(f"  已保存: {dest_path}")

                    # 第一个变体作为默认选择
                    if i == 0:
                        chosen_path = str(dest_path)
                        result["scenes"][scene_name] = chosen_path

                        # 上传到云盘
                        cloud_url = upload_to_cloud(
                            dest_path,
                            f"videoclaw/{project}/assets/{dest_path.name}",
                            config,
                            project
                        )
                        if cloud_url:
                            click.echo(f"  云盘链接: {cloud_url}")
            except Exception as e:
                logger.error(f"生成失败: {e}")
                click.echo(f"  生成失败: {e}")

        # 记录所有变体到结果中
        if num_variants > 1 and variants:
            result["scenes"][scene_name] = {
                "chosen": chosen_path,
                "variants": variants
            }

    state.update_step("assets", "completed", result)
    state.set_status("assets_generated")

    logger.info(f"资产生成完成: {len(result['characters'])} 个角色, {len(result['scenes'])} 个场景")
    click.echo("资产生成完成!")
