# videoclaw

[中文](README.md) | **AI Video Creation CLI Tool | SOTA Model Power Couple**

## ⭐ SOTA Model Power Couple ⭐

| Video Generation | Image Assets |
|------------------|--------------|
| **Seedance 2.0** (ByteDance) | **Nano Banana Pro** (Google Gemini) |

> Industry-leading video generation: Seedance 2.0 + Nano Banana Pro

## Overview

videoclaw is an AI video creation CLI tool, deeply integrated with Seedance 2.0 and Nano Banana Pro, making AI video generation as simple as telling AI your idea—it will automatically handle everything from asset generation to video synthesis.

## Recommended Clients

| Client | Status |
|--------|--------|
| Claude Code | ✅ In Use |
| Claude Cowork | ✅ Supported |
| OpenCode | 🔄 Coming Soon |
| Codex | 🔄 Coming Soon |
| OpenCowork | 🔄 Coming Soon |

>理论上按照各客户端的 skills 安装方式即可使用 videoclaw。(In theory, install skills according to each client's method to use videoclaw.)

## Install Skills (Claude Code Plugin)

To use Claude Code Skills, install the videoclaw plugin marketplace:

```bash
# Run in Claude Code
/claude install marketplace https://github.com/T0UGH/videoclaw/raw/main/.claude-plugin/marketplace.json
```

After installation, Claude Code will automatically load all skills.

## Install CLI

### Method 1: uvx (Recommended, No Installation Required)

```bash
# Run directly (no installation)
uvx videoclaw --help
```

### Method 2: pip (Global Installation)

```bash
pip install videoclaw
```

### Method 3: Development Mode

```bash
# Clone project
git clone https://github.com/T0UGH/videoclaw.git
cd videoclaw

# Install dependencies
pip install -e .

# Configure API Keys
export ARK_API_KEY=your-ark-api-key      # VolcEngine
export DASHSCOPE_API_KEY=your-api-key   # Alibaba Cloud
export GOOGLE_API_KEY=your-api-key       # Google Gemini
```

## Quick Start

```bash
# Initialize project
videoclaw init my-video

# View help
videoclaw --help
```

**Full Workflow (via skills):**

Claude Code will automatically invoke the appropriate skill based on your needs:
- `video-quick-create` - Quick mode
- `video-text-storyboard` - Standalone text storyboard generation

### video-quick-create Workflow

```
1. Describe your idea → AI generates story outline (theme, plot, characters)
2. Prepare assets → AI generates character 9-grid images, scene images (T2I/I2I mode, Nano Banana Pro recommended)
3. Generate script → AI generates structured storyboard (shots, visuals, sound effects)
4. Generate video → AI image-to-video (Seedance 2.0 recommended)
```

See [video-quick-create skill](../skills/video-quick-create/SKILL.md) for detailed workflow.

## Supported Model Providers

| Provider | Image (T2I) | Video (I2V) | Audio (TTS) |
|----------|--------------|-------------|-------------|
| volcengine | Seedream | **Seedance 2.0** | TTS |
| dashscope | wan2.6-t2i | wan2.6-i2v | cosyvoice-v2 |
| gemini | **Nano Banana Pro** | - | - |
| mock | For Testing | For Testing | For Testing |

> ⚡ **Recommended Config**: Use **Nano Banana Pro** (gemini) for images and **Seedance 2.0** (volcengine) for video

## Skills

All video creation workflows are implemented through Claude Code Skills:

| Skill | Description |
|-------|-------------|
| video-quick-create | Quick video creation |
| video-text-storyboard | Text storyboard generation |
| video-t2i | Text-to-image |
| video-i2i | Image-to-image |
| video-i2v | Image-to-video |
| video-audio | Audio generation |
| video-merge | Video merging |
| video-config | Configuration management |
| video-upload | Cloud upload |
| video-publish-douyin | Publish to Douyin |
| video-publish-kuaishou | Publish to Kuaishou |

## CLI Commands

| Command | Description |
|---------|-------------|
| `videoclaw init` | Initialize project |
| `videoclaw t2i` | Text-to-image |
| `videoclaw i2i` | Image-to-image |
| `videoclaw i2v` | Image-to-video |
| `videoclaw audio` | Generate audio |
| `videoclaw merge` | Merge videos |
| `videoclaw config` | Configuration management |
| `videoclaw upload` | Cloud upload |
| `videoclaw preview` | Preview files |
| `videoclaw publish` | Publish to social platforms |

Supports auto-publishing video to Douyin, Kuaishou and other platforms. Publishing reference [social-auto-upload](https://github.com/dreammis/social-auto-upload).

To publish to Douyin, use the `video-publish-douyin` skill.

## Configuration

See [docs/configuration.md](docs/configuration.md) for full configuration options.

### Environment Variables

```bash
export ARK_API_KEY=xxx           # VolcEngine ARK API Key
export DASHSCOPE_API_KEY=xxx    # Alibaba Cloud API Key
export GOOGLE_API_KEY=xxx        # Google API Key
```

### Global Config

```bash
# Image provider - Nano Banana Pro recommended (gemini)
videoclaw config --global --set models.image.provider=gemini

# Video provider - Seedance 2.0 recommended (volcengine)
videoclaw config --global --set models.video.provider=volcengine
```

### Project Config

```bash
videoclaw config --project my-video --set models.image.provider=gemini
```

### Config Priority

1. Environment variables (highest)
2. Global config `~/.videoclaw/config.yaml`
3. Project config `<project>/.videoclaw/config.yaml`

## Mobile Usage

For mobile, we recommend [Happy](https://github.com/slopus/happy), which can connect to Claude Code on your PC for video creation.

For syncing image and video assets, we recommend Google Drive, iCloud, or Nutstore (Jianguoyun)—all have automatic folder sync to cloud features.

## Development

```bash
# Run tests
pytest

# Code checking
ruff check .
black .
```

## Release New Version

```bash
# 1. Update version (modify version in pyproject.toml)
# 2. Commit changes
git add pyproject.toml && git commit -m "chore: bump version to x.x.x"

# 3. Push to GitHub
git push

# 4. Build and publish to PyPI
uvx --from build pyproject-build
uvx twine upload dist/*
```

## License

MIT
