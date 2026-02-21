# videoclaw

AI 视频创作 CLI 工具，专为 Claude Code 设计。

## 概述

videoclaw 是一个 AI 视频生成工具，通过命令行与 Claude Code 集成，支持多种 AI 模型提供商，帮助用户快速创建视频内容。

## 两种创作模式

### video-quick-create（快速模式）

简化流程，追求快速出片：
1. 用户描述视频想法
2. 生成九宫格角色资产图（T2I/I2I）
3. 生成文本分镜（video-text-storyboard）
4. i2v 生成视频

适合快速验证想法或使用seedance2.0这种强力模型的情况

### video-standard-create（标准模式）

完整的视频创作流程，包含多轮交互确认：
1. 用户描述视频想法
2. AI 分析并生成角色/场景资产（多张候选供选择）
3. AI 生成图片故事板
4. 用户确认每一帧
5. 图生视频
6. 音频生成
7. 视频合并

适合需要精细控制的视频创作。

## 安装

### 方式一：uvx（推荐，无需安装）

```bash

# 直接运行（无需安装）
uvx videoclaw --help

# 或安装到本地
uv pip install videoclaw
```

### 方式二：pip

```bash
pip install videoclaw
```

### 方式三：开发模式

```bash
# 克隆项目
git clone https://github.com/T0UGH/videoclaw.git
cd videoclaw

# 安装依赖
pip install -e .

# 配置 API Key
export ARK_API_KEY=your-ark-api-key      # 火山引擎
export DASHSCOPE_API_KEY=your-api-key   # 阿里云
export GOOGLE_API_KEY=your-api-key       # Google Gemini
```

## 安装 Skills（Claude Code 插件）

要使用 Claude Code Skills，需要安装 videoclaw 插件市场：

```bash
# 在 Claude Code 中运行
/claude install marketplace https://github.com/T0UGH/videoclaw/raw/main/.claude-plugin/marketplace.json
```

安装后，Claude Code 会自动加载所有 skills。

## 快速开始

```bash
# 初始化项目
videoclaw init my-video

# 查看帮助
videoclaw --help
```

**完整流程（通过 skill 调用）：**

Claude Code 会根据你的需求自动调用相应的 skill：
- `video-standard-create` - 标准模式
- `video-quick-create` - 快速模式
- `video-text-storyboard` - 独立文本分镜生成

## 支持的模型提供商

| 提供商 | 图像 (T2I) | 视频 (I2V) | 音频 (TTS) |
|--------|-------------|--------------|-------------|
| volcengine | Seedream | Seedance | TTS |
| dashscope | wan2.6-t2i | wan2.6-i2v | cosyvoice-v2 |
| gemini | gemini-3-pro-image-preview | - | - |
| mock | 测试用 | 测试用 | 测试用 |

## 配置

### 环境变量

```bash
export ARK_API_KEY=xxx           # 火山引擎方舟 API Key
export DASHSCOPE_API_KEY=xxx    # 阿里云 API Key
export GOOGLE_API_KEY=xxx        # Google API Key
```

### 全局配置

```bash
# 图像提供商
videoclaw config --global --set models.image.provider=volcengine

# 视频提供商
videoclaw config --global --set models.video.provider=volcengine
```

### 项目配置

```bash
videoclaw config --project my-video --set models.image.provider=gemini
```

### 配置优先级

1. 环境变量（最高）
2. 全局配置 `~/.videoclaw/config.yaml`
3. 项目配置 `<project>/.videoclaw/config.yaml`

## 项目结构

```
~/videoclaw-projects/<project>/
├── .videoclaw/
│   ├── config.yaml    # 项目配置
│   └── state.json    # 状态跟踪
├── assets/           # 角色/场景图片
├── storyboard/       # 故事板帧图片
├── videos/           # 生成的视频片段
└── audio/            # 音频文件
```

## CLI 命令

| 命令 | 说明 |
|------|------|
| `videoclaw init` | 初始化项目 |
| `videoclaw assets` | 生成角色/场景资产 |
| `videoclaw storyboard` | 生成故事板 |
| `videoclaw i2v` | 图生视频 |
| `videoclaw audio` | 生成音频 |
| `videoclaw merge` | 合并视频 |
| `videoclaw t2i` | 独立文生图 |
| `videoclaw i2i` | 独立图生图 |
| `videoclaw config` | 配置管理 |
| `videoclaw status` | 查看状态 |

## Skills

所有视频创作流程通过 Claude Code Skills 实现：

| Skill | 说明 |
|-------|------|
| video-standard-create | 标准模式（多轮交互） |
| video-quick-create | 快速模式 |
| video-text-storyboard | 文本分镜生成 |
| video-assets | 资产生成 |
| video-storyboard | 图片故事板 |
| video-i2v | 图生视频 |
| video-audio | 音频生成 |
| video-merge | 视频合并 |
| video-config | 配置管理 |
| video-status | 状态查看 |

## 云盘存储

支持将生成的视频/图片上传到 Google Drive：

```bash
# 开启上传
videoclaw config --global --set storage.provider=google_drive
videoclaw config --global --set storage.upload_on_generate=true
```

## 开发

```bash
# 运行测试
pytest

# 代码检查
ruff check .
black .
```

## License

MIT
