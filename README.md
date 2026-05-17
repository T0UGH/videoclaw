# videoclaw

[English](README_en.md) | **AI 视频创作 CLI 工具 | 宿主中立 Skill Pack + CLI**

## 概述

videoclaw 是 AI 视频创作 CLI 工具，目标是把视频创作拆成：

- **CLI 执行层**：负责项目结构、模型调用、产物归档；
- **Skill Pack 工作流层**：负责交互、模板和创作流程；
- **Host Adapter 适配层**：负责把同一套 skill pack 接到不同宿主。

当前推荐组合仍然是：图像优先 Gemini，视频优先 Seedance 2.0；但 videoclaw 的长期方向不再是“只给 Claude Code 用”，而是让同一套 CLI + skills 可以被多个宿主复用。

## 安装 CLI

### 方式一：uvx（推荐，无需安装）

```bash
uvx videoclaw --help
```

### 方式二：pip（全局安装）

```bash
pip install videoclaw
```

### 方式三：开发模式

```bash
git clone https://github.com/T0UGH/videoclaw.git
cd videoclaw
pip install -e .
```

### 可选环境变量

```bash
export ARK_API_KEY=your-ark-api-key
export DASHSCOPE_API_KEY=your-api-key
export GOOGLE_API_KEY=your-api-key
export OPENAI_API_KEY=your-api-key
```

## 安装 Skill Pack / Host Adapter

videoclaw 的分发现在分成两层：

1. **CLI**：标准 Python 包（`uvx` / `pip`）
2. **Skill Pack / Host Adapter**：按宿主选择安装方式

### Claude Code Adapter

Claude Code 目前仍可通过 marketplace 安装适配层：

```bash
/claude install marketplace https://github.com/T0UGH/videoclaw/raw/main/.claude-plugin/marketplace.json
```

这个 marketplace 入口现在应理解为 **Claude Code adapter**，而不是 videoclaw 的唯一分发中心。

### 其他宿主

长期方向是让 `skills/` 成为 canonical skill pack，再为不同宿主提供薄 adapter：

- Claude Code adapter
- OpenClaw adapter（优先目标）
- Hermes adapter（先走目录式接入）
- Codex runtime / host capability adapter

## 快速开始

```bash
# 初始化一个 project
videoclaw init my-project

# 在 project 下创建一个视频单元
videoclaw video create my-project demo-video

# 查看视频列表
videoclaw video list my-project
```

### 新的 Project / Video 模型

videoclaw 现在采用：

- 一个 `project` 承载共享资产与多个视频；
- 一个 `video` 是独立产出单元；
- 单段视频默认使用 `render/` 管理生成过程；
- 多段视频后续可扩展到 `clips/`。

推荐目录结构：

```text
my-project/
├── .videoclaw/
│   ├── config.yaml
│   ├── index.json
│   └── logs/
├── assets/
│   ├── characters/
│   ├── scenes/
│   ├── props/
│   └── covers/
├── videos/
│   └── demo-video/
│       ├── meta.json
│       ├── brief.md
│       ├── storyboard/
│       ├── images/
│       ├── clips/
│       └── audio/
└── exports/
```

## 图片 Backend

图片能力正在升级为双轨模型：

- `openai-image`：正式 provider（长期方向）
- `codex-host-image`：宿主适配器（低门槛接入）

当前配置推荐统一使用：

```bash
videoclaw config --project my-project --set models.image.backend=gemini
videoclaw config --project my-project --set models.image.model=gemini-3-pro-image-preview
```

也兼容新的 backend 命名：

```bash
videoclaw config --project my-project --set models.image.backend=openai-image
videoclaw config --project my-project --set models.image.auth=api_key
```

## 视频工作流

### 单段视频

单段视频会在 `videos/<slug>/render/` 下落盘：

- `input/reference.json`
- `input/prompt.md`
- `candidates/`
- `selected.mp4`
- `task.json`

### 当前可用命令骨架

```bash
videoclaw video create my-project demo-video
videoclaw video list my-project
videoclaw video status my-project demo-video
videoclaw video generate my-project demo-video --prompt "walk forward" --provider mock
videoclaw video select my-project demo-video v001.mp4
```

## 支持的模型提供商

| 提供商 / Backend | 图像 | 视频 | 音频 |
|------------------|------|------|------|
| volcengine | Seedream | Seedance 2.0 | TTS |
| dashscope | wan2.6-t2i | wan2.6-i2v | cosyvoice-v2 |
| gemini | Nano Banana Pro | - | - |
| openai-image | 规划中 / 接入中 | - | - |
| codex-host-image | 宿主适配路径 | - | - |
| mock | 测试用 | 测试用 | 测试用 |

## Skills

所有视频创作流程通过 `skills/` 目录中的 skill pack 定义。当前主要 skill 包括：

- `video-quick-create`
- `video-text-storyboard`
- `video-t2i`
- `video-i2i`
- `video-i2v`
- `video-audio`
- `video-merge`
- `video-config`
- `video-upload`
- `video-publish-douyin`
- `video-publish-kuaishou`

## CLI 命令

| 命令 | 说明 |
|------|------|
| `videoclaw init` | 初始化 project |
| `videoclaw video create` | 创建 video |
| `videoclaw video list` | 列出 video |
| `videoclaw video status` | 查看 video 状态 |
| `videoclaw video generate` | 生成单段视频候选 |
| `videoclaw video select` | 选择单段视频候选 |
| `videoclaw t2i` | 文生图 |
| `videoclaw i2i` | 图生图 |
| `videoclaw i2v` | 图生视频 |
| `videoclaw audio` | 生成音频 |
| `videoclaw merge` | 合并视频 |
| `videoclaw config` | 配置管理 |
| `videoclaw upload` | 云盘上传 |
| `videoclaw preview` | 预览文件 |
| `videoclaw publish` | 发布到社交平台（可选依赖） |

## 配置

详细配置项清单见 [docs/configuration.md](docs/configuration.md)

配置优先级：

1. 环境变量（最高）
2. 全局配置 `~/.videoclaw/config.yaml`
3. 项目配置 `<project>/.videoclaw/config.yaml`

## 开发

```bash
pytest
ruff check .
black .
```

MIT
