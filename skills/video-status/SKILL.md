---
name: video-status
description: Use when user wants to check the progress and status of a video project
---

# video-status - 查看项目状态

## 概述
查看当前项目的进度和状态。

## 使用方式

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

```bash
videoclaw status --project my-project
```

## 输出

- 项目名称
- 当前状态
- 各步骤状态（pending/in_progress/completed/failed）

## 示例

```
Claude Code: videoclaw status --project mars-video

输出:
项目: mars-video
状态: generating_video

步骤状态:
  analyze: completed
  assets: completed
  storyboard: completed
  i2v: in_progress
  audio: pending
  merge: pending
```
