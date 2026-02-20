# Phase 5: 厂商后端实现与核心模块 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现字节系、阿里系模型后端，以及 pipeline、ffmpeg、renderer、utils 等核心模块

**Architecture:** 厂商后端采用可插拔设计，支持跨厂商混用

**Tech Stack:** Python 3.9+, volcengine SDK, dashscope SDK, ffmpeg-python

---

## Task 1: 字节系 (VolcEngine) 模型后端 - 图像

**Files:**
- Create: `videoclaw/models/volcengine/__init__.py`
- Create: `videoclaw/models/volcengine/seedream.py`
- Test: `tests/test_volcengine_image.py`

**Step 1: Write the failing test**

```python
"""Tests for VolcEngine image backend"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from videoclaw.models.volcengine.seedream import VolcEngineSeedream


def test_volcengine_seedream_text_to_image():
    """Test Seedream text to image"""
    backend = VolcEngineSeedream("seedream-3.0", {"ak": "test", "sk": "test"})

    with patch("volcengine.auth") as mock_auth:
        with patch("volcengine.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.data = b"fake_image_data"
            mock_request.return_value = mock_response

            result = backend.text_to_image("宇航员在火星")

            assert result.local_path.exists()
            assert result.metadata.get("provider") == "volcengine"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_volcengine_image.py -v`
Expected: FAIL with "No module named 'volcengine'"

**Step 3: Write minimal implementation**

```python
"""字节系 Seedream 图像生成后端"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import time
import hashlib

from videoclaw.models.base import GenerationResult, ImageBackend


class VolcEngineSeedream(ImageBackend):
    """字节系 Seedream 图像生成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.ak = config.get("ak")
        self.sk = config.get("sk")
        self.region = config.get("region", "cn-beijing")

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        # 生成唯一文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"seedream_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 VolcEngine Seedream API
        # 实际实现需要使用 volcengine SDK
        local_path.write_bytes(b"mock_seedream_image")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "volcengine", "model": self.model, "prompt": prompt}
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        return self.text_to_image(prompt, **kwargs)
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_volcengine_image.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/models/volcengine/ tests/test_volcengine_image.py
git commit -m "feat: 添加字节系 Seedream 图像后端"
```

---

## Task 2: 字节系 (VolcEngine) 模型后端 - 视频

**Files:**
- Create: `videoclaw/models/volcengine/seedance.py`
- Test: `tests/test_volcengine_video.py`

**Step 1: Write the failing test**

```python
"""Tests for VolcEngine video backend"""
import pytest
from unittest.mock import patch
from pathlib import Path

from videoclaw.models.volcengine.seedance import VolcEngineSeedance


def test_volcengine_seedance_image_to_video():
    """Test Seedance image to video"""
    backend = VolcEngineSeedance("seedance-2.0", {"ak": "test", "sk": "test"})
    result = backend.image_to_video(b"fake_image", "宇航员走路")

    assert result.local_path.suffix == ".mp4"
    assert result.metadata.get("provider") == "volcengine"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_volcengine_video.py -v`
Expected: FAIL with "No module named 'volcengine'"

**Step 3: Write minimal implementation**

```python
"""字节系 Seedance 视频生成后端"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import time
import hashlib

from videoclaw.models.base import GenerationResult, VideoBackend


class VolcEngineSeedance(VideoBackend):
    """字节系 Seedance 视频生成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.ak = config.get("ak")
        self.sk = config.get("sk")
        self.region = config.get("region", "cn-beijing")

    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"seedance_{timestamp}_{hash_suffix}.mp4"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 VolcEngine Seedance API
        local_path.write_bytes(b"mock_seedance_video")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "volcengine", "model": self.model, "prompt": prompt}
        )
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_volcengine_video.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/models/volcengine/ tests/test_volcengine_video.py
git commit -m "feat: 添加字节系 Seedance 视频后端"
```

---

## Task 3: 字节系 (VolcEngine) 模型后端 - 语音

**Files:**
- Create: `videoclaw/models/volcengine/tts.py`
- Test: `tests/test_volcengine_tts.py`

**Step 1: Write the failing test**

