# Phase 2: Storage & Model Layer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 实现存储抽象层和模型抽象层，支持多厂商混用

**Architecture:** 存储层和模型层都采用可插拔设计，通过配置文件选择具体实现

**Tech Stack:** Python 3.11+, Click, Pydantic

---

## Task 1: 存储抽象层基类

**Files:**
- Create: `videoclaw/storage/__init__.py`
- Create: `videoclaw/storage/base.py`

**Step 1: 创建存储基类**

```python
"""存储抽象层"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StorageResult:
    """存储结果"""
    local_path: Path
    cloud_url: str | None = None


class StorageBackend(ABC):
    """存储后端基类"""

    @abstractmethod
    def save(self, data: bytes, path: str) -> StorageResult:
        """保存数据，返回本地路径和云端URL"""
        pass

    @abstractmethod
    def load(self, path: str) -> bytes:
        """加载数据"""
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """删除数据"""
        pass

    @abstractmethod
    def get_url(self, path: str) -> str | None:
        """获取访问链接"""
        pass
```

**Step 2: 创建 __init__.py**

```python
"""存储模块"""
from videoclaw.storage.base import StorageBackend, StorageResult

__all__ = ["StorageBackend", "StorageResult"]
```

**Step 3: Commit**

```bash
git add videoclaw/storage/
git commit -m "feat: 添加存储抽象层基类"
```

---

## Task 2: 本地存储实现

**Files:**
- Create: `videoclaw/storage/local.py`

**Step 1: 创建本地存储**

```python
"""本地存储后端"""
from pathlib import Path
from videoclaw.storage.base import StorageBackend, StorageResult


class LocalStorage(StorageBackend):
    """本地文件系统存储"""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path.home() / "videoclaw-projects"

    def save(self, data: bytes, path: str) -> StorageResult:
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)
        return StorageResult(
            local_path=full_path,
            cloud_url=None
        )

    def load(self, path: str) -> bytes:
        full_path = self.base_dir / path
        return full_path.read_bytes()

    def delete(self, path: str) -> None:
        full_path = self.base_dir / path
        if full_path.exists():
            full_path.unlink()

    def get_url(self, path: str) -> str | None:
        # 本地存储没有云端URL
        return None
```

**Step 2: 测试**

```python
# tests/test_storage_local.py
from pathlib import Path
import tempfile
from videoclaw.storage.local import LocalStorage


def test_local_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(Path(tmpdir))
        data = b"hello world"

        result = storage.save(data, "test/file.txt")
        assert result.local_path.exists()
        assert result.cloud_url is None

        loaded = storage.load("test/file.txt")
        assert loaded == data

        storage.delete("test/file.txt")
        assert not result.local_path.exists()
```

**Step 3: Commit**

```bash
git add videoclaw/storage/
git commit -m "feat: 添加本地存储实现"
```

---

## Task 3: 模型抽象层基类

**Files:**
- Create: `videoclaw/models/__init__.py`
- Create: `videoclaw/models/base.py`

**Step 1: 创建模型基类**

```python
"""模型抽象层"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GenerationResult:
    """生成结果"""
    local_path: Path
    cloud_url: str | None = None
    metadata: dict


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
```

**Step 2: 创建 __init__.py**

```python
"""模型模块"""
from videoclaw.models.base import (
    ModelBackend,
    ImageBackend,
    VideoBackend,
    AudioBackend,
    GenerationResult,
)

__all__ = [
    "ModelBackend",
    "ImageBackend",
    "VideoBackend",
    "AudioBackend",
    "GenerationResult",
]
```

**Step 3: Commit**

```bash
git add videoclaw/models/
git commit -m "feat: 添加模型抽象层基类"
```

---

## Task 4: 模型工厂（支持多厂商）

**Files:**
- Create: `videoclaw/models/factory.py`

**Step 1: 创建模型工厂**

```python
"""模型工厂"""
from videoclaw.models.base import ImageBackend, VideoBackend, AudioBackend
from videoclaw.models.factory import get_image_backend, get_video_backend, get_audio_backend


def get_image_backend(provider: str, model: str, config: dict) -> ImageBackend:
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


def get_video_backend(provider: str, model: str, config: dict) -> VideoBackend:
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


def get_audio_backend(provider: str, model: str, config: dict) -> AudioBackend:
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
```

**Step 2: Commit**

```bash
git add videoclaw/models/
git commit -m "feat: 添加模型工厂"
```

---

## Task 5: Mock 后端（用于测试）

**Files:**
- Create: `videoclaw/models/mock/__init__.py`
- Create: `videoclaw/models/mock/image.py`
- Create: `videoclaw/models/mock/video.py`
- Create: `videoclaw/models/mock/audio.py`

**Step 1: 创建 Mock 图像后端**

```python
"""Mock 图像后端"""
import io
from pathlib import Path
from PIL import Image
from videoclaw.models.base import ImageBackend, GenerationResult


class MockImageBackend(ImageBackend):
    """用于测试的 Mock 图像后端"""

    def __init__(self, model: str, config: dict):
        self.model = model
        self.config = config

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        # 创建一个简单的测试图片
        img = Image.new("RGB", (1024, 576), color=(100, 150, 200))
        path = Path(f"/tmp/mock_image_{hash(prompt)}.png")
        img.save(path)
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"width": 1024, "height": 576, "format": "png"}
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        return self.text_to_image(prompt, **kwargs)
```

**Step 2: 创建 Mock 视频后端**

```python
"""Mock 视频后端"""
from pathlib import Path
from videoclaw.models.base import VideoBackend, GenerationResult


class MockVideoBackend(VideoBackend):
    """用于测试的 Mock 视频后端"""

    def __init__(self, model: str, config: dict):
        self.model = model
        self.config = config

    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        # 创建一个空的测试视频文件
        path = Path(f"/tmp/mock_video_{hash(prompt)}.mp4")
        path.write_bytes(b"mock video")
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"duration": 5, "format": "mp4"}
        )
```

**Step 3: 创建 Mock 音频后端**

```python
"""Mock 音频后端"""
from pathlib import Path
from videoclaw.models.base import AudioBackend, GenerationResult


class MockAudioBackend(AudioBackend):
    """用于测试的 Mock 音频后端"""

    def __init__(self, model: str, config: dict):
        self.model = model
        self.config = config

    def text_to_speech(self, text: str, voice: str, **kwargs) -> GenerationResult:
        path = Path(f"/tmp/mock_audio_{hash(text)}.mp3")
        path.write_bytes(b"mock audio")
        return GenerationResult(
            local_path=path,
            cloud_url=None,
            metadata={"duration": 3, "format": "mp3", "voice": voice}
        )
```

**Step 4: Commit**

```bash
git add videoclaw/models/mock/
git commit -m "feat: 添加 Mock 后端用于测试"
```

---

## 下一步

Phase 2 完成后，继续 Phase 3 实现具体的厂商后端（DashScope、VolcEngine 等）。
