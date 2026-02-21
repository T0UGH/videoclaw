---
name: video-audio
description: Use when user needs to generate TTS voice, sound effects, and background music for a video
---

# video-audio - 音频生成

## 概述
生成 TTS 语音、音效和背景音乐。

## 使用方式

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

```bash
videoclaw audio --project my-project
```

## 参数

- `--project, -p`: 项目名称（必填）

## 前置条件

需要先完成 `video:i2v`

## 示例

```
Claude Code: videoclaw audio --project mars-video
```
