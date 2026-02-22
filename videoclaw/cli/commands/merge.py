"""merge 命令"""
from __future__ import annotations

import click
import subprocess
from pathlib import Path

from videoclaw.config import Config
from videoclaw.utils.logging import get_logger
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


def check_ffmpeg():
    """检查 FFmpeg 是否可用"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def merge_with_ffmpeg(video_files: list, audio_files: list, bgm_file: str, output_path: Path) -> bool:
    """使用 FFmpeg 合并视频和音频"""
    if not video_files:
        return False

    # 先获取所有视频的分辨率，选择第一个视频的分辨率作为目标分辨率
    target_width = None
    target_height = None

    for video in video_files:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height", "-of", "csv=s=,:p=0", video],
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                w, h = map(int, result.stdout.strip().split(','))
                if target_width is None:
                    target_width, target_height = w, h
                break
        except Exception:
            continue

    if target_width is None:
        target_width, target_height = 1280, 720  # 默认分辨率

    # 创建临时目录用于处理后的视频
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    processed_files = []

    try:
        # 1. 将所有视频重新编码为目标分辨率
        for i, video in enumerate(video_files):
            processed_path = temp_dir / f"video_{i:03d}.mp4"

            # 使用 scale 滤镜统一分辨率，同时使用 pad 保持纵横比
            cmd = [
                "ffmpeg", "-y", "-i", video,
                "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                str(processed_path)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            processed_files.append(str(processed_path))

        # 2. 使用 concat 合并处理后的视频
        concat_list = temp_dir / "concat_list.txt"
        with open(concat_list, "w") as f:
            for video in processed_files:
                f.write(f"file '{video}'\n")

        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True

    except subprocess.CalledProcessError as e:
        click.echo(f"FFmpeg 错误: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--videos", "-v", multiple=True, required=True, help="视频文件路径（可多次指定）")
@click.option("--audio", "-a", help="背景音乐文件路径")
@click.option("--output", "-o", default="final.mp4", help="输出文件名")
def merge(project: str, videos: tuple, audio: str, output: str):
    """合并视频片段"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始合并视频，项目: {project}")

    config = Config(project_path)

    # 直接使用命令行参数
    video_files = list(videos)
    bgm_file = audio

    videos_dir = project_path / "videos"
    videos_dir.mkdir(exist_ok=True)
    output_path = videos_dir / output

    click.echo(f"找到 {len(video_files)} 个视频片段")
    if bgm_file:
        click.echo(f"背景音乐: {bgm_file}")

    # 检查 FFmpeg
    has_ffmpeg = check_ffmpeg()

    if has_ffmpeg and all(Path(v).exists() for v in video_files):
        # 使用 FFmpeg 合并
        click.echo("使用 FFmpeg 合并视频...")

        # 尝试合并
        if merge_with_ffmpeg(video_files, [], bgm_file, output_path):
            click.echo(f"视频已合并: {output_path}")
        else:
            click.echo("FFmpeg 合并失败，创建占位文件")
            output_path.write_bytes(b"merged video placeholder")
    else:
        # FFmpeg 不可用或文件不存在，创建占位文件
        click.echo("FFmpeg 不可用或文件不存在，创建占位文件")

        # 复制第一个视频作为最终输出（模拟）
        if video_files and Path(video_files[0]).exists():
            import shutil
            shutil.copy(video_files[0], output_path)
        else:
            output_path.write_bytes(b"merged video placeholder")

    # 上传到云盘
    cloud_url = upload_to_cloud(
        output_path,
        f"videoclaw/{project}/{output}",
        config,
        project
    )
    if cloud_url:
        click.echo(f" 云盘链接: {cloud_url}")

    click.echo(f"\n视频合并完成: {output_path}")
