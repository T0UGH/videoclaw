# Videoclaw Design - AI 视频创作工具

## 1. 项目概述

**项目名称**: videoclaw

**项目定位**: 一个给 Claude Code 用的 AI 视频创作 CLI 工具。人类通过 Happy + Claude Code 对话，Claude Code 调用 videoclaw CLI 执行实际任务。

**核心理念**: "极客风格" - AI 原生工具链，Claude Code 通过 Skills 调用 CLI 完成工作流。

**技术栈**: Python 3.11+, uv (包管理), Click (CLI), Pydantic, PyYAML

---

## 2. 整体架构

```
┌────────────────────────────────────────┐
│  人类 ←→ Happy ←→ Claude Code          │
│              │                         │
│              ├── Skills (提示词/工作流)  │
│              └── Subagents (任务编排)   │
└────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│  videoclaw CLI (Python)               │
│  - 命令行工具                          │
│  - 存储抽象层                         │
│  - AI 模型调用                        │
│  - 视频处理                           │
└────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│  外部服务                              │
│  - DashScope (LLM/图像/视频/TTS)       │
│  - 云存储 (用户可选 OSS/S3/MinIO)      │
└────────────────────────────────────────┘
```

**部署方式**
- Claude Code 和 CLI 都在同一台机器上
- 同机部署，不需要管理服务进程

---

## 3. Skills 设计

### 技能体系

```
videoclaw/
└── skills/
    ├── video:init          # 初始化项目
    ├── video:create       # 创建视频（主工作流）
    ├── video:analyze      # 脚本分析
    ├── video:assets       # 资产生成
    ├── video:storyboard  # 故事板渲染
    ├── video:i2v          # 图生视频
    ├── video:audio        # 音频生成
    ├── video:merge        # 视频合并
    ├── video:preview      # 预览图片/视频
    ├── video:status       # 查看进度
    └── video:config       # 配置管理
```

### 技能职责

| Skill | 职责 |
|-------|------|
| `video:init` | 初始化项目目录，生成配置文件 |
| `video:create` | 编排完整视频创建流程（一句话创建） |
| `video:analyze` | 调用 LLM 分析脚本，提取角色/场景/帧 |
| `video:assets` | 生成角色和场景图片 |
| `video:storyboard` | 生成故事板帧图片 |
| `video:i2v` | 图生视频 |
| `video:audio` | TTS/音效/背景音乐 |
| `video:merge` | 合并视频片段 |
| `video:preview` | 预览图片/视频 |
| `video:status` | 查看项目进度和状态 |
| `video:config` | 配置 AI 模型、云存储等 |

### 使用模式

#### 模式 1: 一句话创建（推荐新手）
用户只需要说：
> "帮我做一个关于宇航员在火星上发现外星遗迹的短视频"

然后 Claude Code 自动完成所有步骤。

#### 模式 2: 逐步控制（高级用户）
用户可以分步控制：
> "先帮我分析这个脚本"
> "生成角色图片"
> "第3帧用另外一个动作重新生成视频"
> "调整第2段的配音"

### 子技能调用关系

```
video:create (主技能)
    │
    ├── 内部调用 CLI → video:analyze
    ├── 内部调用 CLI → video:assets
    ├── 内部调用 CLI → video:storyboard
    ├── 内部调用 CLI → video:i2v
    ├── 内部调用 CLI → video:audio
    └── 内部调用 CLI → video:merge
```

用户也可以直接调用子技能进行细粒度控制。

---

## 4. 状态管理

### 项目结构

```
~/videoclaw-projects/              # 用户目录，统一管理所有项目
└── my-video-project/
    ├── .videoclaw/              # 工作目录
    │   ├── config.yaml          # 项目配置
    │   ├── state.json           # 状态跟踪
    │   └── logs/                # 日志
    ├── script.txt               # 原始脚本
    ├── assets/                  # 角色/场景图片
    ├── storyboard/              # 故事板帧图片
    ├── videos/                  # 生成的视频片段
    └── audio/                   # 音频文件
```

### state.json 示例

```json
{
  "project_id": "abc123",
  "status": "rendering_storyboard",
  "steps": {
    "analyzed": { "status": "completed", "output": {...} },
    "assets": { "status": "completed", "output": {...} },
    "storyboard": { "status": "in_progress", "current_frame": 3, "total_frames": 10 },
    "i2v": { "status": "pending" },
    "audio": { "status": "pending" },
    "merge": { "status": "pending" }
  },
  "resume_token": "step_3_frame_5"
}
```

### 关键特性

1. **可恢复** - 中断后可以从上一步继续
2. **幂等** - 重复执行不会产生副作用
3. **进度追踪** - 每步状态实时更新

### 产物命名

产物文件使用时间戳 + 随机数命名：

```
assets/
├── character_20260218_143052_a1b2c3.png
├── scene_20260218_143052_d4e5f6.png
storyboard/
├── frame_001_20260218_143052_g7h8i9.png
videos/
├── frame_001_20260218_143052_j0k1l2.mp4
audio/
├── dialogue_001_20260218_143052_m3n4o5.mp3
```

