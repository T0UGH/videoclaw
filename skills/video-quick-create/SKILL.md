---
name: video-quick-create
description: 简化版视频创建流程，一步完成。用于用户想要快速生成视频的场景，跳过图片故事板直接用九宫格资产图生成视频。
---

# video-quick-create

## 触发场景

用户说"做一个xx视频"、"帮我生成一个视频"时触发。

## 输入

用户需要提供：
- 视频主题/想法
- 角色（如有）
- 时长偏好

## 执行流程

### 0. 确认资产图来源

用 AskUserQuestion 询问：
> "你有人物九宫格资产图吗？"

- 有 → 跳过步骤 1，直接用用户图片
- 没有 → 继续步骤 1

如无资产，追问：
> "有人物参考图吗？"

- 有 → I2I 模式
- 没有 → T2I 模式

### 1. 生成九宫格资产

**T2I 模式**:
```bash
videoclaw t2i -p "九宫格角色图：正面、侧面、背面..." -o <project>/assets/character_grid.png
```

**I2I 模式**:
```bash
videoclaw i2i -i <reference.jpg> -p "转换为九宫格角色图" -o <project>/assets/character_grid.png
```

### 2. 生成文本分镜

调用 video-text-storyboard skill 生成结构化文本分镜。

### 3. 生成视频

```bash
videoclaw i2v -p <project> -i <assets/image1.png> -t "镜头1描述" -i <assets/image2.png> -t "镜头2描述"
```

## 交互确认

每步完成后用 AskUserQuestion 询问：
- "满意吗？" → 满意 / 调整 / 重新生成
