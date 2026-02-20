---
name: video:audio
description: 生成 TTS 语音、音效和背景音乐
allowed-tools: Bash(videoclaw:*)
---

# video:audio - 音频生成

## 概述
生成 TTS 语音、音效和背景音乐。

## 使用方式

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
