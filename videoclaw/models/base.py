"""模型抽象层"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class GenerationResult:
    """生成结果"""
    local_path: Path
    cloud_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ModelBackend(ABC):
    """模型后端基类"""
    pass


class ImageBackend(ModelBackend):
    """图像生成后端"""

    @abstractmethod
    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        """文生图"""
        pass

    @abstractmethod
    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        """图生图"""
        pass


class VideoBackend(ModelBackend):
    """视频生成后端"""

    @abstractmethod
    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        """图生视频"""
        pass


class AudioBackend(ModelBackend):
    """音频生成后端"""

    @abstractmethod
    def text_to_speech(self, text: str, voice: str, **kwargs) -> GenerationResult:
        """文本转语音"""
        pass
