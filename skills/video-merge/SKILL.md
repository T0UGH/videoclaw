---
name: video-merge
description: Use when user needs to merge video clips, add audio, and generate the final video
---

# video-merge - 视频合并

## 概述
合并视频片段，添加音频，生成最终视频。

## 使用方式

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

```bash
videoclaw merge --project my-project
```

## 参数

- `--project, -p`: 项目名称（必填）

## 前置条件

需要先完成 `video:audio`

## 示例

```
Claude Code: videoclaw merge --project mars-video
```
