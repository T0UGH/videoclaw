# 配置说明

本文档列出 videoclaw 当前的主要配置项，并说明新旧命名在过渡阶段的关系。

## 配置优先级

1. **环境变量**（最高）：如 `DASHSCOPE_API_KEY`, `ARK_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`
2. **项目配置**：`<project>/.videoclaw/config.yaml`
3. **全局配置**：`~/.videoclaw/config.yaml`

推荐默认值：

- 如果你有 Codex / ChatGPT 登录环境，优先使用 `models.image.backend=codex-host-image`
- 如果你不走 Codex 订阅链路，再切换到 `gemini` / `volcengine` / `dashscope`


## 模型配置 (models)

### 图像模型 (models.image)

推荐优先使用新的 backend 语义：

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `models.image.backend` | 图像 backend | `gemini` | `volcengine`, `dashscope`, `gemini`, `mock`, `openai-image`, `codex-host-image` |
| `models.image.model` | 图像模型名 | `gemini-3-pro-image-preview` | 见下方模型列表 |
| `models.image.auth` | 认证来源语义 | `api_key` | `api_key`, `chatgpt_login` |
| `models.image.codex_mode` | Codex host 执行模式 | `exec` | `exec` |

兼容说明：

- `models.image.provider` 仍可读取，作为过渡字段；
- 若同时存在，`models.image.backend` 优先于 `models.image.provider`。

### 视频模型 (models.video)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `models.video.provider` | 视频生成提供商 | `volcengine` | `volcengine`, `dashscope`, `mock` |
| `models.video.model` | 视频模型 | `seedance` | `seedance`, `wan2.6-i2v` |
| `models.video.resolution` | 视频分辨率 | `1280x720` | `1280x720`, `1920x1080` |

### 音频模型 (models.audio)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `models.audio.provider` | 音频提供商 | `dashscope` | `dashscope`, `volcengine`, `mock` |
| `models.audio.model` | 音频模型 | `cosyvoice-v2` | `cosyvoice-v2`, `tts` |

## 存储配置 (storage)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `storage.provider` | 存储提供商 | `local` | `local`, `google_drive` |
| `storage.upload_on_generate` | 生成后自动上传 | `false` | `true`, `false` |
| `storage.credentials_path` | 云存储凭证路径 | `/path/to/credentials.json` | - |

## API 密钥配置

| 配置项 | 环境变量 | 说明 |
|--------|----------|------|
| `dashscope.api_key` | `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key |
| `ark.api_key` | `ARK_API_KEY` | 火山引擎方舟 API Key |
| `google.api_key` | `GOOGLE_API_KEY` | Google API Key |
| `openai.api_key` | `OPENAI_API_KEY` | OpenAI API Key |

## 各提供商 / backend 模型列表

### 图像

**volcengine (Seedream)**
- `seedream-3.0`

**dashscope**
- `wan2.6-t2i`

**gemini**
- `gemini-3-pro-image-preview`
- `gemini-2.5-flash-image`
- `imagen-4.0-generate-preview-06-06`
- `imagen-4.0-ultra-generate-preview-06-06`

**openai-image**
- `gpt-image-1`
- 使用 `OPENAI_API_KEY` 或 `openai.api_key`
- 直接调用 OpenAI 官方图片 API

**codex-host-image**
- 当前通过本机 Codex host capability 出图；
- 依赖本机 `codex` binary 和登录态。

### 视频

**volcengine (Seedance)**
- `seedance-v1`

**dashscope**
- `wan2.6-i2v`

## 配置示例

### 通过 CLI 设置

```bash
# 推荐使用新 backend 字段
videoclaw config --project my-project --set models.image.backend=gemini
videoclaw config --project my-project --set models.image.model=gemini-3-pro-image-preview

# 使用 codex host adapter
videoclaw config --project my-project --set models.image.backend=codex-host-image
videoclaw config --project my-project --set models.image.auth=chatgpt_login
videoclaw config --project my-project --set models.image.codex_mode=exec

# 使用 openai-image 命名
videoclaw config --project my-project --set models.image.backend=openai-image
videoclaw config --project my-project --set models.image.auth=api_key

# 设置视频分辨率
videoclaw config --project my-project --set models.video.resolution=1920x1080

# 查看配置
videoclaw config --project my-project --list
```

### 通过 YAML 文件设置

```yaml
project_name: my-project
version: "0.1.0"

models:
  image:
    backend: gemini
    model: gemini-3-pro-image-preview
  video:
    provider: volcengine
    model: seedance
    resolution: 1280x720

storage:
  provider: local
  upload_on_generate: false
```

### 通过环境变量设置

```bash
export ARK_API_KEY="your-ark-api-key"
export DASHSCOPE_API_KEY="your-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export VIDEOCLAW_MODELS_IMAGE_BACKEND=gemini
```
