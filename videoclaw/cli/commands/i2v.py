"""i2v 命令 - 通用图生视频"""
from __future__ import annotations

import click
import shutil
from pathlib import Path

from videoclaw.config import Config
from videoclaw.models.factory import get_video_backend
from videoclaw.utils.logging import get_logger
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--image", "-i", "images", multiple=True, required=True, help="图片路径，可多次指定")
@click.option("--prompt", "-t", required=True, help="传给视频模型的 prompt")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--resolution", "-r", default=None, help="视频分辨率，如 1920x1080, 1280x720")
def i2v(project: str, images: tuple, prompt: str, provider: str, resolution: str):
    """图生视频（通用模式）"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始图生视频，项目: {project}")

    config = Config(project_path)

    # 获取模型
    model = config.get("models.video.model", "")
    video_backend = get_video_backend(provider, model, config.get_all())

    # 确定分辨率
    final_resolution = resolution or config.get("models.video.resolution", "1280x720")
    logger.info(f"使用分辨率: {final_resolution}")

    videos_dir = project_path / "videos"
    videos_dir.mkdir(exist_ok=True)

    result = {"videos": []}

    # 为每张图片生成视频
    for idx, image_path in enumerate(images):
        image_path = Path(image_path)
        if not image_path.exists():
            click.echo(f"警告: 图片 {image_path} 不存在，跳过")
            continue

        click.echo(f"生成视频片段 {idx + 1}: {prompt[:30]}...", nl=False)

        # 读取图片
        with open(image_path, "rb") as f:
            image_data = f.read()

        # 调用模型生成视频
        gen_result = video_backend.image_to_video(image_data, prompt)

        # 保存到项目目录
        dest_path = videos_dir / f"video_{idx:03d}.mp4"
        if gen_result.local_path:
            shutil.copy(gen_result.local_path, dest_path)
            result["videos"].append({
                "index": idx,
                "path": str(dest_path),
                "prompt": prompt
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

    click.echo("\n视频生成完成!")
