---
name: video-init
description: Use when user wants to initialize a new video project with directory structure
---

# video-init - 初始化项目

## 概述

初始化新的视频项目，创建目录结构。**交互确认在 skill 层通过 AskUserQuestion 实现**。

## 触发条件

用户说"创建一个新项目"、"初始化项目"或类似表达时触发。

## 交互流程

### Step 1: 询问项目名称

用 AskUserQuestion 询问：
> "请给项目起个名字？"

### Step 2: 询问图像生成提供商

```
选项:
1) volcengine (火山引擎 Seedream)
2) dashscope (阿里云)
3) gemini (Google)
4) mock (测试用)
```

### Step 3: 询问视频生成提供商

```
选项:
1) volcengine (火山引擎 Seedance)
2) dashscope (阿里云 Wan2.6)
3) mock (测试用)
```

### Step 4: 询问存储方式

```
选项:
1) local (本地存储)
2) google_drive (上传到 Google Drive)
```

## 执行流程

1. 用 AskUserQuestion 依次收集配置（项目名称、图像提供商、视频提供商、存储方式）
2. 调用 `videoclaw init <project-name>` 创建项目
3. 用 `videoclaw config --project <name> --set` 设置项目配置

```bash
# 示例执行
videoclaw init my-video
videoclaw config --project my-video --set models.image.provider=volcengine
videoclaw config --project my-video --set models.video.provider=volcengine
videoclaw config --project my-video --set storage.provider=google_drive
```

## 创建的目录

- `.videoclaw/` - 配置和状态文件
- `assets/` - 角色和场景图片
- `storyboard/` - 故事板帧图片
- `videos/` - 生成的视频片段
- `audio/` - 音频文件

## 参数

- `project_name`: 项目名称（必填）
- `--dir`: 项目目录路径（可选，默认 ~/videoclaw-projects）

## 全局配置（可选）

用户也可以先设置全局配置，新项目会自动使用：

```bash
# 设置全局默认提供商
videoclaw config --set models.image.provider=volcengine
videoclaw config --set models.video.provider=volcengine
videoclaw config --set storage.provider=google_drive
```

## 示例

```
用户: 帮我创建一个新项目

Claude Code:
  - 询问项目名称
  - 询问图像提供商（volcengine/dashscope/gemini/mock）
  - 询问视频提供商（volcengine/dashscope/mock）
  - 询问存储方式（local/google_drive）
  - 执行: videoclaw init my-video
  - 执行: videoclaw config --project my-video --set models.image.provider=xxx
  - 执行: videoclaw config --project my-video --set models.video.provider=xxx
  - 执行: videoclaw config --project my-video --set storage.provider=xxx
```
