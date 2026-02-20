# Google Gemini 模型

本文档记录所有可用的 Google AI/Cloud 模型，供 videoclaw 项目使用。

## 图像生成模型

### Gemini API (ai.google.dev)

使用 google-genai SDK，API Key 认证。

| 模型 | 名称 | 特点 | 推荐场景 |
|------|------|------|----------|
| `gemini-2.0-flash-exp-image-generation` | Nano Banana | 实验模型，原生集成，最新能力 | 快速原型、个人项目 |
| `imagen-3.0-fast` | Imagen 3.0 Fast | 快速生成，性价比高 | 批量生成 |
| `imagen-3.0-generate-002` | Imagen 3.0 | 最高质量 | 最终输出 |

**安装:**
```bash
pip install google-genai
```

**认证:**
```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
```

**使用示例:**
```python
from videoclaw.models.factory import get_image_backend

backend = get_image_backend("gemini", "gemini-2.0-flash-exp-image-generation", {
    "api_key": os.environ["GOOGLE_API_KEY"]
})

result = backend.text_to_image("A cat sitting on a couch")
```

### Vertex AI (cloud.google.com)

使用 google-cloud-vertexai SDK，Service Account 认证。

| 模型 | 名称 | 特点 |
|------|------|------|
| `imagen-4.0-fast` | Imagen 4.0 Fast | 最高质量，最新版本 |
| `imagen-3.0-fast` | Imagen 3.0 Fast | 性价比高 |
| `gemini-2.0-flash-exp-001` | Gemini Flash | 原生图像生成 |

**安装:**
```bash
pip install google-cloud-vertexai
```

**认证:** Service Account JSON 密钥

---

## 视频生成模型

### Veo (Gemini API)

| 模型 | 名称 | 特点 |
|------|------|------|
| `veo-3.1` | Veo 3.1 | 状态-of-the-art，支持原生音频 |

**注意:** 视频生成需通过 Vertex AI 或 Google AI Studio

---

## 音频模型

### Lyria (实验)

音乐生成模型，需通过 Vertex AI 使用。

### TTS

使用 Gemini API 的 Live API 或 Vertex AI TTS

---

## 配置示例

```bash
# 设置 API Key
export GOOGLE_API_KEY="your-api-key"

# 在项目中使用
videoclaw config --project my-project --set models.image.provider=gemini
videoclaw config --project my-project --set models.image.model=gemini-2.0-flash-exp-image-generation
```

## 相关链接

- [Gemini API 文档](https://ai.google.dev/gemini-api/docs)
- [Imagen 文档](https://ai.google.dev/gemini-api/docs/imagen)
- [Vertex AI 文档](https://cloud.google.com/vertex-ai)
- [Google AI Studio](https://aistudio.google.com/app/apikey)