### 错误处理

- **自动重试** - 失败自动重试 2 次
- **交还控制** - 重试失败后，将控制权交还给用户
- **状态记录** - 失败状态会记录在 state.json 中

### 并发控制

- **无锁设计** - 依赖 state.json 的状态判断
- 同一项目同时只能运行一个任务
- 通过状态判断防止并发：检查当前步骤状态是否为 `in_progress`

---

## 5. 配置管理

### 配置文件优先级

1. **环境变量** - 最高优先级
2. **全局配置** - `~/.videoclaw/config.yaml`
3. **项目配置** - `./.videoclaw/config.yaml`

### 环境变量命名

```bash
# DashScope (仅用于图像/视频/音频生成)
DASHSCOPE_API_KEY=xxx

# 存储
VIDEOCLAW_STORAGE_TYPE=oss
VIDEOCLAW_OSS_ACCESS_KEY=xxx
VIDEOCLAW_OSS_SECRET_KEY=xxx

# 其他
VIDEOCLAW_LOG_LEVEL=info
```

### 系统依赖检测

- 启动时自动检测 FFmpeg 等系统依赖
- 如未安装，提示用户是否自动安装
- 用户确认后自动安装

---

## 6. 存储抽象层

### 存储策略

- **本地存储** - 必选，所有产物都会在本地保存一份
- **云存储** - 可选，根据用户配置决定是否同步到云盘
- **同步策略** - 实时双写，同时写入本地和云端

### 配置示例

```yaml
storage:
  local:
    enabled: true

  cloud:
    enabled: true  # 是否启用云存储
    type: oss  # oss, s3, minio
    config:
      access_key: xxx
      secret_key: xxx
      bucket: xxx
      endpoint: xxx
```

### 预览功能

根据存储类型不同，预览方式不同：

- **有云存储**：生成云盘临时访问链接
  - 图片：`oss://bucket/path.jpg` → `https://bucket.oss.com/path.jpg?签名`
- **仅本地存储**：返回本地文件路径，Claude Code 使用 `open` 命令打开

### 存储后端实现

```
videoclaw/storage/
├── base.py           # StorageBackend 基类
├── local.py          # 本地存储
├── oss.py            # 阿里云 OSS
├── s3.py             # AWS S3
└── minio.py          # MinIO
```

---

## 7. AI 模型抽象层

### 模型后端设计（可插拔）

```
videoclaw/models/
├── base.py           # ModelBackend 基类
├── dashscope/       # 阿里云 DashScope
│   ├── t2i.py       # wan2.6-t2i 文生图
│   ├── i2v.py       # wan2.6-i2v 图生视频
│   └── tts.py       # cosyvoice-v2 语音合成
├── volcengine/      # 字节系 火山引擎
│   ├── seedream.py  # seedream 图像生成
│   ├── seedance.py  # seedance 视频生成
│   └── tts.py       # volcengine 语音合成
├── openai/         # OpenAI (可选)
└── mock/            # 测试用 Mock
```

> 第一期优先支持：阿里系 (DashScope) + 字节系 (火山引擎)

> 注意：脚本分析由 Claude Code 直接完成，无需额外配置 LLM 后端。

### 基类定义

```python
class ModelBackend(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> bytes:
        pass

class ImageBackend(ModelBackend):
    @abstractmethod
    def text_to_image(self, prompt: str, **kwargs) -> ImageResult:
        pass

    @abstractmethod
    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> ImageResult:
        pass

class VideoBackend(ModelBackend):
    @abstractmethod
    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> VideoResult:
        pass

class AudioBackend(ModelBackend):
    @abstractmethod
    def text_to_speech(self, text: str, voice: str, **kwargs) -> bytes:
        pass
```

### 模型返回格式

模型调用后直接存文件，返回路径和元数据：

```python
@dataclass
class GenerationResult:
    local_path: Path           # 本地文件路径
    cloud_url: str | None     # 云盘访问链接（如果配置了云存储）
    metadata: dict             # 元数据（尺寸、时长、格式等）

# 示例
result = model.text_to_image(prompt="宇航员")
# result.local_path = ~/videoclaw-projects/my-project/assets/character_20260218_143052_a1b2c3.png
# result.cloud_url = https://bucket.oss.com/... (如果配置了云存储)
# result.metadata = {"width": 1024, "height": 576, "format": "png"}
```

### 用户扩展模型后端

用户可以通过两种方式扩展：

#### 方式 1：内置后端
在 `videoclaw/models/` 目录下添加新后端：

```python
# videoclaw/models/seedance.py
from videoclaw.models.base import VideoBackend

class SeedanceVideoBackend(VideoBackend):
    def image_to_video(self, image: bytes, prompt: str, **kwargs) -> VideoResult:
        # 实现 Seedance API 调用
        pass
```

配置使用：
```yaml
models:
  video:
    provider: seedance
    model: seedance-2.0
```

