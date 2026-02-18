"""模型工厂"""
from __future__ import annotations

from typing import Any, Dict

from videoclaw.models.base import ImageBackend, VideoBackend, AudioBackend


def get_image_backend(provider: str, model: str, config: Dict[str, Any]) -> ImageBackend:
    """获取图像生成后端"""
    if provider == "dashscope":
        from videoclaw.models.dashscope.t2i import DashScopeT2I
        return DashScopeT2I(model, config)
    elif provider == "volcengine":
        from videoclaw.models.volcengine.seedream import VolcEngineSeedream
        return VolcEngineSeedream(model, config)
    elif provider == "google":
        from videoclaw.models.google.imagen import GoogleImagen
        return GoogleImagen(model, config)
    elif provider == "mock":
        from videoclaw.models.mock.image import MockImageBackend
        return MockImageBackend(model, config)
    else:
        raise ValueError(f"Unknown image provider: {provider}")


def get_video_backend(provider: str, model: str, config: Dict[str, Any]) -> VideoBackend:
    """获取视频生成后端"""
    if provider == "dashscope":
        from videoclaw.models.dashscope.i2v import DashScopeI2V
        return DashScopeI2V(model, config)
    elif provider == "volcengine":
        from videoclaw.models.volcengine.seedance import VolcEngineSeedance
        return VolcEngineSeedance(model, config)
    elif provider == "mock":
        from videoclaw.models.mock.video import MockVideoBackend
        return MockVideoBackend(model, config)
    else:
        raise ValueError(f"Unknown video provider: {provider}")


def get_audio_backend(provider: str, model: str, config: Dict[str, Any]) -> AudioBackend:
    """获取音频生成后端"""
    if provider == "dashscope":
        from videoclaw.models.dashscope.tts import DashScopeTTS
        return DashScopeTTS(model, config)
    elif provider == "volcengine":
        from videoclaw.models.volcengine.tts import VolcEngineTTS
        return VolcEngineTTS(model, config)
    elif provider == "mock":
        from videoclaw.models.mock.audio import MockAudioBackend
        return MockAudioBackend(model, config)
    else:
        raise ValueError(f"Unknown audio provider: {provider}")
