# videoclaw

[中文](README.md) | **AI Video Creation CLI | Host-Neutral Skill Pack + CLI**

## Overview

videoclaw is an AI video creation CLI focused on splitting the product into three layers:

- **CLI execution layer**: project structure, model calls, artifact persistence
- **Skill pack workflow layer**: interaction, prompts, templates, creative flow
- **Host adapter layer**: connect the same CLI + skills to different hosts

The recommended paths are now:

- **Default image path**: `codex-host-image` (if you already have Codex / ChatGPT login available)
- **High-quality image path**: Gemini
- **Default video path**: Seedance 2.0

In other words, videoclaw now prioritizes “if you already have a Codex subscription, you can generate images through that path” as the default user experience, while still keeping other providers and the host-neutral architecture direction.

## Install CLI

### Method 1: uvx (recommended)

```bash
uvx videoclaw --help
```

### Method 2: pip

```bash
pip install videoclaw
```

### Method 3: development mode

```bash
git clone https://github.com/T0UGH/videoclaw.git
cd videoclaw
pip install -e .
```

### Optional environment variables

```bash
export ARK_API_KEY=your-ark-api-key
export DASHSCOPE_API_KEY=your-api-key
export GOOGLE_API_KEY=your-api-key
export OPENAI_API_KEY=your-api-key
```

## Install Skill Pack / Host Adapter

videoclaw distribution is now split into two layers:

1. **CLI**: standard Python package (`uvx` / `pip`)
2. **Skill pack / host adapter**: installed per host

### Claude Code adapter

Claude Code can still install the adapter via marketplace:

```bash
/claude install marketplace https://github.com/T0UGH/videoclaw/raw/main/.claude-plugin/marketplace.json
```

This marketplace entry should now be understood as the **Claude Code adapter**, not the only distribution center for videoclaw.

### Other hosts

The long-term direction is to make `skills/` the canonical skill pack and provide thin adapters per host:

- Claude Code adapter
- OpenClaw adapter (priority target)
- Hermes adapter (directory-based first)
- Codex runtime / host capability adapter

## Quick Start

```bash
# Initialize a project
videoclaw init my-project

# Create a video unit inside the project
videoclaw video create my-project demo-video

# List videos inside the project
videoclaw video list my-project
```

## New Project / Video Model

videoclaw now uses:

- one `project` for shared assets and multiple videos
- one `video` as an independent production unit
- `render/` for single-video generation workflow by default
- optional `clips/` for future multi-segment expansion

Recommended structure:

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

## Image Backends

Image generation now has two formal paths:

- `codex-host-image`: Hermes-style / OAuth-native Codex image provider (default recommendation)
- `openai-image`: official OpenAI API provider

If you already have Codex / ChatGPT login available, use:

```bash
videoclaw config --project my-project --set models.image.backend=codex-host-image
videoclaw config --project my-project --set models.image.model=gpt-image-2-medium
videoclaw config --project my-project --set models.image.auth=chatgpt_login
videoclaw config --project my-project --set models.image.transport=codex_oauth
```

Supported Codex image model tiers:

- `gpt-image-2-low`
- `gpt-image-2-medium`
- `gpt-image-2-high`

Recommended default: `gpt-image-2-medium`

If you are not using the Codex subscription path, switch to the OpenAI provider:

```bash
videoclaw config --project my-project --set models.image.backend=openai-image
videoclaw config --project my-project --set models.image.auth=api_key
```

If `OPENAI_API_KEY` is configured, `openai-image` calls the official OpenAI image API directly.

## Video Workflow

### Single-video render flow

Single videos now persist artifacts under `videos/<slug>/render/`:

- `input/reference.json`
- `input/prompt.md`
- `candidates/`
- `selected.mp4`
- `task.json`

### Current CLI skeleton

```bash
videoclaw video create my-project demo-video
videoclaw video list my-project
videoclaw video status my-project demo-video
videoclaw video generate my-project demo-video --prompt "walk forward" --provider mock
videoclaw video select my-project demo-video v001.mp4
```

## Supported Model Providers / Backends

| Provider / Backend | Image | Video | Audio |
|--------------------|-------|-------|-------|
| volcengine | Seedream | Seedance 2.0 | TTS |
| dashscope | wan2.6-t2i | wan2.6-i2v | cosyvoice-v2 |
| gemini | Nano Banana Pro | - | - |
| openai-image | planned / in progress | - | - |
| codex-host-image | host-adapter path | - | - |
| mock | testing | testing | testing |

## Skills

All video creation workflows live in the `skills/` directory as the canonical skill pack. Current skills include:

- `video-quick-create`
- `video-text-storyboard`
- `video-t2i`
- `video-i2i`
- `video-i2v`
- `video-audio`
- `video-merge`
- `video-config`
- `video-upload`
- `video-publish-douyin`
- `video-publish-kuaishou`

## CLI Commands

| Command | Description |
|---------|-------------|
| `videoclaw init` | Initialize a project |
| `videoclaw video create` | Create a video |
| `videoclaw video list` | List videos |
| `videoclaw video status` | Show video status |
| `videoclaw video generate` | Generate a single-video candidate |
| `videoclaw video select` | Select a single-video candidate |
| `videoclaw t2i` | Text-to-image |
| `videoclaw i2i` | Image-to-image |
| `videoclaw i2v` | Image-to-video |
| `videoclaw audio` | Generate audio |
| `videoclaw merge` | Merge videos |
| `videoclaw config` | Configuration management |
| `videoclaw upload` | Cloud upload |
| `videoclaw preview` | Preview files |
| `videoclaw publish` | Publish to social platforms (optional dependency) |

## Configuration

See [docs/configuration.md](docs/configuration.md) for the full configuration reference.

Priority order:

1. Environment variables
2. Global config `~/.videoclaw/config.yaml`
3. Project config `<project>/.videoclaw/config.yaml`

## Development

```bash
pytest
ruff check .
black .
```
