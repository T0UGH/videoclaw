---
name: video-t2i
description: Use when user needs to generate images from text prompts. Independent text-to-image command for creating single images outside of video creation workflow.
---

# video-t2i - 文生图

## Overview

Generate images from text prompts. Independent command that does not require project context.

## Usage

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

```bash
# Generate image
videoclaw t2i -p "九宫格角色图：正面、侧面、背面..." -o output.png

# Specify provider
videoclaw t2i -p "描述" -o output.png --provider volcengine

# Specify model
videoclaw t2i -p "描述" -o output.png --provider gemini --model gemini-3-pro-image-preview
```

## Parameters

- `--prompt, -p`: Text prompt (required)
- `--output, -o`: Output file path (required)
- `--provider`: Model provider (optional, default: volcengine)
- `--model`: Model name (optional)

## Supported Providers

- `volcengine` - Volcano Engine Seedream (default)
- `dashscope` - Alibaba Wan2.6
- `gemini` - Google Gemini
- `mock` - For testing

## Examples

```
Claude Code: videoclaw t2i -p "一个可爱的小黄人角色，正面视图" -o character.png
```
