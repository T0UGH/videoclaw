# videoclaw

[中文](README.md) | **AI Video Creation CLI + Skill Pack**

## Overview

videoclaw is now intentionally shaped as two layers:

1. **CLI execution layer**: project structure, model calls, artifact persistence
2. **Skill pack workflow layer**: interaction, prompts, templates, and creative flow

The project no longer treats host-native plugins as the main distribution path. The primary distribution model is now:

- install the `videoclaw` CLI
- install the skill pack from the repo `skills/` directory via `skills.sh`

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

## Install Skill Pack (primary path)

The recommended way to install videoclaw workflows is through `skills.sh`:

```bash
npx skills add T0UGH/videoclaw --all
```

Common variants:

```bash
# Local development install from the repo root
npx skills add . --all

# Install a single skill
npx skills add T0UGH/videoclaw --skill video-quick-create

# List installable skills
npx skills add T0UGH/videoclaw --list
```

This is now the main distribution path. The `skills/` directory is the canonical workflow source of truth.

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
- `render/` for the default single-video generation workflow
- `clips/` for multi-segment expansion

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

If you are not using the Codex subscription path, switch to OpenAI or another provider, for example:

```bash
videoclaw config --project my-project --set models.image.backend=openai-image
videoclaw config --project my-project --set models.image.auth=api_key
```

If `OPENAI_API_KEY` is configured, `openai-image` calls the official OpenAI image API directly.

## Video Workflow

### Single-video render flow

Single videos persist artifacts under `videos/<slug>/render/`:

- `input/reference.json`
- `input/prompt.md`
- `candidates/`
- `selected.mp4`
- `task.json`

### Multi-segment flow

Multi-segment videos can use `clips/`:

- `clips/<clip-id>/input/reference.json`
- `clips/<clip-id>/input/prompt.md`
- `clips/<clip-id>/candidates/`
- `clips/<clip-id>/selected.mp4`
- `clips/<clip-id>/task.json`

### Current commands

```bash
videoclaw video create my-project demo-video
videoclaw video list my-project
videoclaw video status my-project demo-video
videoclaw video generate my-project demo-video --prompt "walk forward" --provider mock
videoclaw video select my-project demo-video v001.mp4

videoclaw video clip create my-project demo-video clip-01
videoclaw video clip generate my-project demo-video clip-01 --prompt "turn head" --provider mock
videoclaw video clip select my-project demo-video clip-01 v001.mp4

videoclaw merge --project my-project --output final.mp4
```

## Supported Model Providers / Backends

| Provider / Backend | Image | Video | Audio |
|--------------------|-------|-------|-------|
| volcengine | Seedream | Seedance 2.0 | TTS |
| dashscope | wan2.6-t2i | wan2.6-i2v | cosyvoice-v2 |
| gemini | Nano Banana Pro | - | - |
| openai-image | Official OpenAI image API | - | - |
| codex-host-image | Hermes-style / Codex OAuth-native path | - | - |
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
| `videoclaw video clip create` | Create a clip |
| `videoclaw video clip generate` | Generate a clip candidate |
| `videoclaw video clip select` | Select a clip candidate |
| `videoclaw t2i` | Text-to-image |
| `videoclaw i2i` | Image-to-image |
| `videoclaw image smoke` | Smoke test an image backend |
| `videoclaw i2v` | Image-to-video |
| `videoclaw video-smoke` | Smoke test a video backend |
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

## Notes

- `skills/` is the canonical skill pack and the only workflow source of truth.
- Host-side differences should be absorbed by `skills.sh` installation as much as possible instead of maintaining deep host-native plugin integrations.
- The primary recommended paths have already been smoke-tested for real:
  - Image: `codex-host-image`
  - Video: `volcengine` / Ark / Seedance
