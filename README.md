# videoclaw

AI 视频创作 CLI 工具，专为 Claude Code 设计。

## 概述

videoclaw 是一个 AI 视频生成工具，通过命令行与 Claude Code 集成，支持多种 AI 模型提供商，帮助用户快速创建视频内容。

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

## 发布新版本

```bash
# 1. 更新版本号（修改 pyproject.toml 中的 version）
# 2. 提交更改
git add pyproject.toml && git commit -m "chore: bump version to x.x.x"

# 3. 推送到 GitHub
git push

# 4. 构建并发布到 PyPI
uvx --from build pyproject-build
uvx twine upload dist/*
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
│   └── config.yaml    # 项目配置
├── videos/           # 生成的视频片段
└── audio/            # 音频文件
```

## CLI 命令

| 命令 | 说明 |
|------|------|
| `videoclaw init` | 初始化项目 |
| `videoclaw t2i` | 文生图 |
| `videoclaw i2i` | 图生图 |
| `videoclaw i2v` | 图生视频 |
| `videoclaw audio` | 生成音频 |
| `videoclaw merge` | 合并视频 |
| `videoclaw config` | 配置管理 |
| `videoclaw upload` | 云盘上传 |
| `videoclaw preview` | 预览文件 |
| `videoclaw publish` | 发布到社交平台 |

## Skills

所有视频创作流程通过 Claude Code Skills 实现：

| Skill | 说明 |
|-------|------|
| video-quick-create | 快速创建视频 |
| video-text-storyboard | 文本分镜生成 |
| video-t2i | 文生图 |
| video-i2i | 图生图 |
| video-i2v | 图生视频 |
| video-audio | 音频生成 |
| video-merge | 视频合并 |
| video-config | 配置管理 |
| video-upload | 云盘上传 |
| video-publish-douyin | 发布到抖音 |
| video-publish-kuaishou | 发布到快手 |

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
