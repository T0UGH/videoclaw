---
name: video-preview
description: Use when user wants to preview images or videos
---

# video-preview - 预览

## 概述
预览图片或视频。

## 使用方式

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

```bash
videoclaw preview <file_path> --project my-project
```

## 参数

- `file_path`: 文件路径（必填）
- `--project, -p`: 项目名称（可选）

## 示例

```
Claude Code: videoclaw preview videos/final.mp4 --project mars-video
```
