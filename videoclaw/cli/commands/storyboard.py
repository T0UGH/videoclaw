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


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


def ask_confirm(prompt: str) -> str:
    """Ask user for confirmation, return 'y' (yes), 'n' (no), 'r' (retry/adjust)"""
    while True:
        answer = input(f"{prompt} (y/n/r): ").strip().lower()
        if answer in ['y', 'n', 'r']:
            return answer
        click.echo("请输入 y (是), n (否), 或 r (调整)")


def generate_frame_with_confirm(image_backend, prompt: str, dest_path: Path, frame_id: int, logger) -> tuple[bool, str]:
    """
    Generate a frame and ask for confirmation.
    Returns: (confirmed: bool, final_prompt: str)
    """
    while True:
        click.echo(f"生成中: 帧 {frame_id}...")

        try:
            gen_result = image_backend.text_to_image(prompt)

            if gen_result.local_path:
                shutil.copy(gen_result.local_path, dest_path)
        except Exception as e:
            logger.error(f"生成失败: {e}")
            click.echo(f"生成失败: {e}")

        # Show result and ask
        click.echo(f"生成完成: {dest_path}")
        click.echo(f"提示词: {prompt}")

        answer = ask_confirm("这帧可以吗？")

        if answer == 'y':
            return True, prompt
        elif answer == 'n':
            return False, prompt
        else:
            new_prompt = input("请输入调整后的提示词: ").strip()
            if new_prompt:
                prompt = new_prompt


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, mock")
@click.option("--yes", "-y", is_flag=True, help="跳过确认，直接使用生成的图片")
def storyboard(project: str, provider: str, yes: bool):
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

        if yes:
            # 自动模式：直接生成，不确认
            click.echo(f"生成故事板帧 {frame_id}: {frame_desc[:30]}...", nl=False)
            try:
                gen_result = image_backend.text_to_image(prompt)
                if gen_result.local_path:
                    shutil.copy(gen_result.local_path, dest_path)
                    result["frames"].append({
                        "frame_id": frame_id,
                        "path": str(dest_path),
                        "description": frame_desc
                    })
                    click.echo(f" 已保存: {dest_path.name}")
            except Exception as e:
                logger.error(f"生成失败: {e}")
                click.echo(f" 生成失败: {e}")
        else:
            # 交互模式：生成后确认
            click.echo(f"生成故事板帧 {frame_id}: {frame_desc[:30]}...")
            confirmed, final_prompt = generate_frame_with_confirm(
                image_backend, prompt, dest_path, frame_id, logger
            )
            if confirmed:
                result["frames"].append({
                    "frame_id": frame_id,
                    "path": str(dest_path),
                    "description": frame_desc
                })
            else:
                click.echo(f"跳过帧: {frame_id}")

    state.update_step("storyboard", "completed", result)
    state.set_status("storyboard_rendered")

    logger.info(f"故事板生成完成: {len(frames)} 帧")
    click.echo("\n故事板生成完成!")
