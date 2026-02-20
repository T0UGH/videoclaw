"""i2v 命令"""
from __future__ import annotations

import click
import shutil
from pathlib import Path

from videoclaw.state import StateManager
from videoclaw.config import Config
from videoclaw.models.factory import get_video_backend
from videoclaw.utils.logging import get_logger
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--resolution", "-r", default=None, help="视频分辨率，如 1920x1080, 1280x720")
def i2v(project: str, provider: str, resolution: str):
    """图生视频"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始图生视频，项目: {project}")

    state = StateManager(project_path)
    config = Config(project_path)

    # 检查上一步是否完成
    storyboard_step = state.get_step("storyboard")
    if not storyboard_step or storyboard_step.get("status") != "completed":
        click.echo("错误: 请先完成故事板生成", err=True)
        return

    state.set_status("generating_video")
    state.update_step("i2v", "in_progress")

    # 获取故事板帧
    storyboard_data = storyboard_step.get("output", {})
    frames = storyboard_data.get("frames", [])

    # 获取模型
    model = config.get("models.video.model", "")
    video_backend = get_video_backend(provider, model, config.get_all())

    # 确定分辨率：命令行 > 配置 > 默认
    final_resolution = resolution or config.get("models.video.resolution", "1280x720")
    logger.info(f"使用分辨率: {final_resolution}")

    videos_dir = project_path / "videos"
    videos_dir.mkdir(exist_ok=True)

    result = {
        "videos": []
    }

    # 为每帧生成视频
    for frame in frames:
        frame_id = frame.get("frame_id", 0)
        frame_path = frame.get("path", "")
        frame_desc = frame.get("description", "")

        if not frame_path or not Path(frame_path).exists():
            click.echo(f"警告: 帧 {frame_id} 图片不存在，跳过")
            continue

        click.echo(f"生成视频片段 {frame_id}: {frame_desc[:30]}...", nl=False)

        # 读取图片
        with open(frame_path, "rb") as f:
            image_data = f.read()

        # 调用模型生成视频 (注意: volcengine i2v 不支持 resolution 参数)
        gen_result = video_backend.image_to_video(image_data, frame_desc)

        # 保存到项目目录
        dest_path = videos_dir / f"video_{frame_id:03d}.mp4"
        if gen_result.local_path:
            shutil.copy(gen_result.local_path, dest_path)
            result["videos"].append({
                "frame_id": frame_id,
                "path": str(dest_path),
                "description": frame_desc
            })
            click.echo(f" 已保存: {dest_path.name}")

            # 上传到云盘
            cloud_url = upload_to_cloud(
                dest_path,
                f"videoclaw/{project}/videos/{dest_path.name}",
                config,
                project
            )
            if cloud_url:
                click.echo(f" 云盘链接: {cloud_url}")

    state.update_step("i2v", "completed", result)
    state.set_status("video_generated")

    click.echo("\n视频生成完成!")
