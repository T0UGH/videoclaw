# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 安装项目
pip install -e .

# 运行 CLI
videoclaw --help

# 运行测试
pytest
pytest tests/                          # 运行所有测试
pytest tests/test_config.py            # 运行单个测试文件
pytest tests/test_config.py::test_xxx  # 运行单个测试

# 代码检查
ruff check .
black .

# 发布到 PyPI
uvx --from build pyproject-build            # 构建包
uvx twine upload dist/*                     # 发布到 PyPI
# 注意：发布前需要先 bump 版本号（修改 pyproject.toml 中的 version）

# 初始化项目
videoclaw init my-project

# 配置管理
videoclaw config --help
```

## 项目架构

### 整体结构

```
videoclaw/
├── cli/                    # 命令行入口 (Click)
│   ├── main.py            # 主入口，注册子命令
│   └── commands/         # 子命令
│       ├── init.py       # 项目初始化
│       ├── t2i.py        # 文生图
│       ├── i2i.py       # 图生图
│       ├── i2v.py       # 图生视频
│       ├── audio.py      # 音频生成
│       ├── merge.py      # 视频合并
│       ├── preview.py    # 预览
│       ├── config.py    # 配置管理
│       ├── upload.py    # 云盘上传
│       └── publish.py   # 社交媒体发布
├── config/                # 配置加载器
│   └── loader.py         # Config 类，支持全局/项目配置 + 环境变量
├── models/               # AI 模型抽象层（可插拔）
│   ├── base.py          # ImageBackend, VideoBackend, AudioBackend 基类
│   ├── factory.py       # get_image_backend, get_video_backend, get_audio_backend
│   ├── dashscope/      # 阿里云 DashScope (t2i, i2v, tts)
│   ├── volcengine/     # 字节系火山引擎 (seedream, seedance, tts)
│   ├── gemini/         # Google Gemini
│   └── mock/           # 测试用 Mock
├── storage/             # 存储抽象层
│   ├── base.py         # StorageBackend 基类
│   ├── local.py        # 本地存储实现
│   └── google_drive.py # Google Drive 上传
├── publisher/           # 社交媒体发布
│   ├── douyin.py       # 抖音发布
│   └── kuaishou.py    # 快手发布
├── ffmpeg/              # FFmpeg 处理
│   └── processor.py    # 视频处理
└── utils/               # 工具函数
```

### 视频创建流程（quick-create）

```
故事大纲 → 素材准备 → 文本分镜 → i2v 生成视频
  (Claude Code)   (T2I)      (I2V)
```

### 配置优先级

1. **环境变量**（最高）：`DASHSCOPE_API_KEY`, `ARK_API_KEY`, `GOOGLE_API_KEY`, `VIDEOCLAW_*`
2. **项目配置**：`<project>/.videoclaw/config.yaml`
3. **全局配置**：`~/.videoclaw/config.yaml`

配置加载使用深度合并，项目配置会覆盖全局配置的同名键。

完整配置项清单见 [docs/configuration.md](docs/configuration.md)

### 项目存储结构

```
~/videoclaw-projects/<project>/
├── .videoclaw/
│   └── config.yaml    # 项目配置
├── videos/           # 生成的视频片段
└── audio/            # 音频文件
```

### 模型后端

支持跨厂商混用：
- **dashscope**：图像(wan2.6-t2i)、视频(wan2.6-i2v)、音频(cosyvoice-v2)
- **volcengine**：图像(seedream)、视频(seedance)、音频(tts)
- **gemini**：图像生成 (gemini-3-pro-image-preview, gemini-2.5-flash-image)
- **mock**：测试用

### Google Gemini

- **gemini**: 图像生成 (gemini-3-pro-image-preview, gemini-2.5-flash-image)
- 使用 `GOOGLE_API_KEY` 环境变量认证
- 安装: `pip install google-genai`

### VolcEngine 火山引擎接入说明

**重要**：火山引擎方舟 API 使用 Bearer Token 认证，不是 AK/SK 签名。

**认证方式**：
```python
# 使用 ARK_API_KEY (从控制台获取)
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="your-ark-api-key"
)
```

**API 端点**：
- Seedream: `POST /api/v3/images/generations`
- Seedance: `POST /api/v3/contents/generations/tasks` (异步)

**环境变量**：
```bash
ARK_API_KEY=xxx  # 火山引擎方舟 API Key
```

**依赖**：
```toml
volcengine-python-sdk[ark]>=5.0.0
httpx>=0.27.0
```

## CLI 工具使用说明

**重要**：所有 CLI 工具仅供 Claude Code 调用，不面向终端用户。

### 设计原则

- **纯执行**：CLI 工具只负责执行命令，不做交互确认
- **交互在 Skill 层**：用户交互通过 video-create skill 的 AskUserQuestion 实现
- **Claude Code 专用**：用户不直接运行这些 CLI 命令

### 常用命令

```bash
# 文生图
videoclaw t2i --project my-project -p "宇航员在火星上"

# 图生视频
videoclaw i2v --project my-project -i image.png -t "角色向前行走"

# 音频生成
videoclaw audio --project my-project -t "这是测试语音"

# 视频合并
videoclaw merge --project my-project -v video1.mp4 -v video2.mp4
```

### 与 Skill 集成

video-create skill 负责交互流程：
1. 用 AskUserQuestion 与用户确认需求
2. 调用 CLI 命令执行
3. 读取生成结果，用 AskUserQuestion 让用户确认
4. 根据用户反馈决定是否重新生成

### 云盘存储配置

```bash
# 配置 Google Drive 上传
videoclaw config --set storage.provider=google_drive
videoclaw config --set storage.upload_on_generate=true
```

如需关闭上传功能：

```bash
videoclaw config --set storage.provider=local
```
