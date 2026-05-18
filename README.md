# videoclaw

[English](README_en.md) | **AI 视频创作 CLI 工具 | Codex 订阅出图 + Seedance 官方视频 API**

## ⭐ 主推荐链路 ⭐

| 视频生成 | 图片素材 |
|----------|----------|
| **Seedance 2.0** (字节跳动官方 Ark API) | **Codex OAuth-native** (无需 OpenAI API key) |

> 如果你已经有 Codex / ChatGPT 订阅与登录态，现在可以直接走 Codex 原生链路出图；视频则走火山官方 Seedance API。

## 概述

videoclaw 是 AI 视频创作 CLI 工具，目标是把 AI 视频创作真正做成一条能跑通的工作流：

- **图片**：默认走 `codex-host-image`，通过 Codex / ChatGPT OAuth 原生链路出图
- **视频**：默认走火山引擎 Ark / Seedance 官方 API
- **结构**：一个 `project` 管多个 `video`，支持单段 `render/` 和多段 `clips/`
- **分发**：`videoclaw` CLI + 可安装的 skill pack（`skills.sh`）

也就是说，这个项目现在不只是 prompt 模板集合，而是：

> **一个能真实出图、真实出视频、真实合并产物的 AI 视频创作 CLI + Skill Pack。**

## 推荐客户端

| 客户端 | 状态 |
|--------|------|
| 支持 `skills.sh` 的客户端 | ✅ 主推荐 |
| Codex / ChatGPT 登录环境 | ✅ 默认图片链路 |
| Claude Code | ✅ 可用，但不再是主分发方式 |
| 其他 skills-compatible hosts | ✅ 原则上可接入 |

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

## 安装 Skill Pack（主推荐方式）

推荐直接通过 `skills.sh` 安装整个 skill pack：

```bash
npx skills add T0UGH/videoclaw --all
```

常见变体：

```bash
# 本地开发时从仓库根目录安装
npx skills add . --all

# 只安装一个 skill
npx skills add T0UGH/videoclaw --skill video-quick-create

# 查看可安装的 skills
npx skills add T0UGH/videoclaw --list
```

这条路径现在是 videoclaw 的主分发方式。`skills/` 目录是 workflow 的唯一事实源。

## 快速开始（30 秒）

```bash
# 1. 初始化一个 project
videoclaw init my-project

# 2. 在 project 下创建一个视频单元
videoclaw video create my-project demo-video

# 3. 查看视频列表
videoclaw video list my-project
```

如果你已经有 Codex / ChatGPT 登录环境，建议把图片默认链路显式设成：

```bash
videoclaw config --project my-project --set models.image.backend=codex-host-image
videoclaw config --project my-project --set models.image.model=gpt-image-2-medium
videoclaw config --project my-project --set models.image.auth=chatgpt_login
videoclaw config --project my-project --set models.image.transport=codex_oauth
```

## 新的 Project / Video 模型

videoclaw 现在采用：

- 一个 `project` 承载共享资产与多个视频
- 一个 `video` 是独立产出单元
- 单段视频默认使用 `render/` 管理生成过程
- 多段视频可扩展到 `clips/`

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

图片能力现在有两条正式可用路径：

### 1. `codex-host-image`（默认推荐）

这是当前最推荐的图片链路：

- Hermes-style / OAuth-native Codex image provider
- 不需要 `OPENAI_API_KEY`
- 读取本机 Codex / ChatGPT 登录态
- 支持：
  - `gpt-image-2-low`
  - `gpt-image-2-medium`
  - `gpt-image-2-high`

推荐默认值：`gpt-image-2-medium`

### 2. `openai-image`

这是正式的 OpenAI API provider：

- 需要 `OPENAI_API_KEY`
- 直接调用 OpenAI 官方图片 API

如果你不走 Codex 订阅链路，可以改成：

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

### 多段视频

多段视频可以使用 `clips/`：

- `clips/<clip-id>/input/reference.json`
- `clips/<clip-id>/input/prompt.md`
- `clips/<clip-id>/candidates/`
- `clips/<clip-id>/selected.mp4`
- `clips/<clip-id>/task.json`

### 当前可用命令

```bash
videoclaw video create my-project demo-video
videoclaw video list my-project
videoclaw video status my-project demo-video
videoclaw video generate my-project demo-video --prompt "walk forward" --provider mock
videoclaw video select my-project demo-video v001.mp4

videoclaw video clip create my-project demo-video clip-01
videoclaw video clip generate my-project demo-video clip-01 --prompt "turn head" --provider mock
videoclaw video clip select my-project demo-video clip-01 v001.mp4

videoclaw merge --project my-project --output final.mp4
```

## 支持的模型提供商

| 提供商 / Backend | 图像 | 视频 | 音频 |
|------------------|------|------|------|
| volcengine | Seedream | Seedance 2.0 | TTS |
| dashscope | wan2.6-t2i | wan2.6-i2v | cosyvoice-v2 |
| gemini | Nano Banana Pro | - | - |
| openai-image | OpenAI 官方图片 API | - | - |
| codex-host-image | Codex OAuth 原生链路 | - | - |
| mock | 测试用 | 测试用 | 测试用 |

## Skills

所有视频创作流程通过 `skills/` 目录中的 skill pack 定义。当前主要 skill 包括：

| Skill | 说明 |
|-------|------|
| video-quick-create | 快速创建视频（故事类） |
| video-text-storyboard | 文本分镜生成（故事/产品/动作/风景） |
| video-t2i | 文生图 |
| video-i2i | 图生图 |
| video-i2v | 图生视频 |
| video-audio | 音频生成 |
| video-merge | 视频合并 |
| video-config | 配置管理 |
| video-upload | 云盘上传 |
| video-publish-douyin | 发布到抖音 |
| video-publish-kuaishou | 发布到快手 |

## CLI 命令

| 命令 | 说明 |
|------|------|
| `videoclaw init` | 初始化 project |
| `videoclaw video create` | 创建 video |
| `videoclaw video list` | 列出 video |
| `videoclaw video status` | 查看 video 状态 |
| `videoclaw video generate` | 生成单段视频候选 |
| `videoclaw video select` | 选择单段视频候选 |
| `videoclaw video clip create` | 创建 clip |
| `videoclaw video clip generate` | 生成 clip 候选 |
| `videoclaw video clip select` | 选择 clip 候选 |
| `videoclaw t2i` | 文生图 |
| `videoclaw i2i` | 图生图 |
| `videoclaw image smoke` | 图片 backend 冒烟 |
| `videoclaw i2v` | 图生视频 |
| `videoclaw video-smoke` | 视频 backend 冒烟 |
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

## 当前真实跑通的主链路

目前已经真实冒烟通过的主链路：

- 图片：`codex-host-image`
- 视频：`volcengine` / Ark / Seedance

也就是说，这个项目现在不是只停在设计上，而是主推荐图片链路和主推荐视频链路都已经真实跑通。

## 开发

```bash
pytest
ruff check .
black .
```
