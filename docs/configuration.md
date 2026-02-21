# 配置说明

本文档列出 videoclaw 的所有可配置项。

## 配置优先级

1. **环境变量**（最高）：如 `DASHSCOPE_API_KEY`, `ARK_API_KEY`, `GOOGLE_API_KEY`
2. **项目配置**：`<project>/.videoclaw/config.yaml`
3. **全局配置**：`~/.videoclaw/config.yaml`

## 配置项清单

### 项目基础配置

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `project_name` | 项目名称 | `mars-video` |
| `version` | 项目版本 | `0.1.0` |

### 模型配置 (models)

#### 图像模型 (models.image)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `models.image.provider` | 图像生成提供商 | `volcengine` | `volcengine`, `dashscope`, `gemini`, `mock` |
| `models.image.model` | 图像生成模型 | `gemini-3-pro-image-preview` | 见下方模型列表 |

#### 视频模型 (models.video)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `models.video.provider` | 视频生成提供商 | `volcengine` | `volcengine`, `dashscope`, `mock` |
| `models.video.model` | 视频生成模型 | `seedance` | `seedance`, `wan2.6-i2v` |
| `models.video.resolution` | 视频分辨率 | `1280x720` | `1280x720`, `1920x1080` |

#### 音频模型 (models.audio)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `models.audio.provider` | 音频提供商 | `dashscope` | `dashscope`, `volcengine`, `mock` |
| `models.audio.model` | 音频模型 | `cosyvoice-v2` | `cosyvoice-v2`, `tts` |

### 存储配置 (storage)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `storage.provider` | 存储提供商 | `local` | `local`, `google_drive` |
| `storage.upload_on_generate` | 生成后自动上传 | `false` | `true`, `false` |
| `storage.credentials_path` | 云存储凭证路径 | `/path/to/credentials.json` | - |

### 日志配置 (logging)

| 配置项 | 说明 | 示例值 | 可选值 |
|--------|------|--------|--------|
| `logging.level` | 控制台日志级别 | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `logging.file_level` | 文件日志级别 | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### API 密钥配置

| 配置项 | 环境变量 | 说明 |
|--------|----------|------|
| `dashscope.api_key` | `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key |
| `volcengine.api_key` / `ark.api_key` | `ARK_API_KEY` | 火山引擎方舟 API Key |
| `volcengine.ak` | `VOLCENGINE_AK` | 火山引擎 Access Key |
| `volcengine.sk` | `VOLCENGINE_SK` | 火山引擎 Secret Key |
| `google.api_key` | `GOOGLE_API_KEY` | Google API Key |

## 各提供商模型列表

### 图像模型

**volcengine (Seedream):**
- `seedream-3.0`

**dashscope:**
- `wan2.6-t2i`

**gemini:**
- `gemini-3-pro-image-preview` - Nano Banana Pro，质量优先
- `gemini-2.5-flash-image` - Nano Banana，速度优先
- `imagen-4.0-generate-preview-06-06` - Imagen 4.0，最高质量
- `imagen-4.0-ultra-generate-preview-06-06` - Imagen 4.0 Ultra

### 视频模型

**volcengine (Seedance):**
- `seedance-v1`

**dashscope:**
- `wan2.6-i2v`

### 音频模型

**dashscope (CosyVoice):**
- `cosyvoice-v2`

**volcengine (TTS):**
- `tts` - 火山引擎 TTS

## 配置示例

### 通过 CLI 设置

```bash
# 设置图像提供商
videoclaw config --project my-project --set models.image.provider=gemini

# 设置图像模型
videoclaw config --project my-project --set models.image.model=gemini-3-pro-image-preview

# 设置视频分辨率
videoclaw config --project my-project --set models.video.resolution=1920x1080

# 开启生成后自动上传
videoclaw config --project my-project --set storage.upload_on_generate=true

# 查看配置
videoclaw config --project my-project --list
```

### 通过 YAML 文件设置

项目配置文件：`~/videoclaw-projects/my-project/.videoclaw/config.yaml`

```yaml
project_name: my-project
version: "0.1.0"

models:
  image:
    provider: gemini
    model: gemini-3-pro-image-preview
  video:
    provider: volcengine
    model: seedance
    resolution: 1280x720

storage:
  provider: local
  upload_on_generate: false

logging:
  level: INFO
  file_level: DEBUG
```

全局配置文件：`~/.videoclaw/config.yaml`

```yaml
# 全局默认设置
models:
  image:
    provider: volcengine
  video:
    provider: volcengine
    resolution: 1280x720
```

### 通过环境变量设置

```bash
# 阿里云
export DASHSCOPE_API_KEY="your-api-key"

# 火山引擎
export ARK_API_KEY="your-ark-api-key"

# Google
export GOOGLE_API_KEY="your-google-api-key"

# 通用格式 (VIDEOCLAW_前缀 + key)
export VIDEOCLAW_MODELS_IMAGE_PROVIDER=gemini
```
