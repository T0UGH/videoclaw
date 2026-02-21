---
name: video-i2v
description: Use when user needs to convert images into video clips with custom prompts
---

# video-i2v - 图生视频（通用模式）

## 概述

将图片转换为视频片段，支持自定义 prompt。

## 使用方式

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

```bash
# 一张图片生成一个视频
videoclaw i2v --project my-project -i image.png -t "角色向前行走"

# 多张图片生成多个视频（用同一个 prompt）
videoclaw i2v --project my-project -i image1.png -i image2.png -t "角色向前行走"
```

## 参数

- `--project, -p`: 项目名称（必填）
- `--image, -i`: 图片路径（必填，每张图片生成一个视频）
- `--prompt, -t`: 传给视频模型的 prompt（必填，生成视频的指令）
- `--provider`: 模型提供商（可选）
- `--resolution, -r`: 分辨率（可选）

## 示例

```
Claude Code: videoclaw i2v --project mars-video -i assets/frame1.png -t "角色向前行走"
```
