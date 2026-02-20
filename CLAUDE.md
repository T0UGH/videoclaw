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

# 初始化项目
videoclaw init my-project

# 查看项目状态
videoclaw status -p my-project

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
│       ├── assets.py     # 资产生成
│       ├── storyboard.py # 故事板生成
│       ├── i2v.py       # 图生视频
│       ├── audio.py     # 音频生成
│       ├── merge.py     # 视频合并
│       ├── preview.py   # 预览
│       └── config.py    # 配置管理
├── config/                # 配置加载器
│   └── loader.py         # Config 类，支持全局/项目配置 + 环境变量
├── models/               # AI 模型抽象层（可插拔）
│   ├── base.py          # ImageBackend, VideoBackend, AudioBackend 基类
│   ├── factory.py       # get_image_backend, get_video_backend, get_audio_backend
│   ├── dashscope/      # 阿里云 DashScope (t2i, i2v, tts)
│   ├── volcengine/     # 字节系火山引擎 (seedream, seedance, tts)
│   └── mock/           # 测试用 Mock
├── storage/             # 存储抽象层
│   ├── base.py         # StorageBackend 基类
│   └── local.py        # 本地存储实现
├── state/               # 状态管理
│   └── manager.py      # StateManager，管理项目 state.json
├── pipeline/            # 工作流编排
│   └── orchestrator.py # PipelineOrchestrator
├── ffmpeg/              # FFmpeg 处理
│   └── processor.py    # 视频处理
└── utils/               # 工具函数
```

### 视频创建流程

```
脚本分析 → 资产生成 → 故事板生成 → 图生视频 → 音频生成 → 视频合并
  (Claude Code)   (T2I)      (T2I/I2I)     (I2V)       (TTS)      (FFmpeg)
```

### 配置优先级

1. **环境变量**（最高）：`DASHSCOPE_API_KEY`, `ARK_API_KEY`, `VIDEOCLAW_*`
2. **全局配置**：`~/.videoclaw/config.yaml`
3. **项目配置**：`<project>/.videoclaw/config.yaml`

### 项目存储结构

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

### 模型后端

支持跨厂商混用：
- **dashscope**：图像(wan2.6-t2i)、视频(wan2.6-i2v)、音频(cosyvoice-v2)
- **volcengine**：图像(seedream)、视频(seedance)、音频(tts)
- **mock**：测试用

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
