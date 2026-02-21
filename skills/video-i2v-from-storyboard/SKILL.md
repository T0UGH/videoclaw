---
name: video-i2v-from-storyboard
description: Use when user needs to convert storyboard images into video clips (requires storyboard step completed)
---

# video-i2v-from-storyboard - 从故事板生成视频

## 概述

从 storyboard 步骤生成的图片转换为视频片段。

## 使用方式

```bash
videoclaw i2v-from-storyboard --project my-project
```

## 参数

- `--project, -p`: 项目名称（必填）
- `--provider`: 模型提供商（可选）
- `--resolution, -r`: 分辨率（可选）

## 前置条件

需要先完成 `video:storyboard`

## 示例

```
Claude Code: videoclaw i2v-from-storyboard --project mars-video
```
