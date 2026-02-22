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
@click.option("--image", "-i", "images", multiple=True, default=None, help="图片路径，可多次指定")
@click.option("--prompt", "-t", required=True, help="传给视频模型的 prompt")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--resolution", "-r", default=None, help="视频分辨率，如 1920x1080, 1280x720")
@click.option("--video-ref", "-v", "video_refs", multiple=True, default=None, help="视频参考路径（运镜/动作）")
@click.option("--audio-ref", "-a", "audio_refs", multiple=True, default=None, help="音频参考路径（配乐/对白）")
def i2v(project: str, images: tuple, prompt: str, provider: str, resolution: str, video_refs: tuple, audio_refs: tuple):
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

    # 验证输入：至少需要图片、视频参考或音频参考之一
    if not images and not video_refs and not audio_refs:
        click.echo("错误: 必须提供至少一种输入（--image, --video-ref 或 --audio-ref）", err=True)
        return

    # 验证图片路径存在
    valid_images = []
    if images:
        for img_path in images:
            img_path = Path(img_path)
            if img_path.exists():
                valid_images.append(img_path)
            else:
                click.echo(f"警告: 图片 {img_path} 不存在，跳过")

    # 验证视频参考路径存在
    valid_video_refs = []
    if video_refs:
        for vid_path in video_refs:
            vid_path = Path(vid_path)
            if vid_path.exists():
                valid_video_refs.append(vid_path)
            else:
                click.echo(f"警告: 视频参考 {vid_path} 不存在，跳过")

    # 验证音频参考路径存在
    valid_audio_refs = []
    if audio_refs:
        for aud_path in audio_refs:
            aud_path = Path(aud_path)
            if aud_path.exists():
                valid_audio_refs.append(aud_path)
            else:
                click.echo(f"警告: 音频参考 {aud_path} 不存在，跳过")

    # 如果只有单张图片且无参考文件，使用原有逻辑（单图生成）
    if len(valid_images) == 1 and not valid_video_refs and not valid_audio_refs:
        # 为每张图片生成视频（原有逻辑）
        for idx, image_path in enumerate(valid_images):
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
    else:
        # 多图或多模态输入：收集所有输入，一次调用
        click.echo(f"多模态输入: {len(valid_images)} 图片, {len(valid_video_refs)} 视频参考, {len(valid_audio_refs)} 音频参考")

        # 读取所有图片数据
        image_data_list = []
        for image_path in valid_images:
            with open(image_path, "rb") as f:
                image_data_list.append(f.read())

        # 转换为字节列表或单字节
        images_input = image_data_list if len(image_data_list) > 1 else (image_data_list[0] if image_data_list else None)

        # 传递参考文件路径列表
        video_refs_input = [str(p) for p in valid_video_refs] if valid_video_refs else None
        audio_refs_input = [str(p) for p in valid_audio_refs] if valid_audio_refs else None

        # 调用模型生成视频
        click.echo(f"生成视频: {prompt[:30]}...", nl=False)
        gen_result = video_backend.image_to_video(
            images_input,
            prompt,
            video_refs=video_refs_input,
            audio_refs=audio_refs_input,
        )

        # 保存到项目目录
        if gen_result.local_path:
            dest_path = videos_dir / f"video_multi_001.mp4"
            shutil.copy(gen_result.local_path, dest_path)
            result["videos"].append({
                "index": 0,
                "path": str(dest_path),
                "prompt": prompt,
                "multi_modal": True
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
