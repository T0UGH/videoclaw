---
name: video:assets
description: 生成角色和场景图片资产
allowed-tools: Bash(videoclaw:*)
---

# video:assets - 资产生成

## 概述
生成角色和场景图片资产。

## 使用方式

```bash
videoclaw assets --project my-project
```

## 参数

- `--project, -p`: 项目名称（必填）

## 前置条件

需要先完成 `video:analyze`

## 示例

```
Claude Code: videoclaw assets --project mars-video
```
