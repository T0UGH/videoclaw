---
name: video-i2i
description: Use when user needs to transform or edit images using AI. Independent image-to-image command for converting reference images to different styles or content.
---

# video-i2i - 图生图

## Overview

Transform or edit images using AI. Independent command for converting reference images to different styles or content.

## Usage

```bash
# Transform image
videoclaw i2i -i input.png -p "转换为九宫格角色图" -o output.png

# Specify provider
videoclaw i2i -i input.png -p "描述" -o output.png --provider volcengine

# Specify model
videoclaw i2i -i input.png -p "描述" -o output.png --provider gemini --model gemini-3-pro-image-preview
```

## Parameters

- `--input, -i`: Input image path (required)
- `--prompt, -p`: Transformation prompt (required)
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
Claude Code: videoclaw i2i -i reference.jpg -p "转换为九宫格角色图" -o character_grid.png
```
