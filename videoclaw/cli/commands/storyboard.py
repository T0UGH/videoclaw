"""storyboard 命令"""
from __future__ import annotations

import click
import shutil
from pathlib import Path
from io import BytesIO

from PIL import Image
from videoclaw.state import StateManager
from videoclaw.config import Config
from videoclaw.models.factory import get_image_backend
from videoclaw.utils.logging import get_logger
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--num-variants", "-n", default=1, type=int, help="生成候选数量 (默认1)")
def storyboard(project: str, provider: str, num_variants: int):
    """生成故事板帧图片"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始生成故事板，项目: {project}")

    state = StateManager(project_path)
    config = Config(project_path)

    # 检查上一步是否完成
    assets_step = state.get_step("assets")
    if not assets_step or assets_step.get("status") != "completed":
        click.echo("错误: 请先完成资产生成", err=True)
        return

    # 检查 analyze 步骤
    analyze_step = state.get_step("analyze")
    if not analyze_step or analyze_step.get("status") != "completed":
        click.echo("错误: 请先完成脚本分析", err=True)
        return

    state.set_status("rendering_storyboard")
    state.update_step("storyboard", "in_progress")

    # 获取分析结果中的帧
    analyze_data = analyze_step.get("output", {})
    frames = analyze_data.get("frames", [])

    # 获取角色图片（用于保持人物一致性）
    assets_data = assets_step.get("output", {})
    character_images = assets_data.get("characters", {})
    character_bytes = {}
    for char_name, char_path in character_images.items():
        if char_path and Path(char_path).exists():
            with Image.open(char_path) as img:
                # 转换为 RGB 模式
                if img.mode != "RGB":
                    img = img.convert("RGB")
                buf = BytesIO()
                img.save(buf, format="PNG")
                character_bytes[char_name] = buf.getvalue()
            logger.info(f"加载角色图片: {char_name}")

    logger.info(f"开始生成 {len(frames)} 个故事板帧")

    # 获取模型
    model = config.get("models.image.model", "")
    image_backend = get_image_backend(provider, model, config.get_all())

    storyboard_dir = project_path / "storyboard"
    storyboard_dir.mkdir(exist_ok=True)

    result = {
        "frames": []
    }

    # 生成每帧的故事板图片
    for frame in frames:
        frame_id = frame.get("frame_id", 0)
        frame_desc = frame.get("description", "")
        camera = frame.get("camera", "")

        # 生成多个变体
        variants = []
        chosen_path = None

        for i in range(num_variants):
            # 构建 variant 文件名
            if num_variants > 1:
                dest_path = storyboard_dir / f"frame_{frame_id:03d}_{i+1}.png"
            else:
                dest_path = storyboard_dir / f"frame_{frame_id:03d}.png"

            # 构建提示词，包含角色信息以保持一致性
            prompt = f"电影镜头，{camera}，{frame_desc}，高清，电影感"
            if character_bytes:
                # 将角色描述加入提示词
                char_descriptions = []
                for char_name, _ in character_images.items():
                    # 从 analyze 结果中获取角色描述
                    for char in analyze_data.get("characters", []):
                        if char.get("name") == char_name:
                            char_descriptions.append(char.get("description", ""))
                if char_descriptions:
                    prompt = f"{'，'.join(char_descriptions)}，{prompt}"

            # 直接生成
            click.echo(f"生成故事板帧 {frame_id}: {frame_desc[:30]}...", nl=False)
            try:
                gen_result = image_backend.text_to_image(prompt)
                if gen_result.local_path:
                    shutil.copy(gen_result.local_path, dest_path)
                    variants.append(str(dest_path))
                    logger.info(f"已保存: {dest_path}")
                    click.echo(f" 已保存: {dest_path.name}")

                    # 第一个变体作为默认选择
                    if i == 0:
                        chosen_path = str(dest_path)
                        result["frames"].append({
                            "frame_id": frame_id,
                            "path": chosen_path,
                            "description": frame_desc
                        })

                        # 上传到云盘
                        cloud_url = upload_to_cloud(
                            dest_path,
                            f"videoclaw/{project}/storyboard/{dest_path.name}",
                            config,
                            project
                        )
                        if cloud_url:
                            click.echo(f" 云盘链接: {cloud_url}")
            except Exception as e:
                logger.error(f"生成失败: {e}")
                click.echo(f" 生成失败: {e}")

        # 记录所有变体到结果中
        if num_variants > 1 and variants:
            # 更新最后一帧的结果为包含所有变体的格式
            if result["frames"]:
                result["frames"][-1] = {
                    "frame_id": frame_id,
                    "chosen": chosen_path,
                    "variants": variants,
                    "description": frame_desc
                }

    state.update_step("storyboard", "completed", result)
    state.set_status("storyboard_rendered")

    logger.info(f"故事板生成完成: {len(frames)} 帧")
    click.echo("\n故事板生成完成!")
