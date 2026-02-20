"""storyboard 命令"""
from __future__ import annotations

import click
import shutil
from pathlib import Path

from videoclaw.state import StateManager
from videoclaw.config import Config
from videoclaw.models.factory import get_image_backend


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, mock")
def storyboard(project: str, provider: str):
    """生成故事板帧图片"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

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

        click.echo(f"生成故事板帧 {frame_id}: {frame_desc[:30]}...", nl=False)

        # 构建提示词
        prompt = f"电影镜头，{camera}，{frame_desc}，高清，电影感"
        gen_result = image_backend.text_to_image(prompt)

        # 保存到项目目录
        dest_path = storyboard_dir / f"frame_{frame_id:03d}.png"
        if gen_result.local_path:
            shutil.copy(gen_result.local_path, dest_path)
            result["frames"].append({
                "frame_id": frame_id,
                "path": str(dest_path),
                "description": frame_desc
            })
            click.echo(f" 已保存: {dest_path.name}")

    state.update_step("storyboard", "completed", result)
    state.set_status("storyboard_rendered")

    click.echo("\n故事板生成完成!")
