---
name: video:preview
description: 预览图片或视频
allowed-tools: Bash(videoclaw:*), Read
---

# video:preview - 预览

## 概述
预览图片或视频。

## 使用方式

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
