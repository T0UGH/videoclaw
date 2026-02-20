---
name: video-analyze
description: Use when user provides a script or description and needs to extract characters, scenes, props, and storyboard frames
---

# video-analyze - 脚本分析

## 概述
分析用户提供的脚本或描述，提取角色、场景、道具和故事板帧。

## 使用方式

```bash
videoclaw analyze --script "故事内容..." --project my-project
```

## 参数

- `--script, -s`: 脚本/故事内容（必填）
- `--project, -p`: 项目名称（必填）

## 输出

生成 JSON 包含：
- characters: 角色列表（名字、描述、服装等）
- scenes: 场景列表（名称、描述、时间等）
- props: 道具列表
- frames: 故事板帧列表（动作、对话、镜头等）

## 示例

```
用户: 分析这个故事：宇航员在火星发现外星人基地

Claude Code: videoclaw analyze --script "宇航员在火星发现外星人基地" --project mars-video

输出:
{
  "characters": [
    {"name": "宇航员", "description": "身穿宇航服的宇航员"}
  ],
  "scenes": [
    {"name": "火星表面", "description": "红色的火星荒原"}
  ],
  "frames": [...]
}
```