#### 方式 2：外部插件（动态加载）
用户可以在项目中创建 `models/` 目录，videoclaw 会自动加载：

```
my-project/
├── .videoclaw/
├── models/              # 用户自定义模型
│   ├── __init__.py
│   └── my_video.py
└── ...
```

实现方式（Python 动态 import）：

```python
import importlib.util
import sys
from pathlib import Path

def load_external_models(project_path: Path):
    models_dir = project_path / "models"
    if not models_dir.exists():
        return

    for file in models_dir.glob("*.py"):
        if file.stem.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[file.stem] = module
        spec.loader.exec_module(module)
```

#### 方式 3：Entry Points（更规范）
通过 `pyproject.toml` 注册插件：

```toml
[project.entry-points."videoclaw.models"]
my_video = "my_package:MyVideoBackend"
```

### 配置示例

#### 阿里系 (DashScope)

```yaml
models:
  image:
    provider: dashscope
    model: wan2.6-t2i

  video:
    provider: dashscope
    model: wan2.6-i2v

  audio:
    provider: dashscope
    model: cosyvoice-v2
```

#### 字节系 (火山引擎)

```yaml
models:
  image:
    provider: volcengine
    model: seedream

  video:
    provider: volcengine
    model: seedance
```

### 环境变量

```bash
# 阿里系
DASHSCOPE_API_KEY=xxx

# 字节系
VOLCENGINE_AK=xxx
VOLCENGINE_SK=xxx
```

---

## 8. CLI 架构

### 模块设计

```
videoclaw-cli/
├── cli/                    # 命令行入口
│   ├── __main__.py
│   └── commands/
│       ├── init.py
│       ├── analyze.py
│       ├── assets.py
│       ├── storyboard.py
│       ├── i2v.py
│       ├── audio.py
│       ├── merge.py
│       ├── preview.py
│       └── config.py
├── pipeline/               # 工作流编排
│   ├── __init__.py
│   └── orchestrator.py
├── models/                # AI 模型调用（可插拔）
├── storage/              # 存储抽象层（可插拔）
├── renderer/             # 图片/视频渲染
├── audio/                # TTS/音频合成
├── ffmpeg/               # 视频处理
└── utils/                # 工具函数
```

---

## 9. 视频创建流程

参照 LumenX 的 7 步流程：

```
文本输入 → 脚本分析 → 资产生成 → 故事板生成 → 视频生成 → 音频生成 → 视频合成
```

### Step 1: 脚本分析
- 由 Claude Code 直接完成（Claude Code 本身就是 LLM）
- 提取：角色、场景、道具、故事板帧
- 无需额外配置 LLM 后端

### Step 2: 资产生成
- 使用 T2I 模型生成角色头像、全身照、三视图
- 生成场景背景图

### Step 3: 故事板生成
- 使用 T2I/I2I 模型生成帧图片

### Step 4: 图生视频
- 使用 I2V 模型生成视频片段

### Step 5: 音频生成
- TTS 语音合成
- SFX 音效
- BGM 背景音乐

### Step 6: 视频选择
- 为每帧选择特定的视频变体

### Step 7: 视频合并
- 使用 FFmpeg 合并视频片段

---

## 10. 外部依赖

### AI 服务

> 注意：脚本分析由 Claude Code 直接完成，无需额外配置 LLM。

#### 阿里系 (DashScope)

| 服务 | 模型 | API | 认证方式 |
|------|------|-----|----------|
| 图像生成 | wan2.6-t2i, wan2.5-i2i | dashscope.aliyuncs.com | API Key |
| 视频生成 | wan2.6-i2v | dashscope.aliyuncs.com | API Key |
| 语音合成 | cosyvoice-v2 | dashscope.aliyuncs.com | API Key |

#### 字节系 (火山引擎)

| 服务 | 模型 | API | 认证方式 |
|------|------|-----|----------|
| 图像生成 | seedream | ark.cn-beijing.volces.com/api/v3/visual/seedream | AK/SK 签名 |
| 视频生成 | seedance | ark.cn-beijing.volces.com/api/v3/seedance | AK/SK 签名 |
| 语音合成 | volcengine-tts | volcengine.com/docs/67009 | AK/SK 签名 |

### SDK 依赖

| 厂商 | SDK | 复杂度 |
|------|-----|--------|
| 阿里 DashScope | `pip install dashscope` | 低 |
| 字节 火山引擎 | `pip install volcengine` | 中 |

### 视频处理
- FFmpeg

---

## 11. Skills 位置

Skills 放在项目内的 `skills/` 目录，通过 CLI 工具打包安装：

```
videoclaw/
├── skills/
│   ├── video-init.md
│   ├── video-create.md
│   ├── video-analyze.md
│   └── ...
└── cli/
```

用户可以通过 `videoclaw skills install` 安装到 Claude Code 的 skills 目录。

---

## 12. 待定事项

- [ ] 测试策略
- [ ] 项目清理策略（如何删除旧项目）
