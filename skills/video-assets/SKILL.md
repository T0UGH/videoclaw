---
name: video-assets
description: Use when user needs to generate character and scene image assets for a video project
---

# video-assets - 资产生成

## 概述
生成角色和场景图片资产。

## 使用方式

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

```bash
videoclaw assets --project my-project
```

## 参数

- `--project, -p`: 项目名称（必填）

## 前置条件

分析结果已在 video-create 时生成，保存在 state.json 中

## 示例

```
Claude Code: videoclaw assets --project mars-video
```