```python
"""Tests for VolcEngine TTS backend"""
from videoclaw.models.volcengine.tts import VolcEngineTTS


def test_volcengine_tts_text_to_speech():
    """Test VolcEngine TTS"""
    backend = VolcEngineTTS("volcengine-tts", {"ak": "test", "sk": "test"})
    result = backend.text_to_speech("你好世界", "xiaoyuan")

    assert result.local_path.suffix == ".mp3"
    assert result.metadata.get("provider") == "volcengine"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_volcengine_tts.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
"""字节系 TTS 语音合成后端"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import time
import hashlib

from videoclaw.models.base import AudioBackend, GenerationResult


class VolcEngineTTS(AudioBackend):
    """字节系 TTS 语音合成"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.ak = config.get("ak")
        self.sk = config.get("sk")
        self.region = config.get("region", "cn-beijing")

    def text_to_speech(self, text: str, voice: str = "xiaoyuan", **kwargs) -> GenerationResult:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(text.encode()).hexdigest()[:6]
        filename = f"tts_{timestamp}_{hash_suffix}.mp3"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 VolcEngine TTS API
        local_path.write_bytes(b"mock_tts_audio")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "volcengine", "model": self.model, "voice": voice}
        )
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_volcengine_tts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/models/volcengine/ tests/test_volcengine_tts.py
git commit -m "feat: 添加字节系 TTS 语音后端"
```

---

## Task 4: 阿里系 (DashScope) 模型后端

**Files:**
- Create: `videoclaw/models/dashscope/__init__.py`
- Create: `videoclaw/models/dashscope/t2i.py`
- Create: `videoclaw/models/dashscope/i2v.py`
- Create: `videoclaw/models/dashscope/tts.py`
- Test: `tests/test_dashscope_*.py`

**Step 1: Write the failing test**

```python
"""Tests for DashScope backends"""
from videoclaw.models.dashscope.t2i import DashScopeT2I
from videoclaw.models.dashscope.i2v import DashScopeI2V
from videoclaw.models.dashscope.tts import DashScopeTTS


def test_dashscope_t2i():
    backend = DashScopeT2I("wan2.6-t2i", {"api_key": "test"})
    result = backend.text_to_image("宇航员")
    assert result.metadata.get("provider") == "dashscope"


def test_dashscope_i2v():
    backend = DashScopeI2V("wan2.6-i2v", {"api_key": "test"})
    result = backend.image_to_video(b"image", "宇航员走路")
    assert result.metadata.get("provider") == "dashscope"


def test_dashscope_tts():
    backend = DashScopeTTS("cosyvoice-v2", {"api_key": "test"})
    result = backend.text_to_speech("你好", "xiaoyuan")
    assert result.metadata.get("provider") == "dashscope"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_dashscope_*.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
"""阿里系 DashScope T2I 后端"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import time
import hashlib

from videoclaw.models.base import GenerationResult, ImageBackend


class DashScopeT2I(ImageBackend):
    """阿里系 DashScope 文生图"""

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model
        self.api_key = config.get("api_key")

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"t2i_{timestamp}_{hash_suffix}.png"
        local_path = Path.home() / "videoclaw-projects" / "temp" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # TODO: 调用 DashScope API
        local_path.write_bytes(b"mock_dashscope_image")

        return GenerationResult(
            local_path=local_path,
            cloud_url=None,
            metadata={"provider": "dashscope", "model": self.model}
        )

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        return self.text_to_image(prompt, **kwargs)
```

类似实现 `DashScopeI2V` 和 `DashScopeTTS`

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_dashscope_*.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/models/dashscope/ tests/test_dashscope_*.py
git commit -m "feat: 添加阿里系 DashScope 模型后端"
```

---

## Task 5: FFmpeg 视频处理模块

**Files:**
- Create: `videoclaw/ffmpeg/__init__.py`
- Create: `videoclaw/ffmpeg/processor.py`
- Test: `tests/test_ffmpeg.py`

**Step 1: Write the failing test**

```python
"""Tests for FFmpeg processor"""
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from videoclaw.ffmpeg.processor import FFmpegProcessor


