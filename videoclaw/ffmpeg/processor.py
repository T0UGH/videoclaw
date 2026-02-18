"""FFmpeg 视频处理模块"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional


class FFmpegError(Exception):
    """FFmpeg 处理错误"""
    pass


class FFmpegProcessor:
    """FFmpeg 视频处理器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def _run_command(self, cmd: List[str]) -> None:
        """执行 FFmpeg 命令"""
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise FFmpegError(f"FFmpeg 执行失败: {e.stderr}")

    def merge(self, input_files: List[str], output_file: str) -> Path:
        """合并多个视频文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建临时文件列表
        list_file = output_path.parent / "input_list.txt"
        with open(list_file, "w") as f:
            for file in input_files:
                f.write(f"file '{file}'\n")

        # 使用 FFmpeg concat 合并
        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            "-y",
            str(output_path)
        ]

        self._run_command(cmd)
        list_file.unlink()

        return output_path

    def add_audio(self, video_file: str, audio_file: str, output_file: str) -> Path:
        """为视频添加音频"""
        output_path = Path(output_file)
        cmd = [
            self.ffmpeg_path,
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-y",
            str(output_path)
        ]
        self._run_command(cmd)
        return output_path
