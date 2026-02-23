# videoclaw

[English](README_en.md) | **AI 视频创作 CLI 工具 | SOTA 模型强强联合**

## ⭐ SOTA 模型强强联合 ⭐

| 视频生成 | 图片素材 |
|----------|----------|
| **Seedance 2.0** (字节跳动) | **Nano Banana Pro** (Google Gemini) |

> 业界顶级视频生成方案：Seedance 2.0 + Nano Banana Pro 强强联合

## 概述

videoclaw 是 AI 视频创作 CLI 工具，深度集成 Seedance 2.0 + Nano Banana Pro 业界顶级模型，让 AI 视频生成像说话一样简单——告诉 AI 你的想法，它会自动完成从素材生成到视频合成的全部工作。

## 推荐客户端

| 客户端 | 状态 |
|--------|------|
| Claude Code | ✅ 已在使用 |
| Claude Cowork | ✅ 已适配 |
| OpenCode | 🔄 适配中 |
| Codex | 🔄 适配中 |
| OpenCowork | 🔄 适配中 |

> 理论上按照各客户端的 skills 安装方式即可使用 videoclaw。

## 安装 Skills（Claude Code 插件）

要使用 Claude Code Skills，需要安装 videoclaw 插件市场：

```bash
# 在 Claude Code 中运行
/claude install marketplace https://github.com/T0UGH/videoclaw/raw/main/.claude-plugin/marketplace.json
```

安装后，Claude Code 会自动加载所有 skills。

## 安装 CLI

### 方式一：uvx（推荐，无需安装）

```bash
# 直接运行（无需安装）
uvx videoclaw --help
```

### 方式二：pip（全局安装）

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

### video-quick-create 流程

```
1. 描述想法 → AI 生成故事大纲（主题、剧情、角色）
2. 准备素材 → AI 生成角色九宫格图、场景图（T2I/I2I 模式，推荐 Nano Banana Pro）
3. 生成脚本 → AI 生成结构化分镜（镜头、画面、音效）
4. 生成视频 → AI 图生视频（推荐 Seedance 2.0）
```

详细流程见 [video-quick-create skill](../skills/video-quick-create/SKILL.md)

## 支持的模型提供商

| 提供商 | 图像 (T2I) | 视频 (I2V) | 音频 (TTS) |
|--------|-------------|--------------|-------------|
| volcengine | Seedream | **Seedance 2.0** | TTS |
| dashscope | wan2.6-t2i | wan2.6-i2v | cosyvoice-v2 |
| gemini | **Nano Banana Pro** | - | - |
| mock | 测试用 | 测试用 | 测试用 |

> ⚡ **推荐配置**：图像用 **Nano Banana Pro** (gemini)，视频用 **Seedance 2.0** (volcengine)，体验业界最前沿的 AI 视频生成能力

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

支持自动发布视频到抖音、快手等平台。发布参考 [social-auto-upload](https://github.com/dreammis/social-auto-upload)。

如需发布到抖音，使用 `video-publish-douyin` skill。

## 配置

详细配置项清单见 [docs/configuration.md](docs/configuration.md)

火山系模型 API Key 获取详见[官方文档](https://www.volcengine.com/docs/82379/1099455?lang=zh)

Gemini 系模型 API Key 获取和使用详见[官方文档](https://ai.google.dev/gemini-api/docs?hl=zh-cn)

### 环境变量

```bash
export ARK_API_KEY=xxx           # 火山引擎方舟 API Key
export DASHSCOPE_API_KEY=xxx    # 阿里云 API Key
export GOOGLE_API_KEY=xxx        # Google API Key
```

### 全局配置

```bash
# 图像提供商 - 推荐使用 Nano Banana Pro (gemini)
videoclaw config --global --set models.image.provider=gemini

# 视频提供商 - 推荐使用 Seedance 2.0 (volcengine)
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

## 手机端使用

手机端推荐使用 [Happy](https://github.com/slopus/happy)，可连接 PC 端的 Claude Code 进行视频创作。

图片和视频素材的同步推荐使用 Google Drive、iCloud 或坚果云，这些工具都有自动同步本地文件夹到云盘的功能。

## 开发

```bash
# 运行测试
pytest

# 代码检查
ruff check .
black .
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

## License

MIT