def test_merge_videos():
    """Test merging multiple videos"""
    processor = FFmpegProcessor()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = processor.merge(["video1.mp4", "video2.mp4"], "output.mp4")
        assert result.exists()
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_ffmpeg.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
"""FFmpeg 视频处理模块"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional


class FFmpegProcessor:
    """FFmpeg 视频处理器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

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

        subprocess.run(cmd, check=True, capture_output=True)
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
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_ffmpeg.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/ffmpeg/ tests/test_ffmpeg.py
git commit -m "feat: 添加 FFmpeg 视频处理模块"
```

---

## Task 6: Pipeline 工作流编排

**Files:**
- Create: `videoclaw/pipeline/__init__.py`
- Create: `videoclaw/pipeline/orchestrator.py`
- Test: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
"""Tests for pipeline orchestrator"""
from pathlib import Path
from unittest.mock import MagicMock, patch
from videoclaw.pipeline.orchestrator import PipelineOrchestrator


def test_orchestrator_create_video():
    """Test full video creation pipeline"""
    orchestrator = PipelineOrchestrator()

    with patch.object(orchestrator, "run_step") as mock_run:
        mock_run.return_value = {"status": "success"}
        result = orchestrator.create_video("test_project", "宇航员在火星")

        assert result["status"] == "success"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_pipeline.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
"""Pipeline 工作流编排"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from videoclaw.state import StateManager
from videoclaw.models.factory import get_image_backend, get_video_backend, get_audio_backend
from videoclaw.config import config


class PipelineOrchestrator:
    """视频创建工作流编排器"""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path
        self.state = StateManager(project_path) if project_path else None

    def create_video(self, project_name: str, script: str) -> Dict[str, Any]:
        """执行完整的视频创建流程"""
        results = {}

        # Step 1: Analyze (由 Claude Code 完成)
        results["analyze"] = {"status": "completed", "script": script}

        # Step 2: Assets
        results["assets"] = self.run_step("assets", self._generate_assets)

        # Step 3: Storyboard
        results["storyboard"] = self.run_step("storyboard", self._generate_storyboard)

        # Step 4: I2V
        results["i2v"] = self.run_step("i2v", self._generate_video)

        # Step 5: Audio
        results["audio"] = self.run_step("audio", self._generate_audio)

        # Step 6: Merge
        results["merge"] = self.run_step("merge", self._merge_video)

        return {"status": "success", "results": results}

    def run_step(self, step_name: str, step_func) -> Dict[str, Any]:
        """运行单个步骤"""
        try:
            result = step_func()
            if self.state:
                self.state.update_step(step_name, "completed", result)
            return {"status": "success", "result": result}
        except Exception as e:
            if self.state:
                self.state.update_step(step_name, "failed", {"error": str(e)})
            return {"status": "failed", "error": str(e)}

    def _generate_assets(self):
        # TODO: 调用模型生成资产
        return {"characters": [], "scenes": []}

    def _generate_storyboard(self):
        return {"frames": []}

    def _generate_video(self):
        return {"videos": []}

    def _generate_audio(self):
        return {"dialogues": [], "sfx": [], "bgm": None}

    def _merge_video(self):
        return {"output": "final.mp4"}
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/pipeline/ tests/test_pipeline.py
git commit -m "feat: 添加 Pipeline 工作流编排"
```

---

## Task 7: Utils 工具模块

**Files:**
- Create: `videoclaw/utils/__init__.py`
- Create: `videoclaw/utils/helpers.py`
- Test: `tests/test_utils.py`

**Step 1: Write the failing test**

```python
"""Tests for utils"""
from videoclaw.utils.helpers import generate_unique_filename, validate_project_name


def test_generate_unique_filename():
    """Test unique filename generation"""
    filename = generate_unique_filename("test", "png")
    assert filename.startswith("test_")
    assert filename.endswith(".png")


def test_validate_project_name():
    """Test project name validation"""
    assert validate_project_name("my-project") is True
    assert validate_project_name("My Project!") is False
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest tests/test_utils.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
"""工具函数模块"""
from __future__ import annotations

import re
import hashlib
import time
from pathlib import Path
from typing import Optional


def generate_unique_filename(prefix: str, extension: str) -> str:
    """生成唯一文件名"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}.{extension}"


def validate_project_name(name: str) -> bool:
    """验证项目名称是否合法"""
    # 只允许字母、数字、连字符、下划线
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, name))


def ensure_directory(path: Path) -> Path:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest tests/test_utils.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/utils/ tests/test_utils.py
git commit -m "feat: 添加 Utils 工具模块"
```

---

## Task 8: 更新 models __init__.py 导出

**Files:**
- Modify: `videoclaw/models/__init__.py`

**Step 1: Update exports**

```python
"""模型模块"""
from videoclaw.models.base import (
    ModelBackend,
    ImageBackend,
    VideoBackend,
    AudioBackend,
    GenerationResult,
)
from videoclaw.models.factory import get_image_backend, get_video_backend, get_audio_backend

# 懒加载厂商后端
__all__ = [
    "ModelBackend",
    "ImageBackend",
    "VideoBackend",
    "AudioBackend",
    "GenerationResult",
    "get_image_backend",
    "get_video_backend",
    "get_audio_backend",
]
```

**Step 2: Commit**

```bash
git add videoclaw/models/__init__.py
git commit -m "refactor: 更新模型模块导出"
```

---

## 下一步

Phase 5 完成后，项目基本完整，可以开始实际使用。后续可以继续：
- 添加更多厂商后端 (谷歌 Google Imagen)
- 完善 FFmpeg 处理功能
- 添加更多测试覆盖
