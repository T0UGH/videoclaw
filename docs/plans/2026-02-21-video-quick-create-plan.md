# video-quick-create 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement.

**Goal:** 创建 video-quick-create、video-text-storyboard skill，重命名 video-create 为 video-standard-create

**Architecture:** 新增两个 skill 文件，复用现有 CLI 命令

**Tech Stack:** Skill（Claude Code）, Gemini T2I/I2I, 火山 i2v

---

## 任务列表

### Task 1: 重命名 video-create 为 video-standard-create

**Files:**
- Create: `skills/video-standard-create/SKILL.md`
- Delete: `skills/video-create/SKILL.md`
- Delete: `skills/video-create/` 目录

**Step 1: 复制现有 skill 文件**

```bash
cp -r skills/video-create skills/video-standard-create
```

**Step 2: 修改 SKILL.md 标题**

将文件开头的 `name: video-create` 改为 `name: video-standard-create`

**Step 3: 删除旧的 skill**

```bash
rm -rf skills/video-create
```

**Step 4: Commit**

```bash
git add skills/video-standard-create/ skills/video-create/
git commit -m "refactor: rename video-create to video-standard-create"
```

---

### Task 2: 创建 video-text-storyboard skill

**Files:**
- Create: `skills/video-text-storyboard/SKILL.md`

**Step 1: 创建 skill 目录**

```bash
mkdir -p skills/video-text-storyboard
```

**Step 2: 编写 SKILL.md**

```markdown
---
name: video-text-storyboard
description: 使用 AI 生成文本形式的视频分镜描述，直接用于视频生成
---

# video-text-storyboard - 文本分镜生成

## 概述

根据用户描述的视频想法，生成结构化的文本分镜，直接作为视频生成的输入。

## 输入

用户描述视频想法，例如：
- "做一个Q版小怪兽打篮球的搞笑视频"
- "宇航员在火星上发现外星遗迹"

## 输出格式

```
创意要点
• 视频主题：...
• 核心内容：...
• 视觉风格：...
• 画面构图：...
• 人物设定：...
• 视频设置：...

剧本内容（X s）

剧情梗概：...

镜头1：...
镜头2：...
```

## 实现方式

使用 Claude API 生成文本分镜。

## 交互确认

生成后展示给用户，用户可以修改或确认。
```

**Step 3: Commit**

```bash
git add skills/video-text-storyboard/
git commit -m "feat: add video-text-storyboard skill"
```

---

### Task 3: 创建 video-quick-create skill

**Files:**
- Create: `skills/video-quick-create/SKILL.md`

**Step 1: 创建 skill 目录**

```bash
mkdir -p skills/video-quick-create
```

**Step 2: 编写 SKILL.md**

```markdown
---
name: video-quick-create
description: 快速创建视频，一步完成所有流程
---

# video-quick-create - 快速创建视频

## 概述

简化版视频生成流程，用户描述想法后自动完成：
1. 生成九宫格角色资产图（T2I/I2I）
2. 生成文本分镜 (video-text-storyboard)
3. 生成视频 (火山 i2v)

每步都需用户确认后继续。

## 使用方式

用户只需要描述想要创建的视频：
> "帮我做一个Q版小怪兽打篮球的搞笑视频"

## 执行流程

### 1. 资产生成（九宫格）

两种模式：
- **T2I 模式**：用户文字描述 → AI 生成九宫格
- **I2I 模式**：用户提供参考图 → AI 转换成九宫格

九宫格内容：
- 正面、侧面、背面
- 面部特写
- 表情变化
- 3/4 侧面、上面
- 服装
- 武器特写（如有）

生成后展示给用户，满意则继续，不满意可修改后重新生成。

### 2. 文本分镜

调用 video-text-storyboard 生成文字分镜，展示给用户确认。

### 3. i2v 生成视频

使用角色资产图 + 文字分镜调用火山 i2v 生成视频，展示给用户确认。

## 与 video-standard-create 的区别

| 特性 | standard-create | quick-create |
|------|----------------|--------------|
| 资产图 | 多张候选让用户选 | 九宫格，直接用于 i2v |
| 分镜 | 图片故事板 | 文本分镜 |
| 交互 | 多轮交互确认 | 每步确认后继续 |
| 速度 | 慢 | 快 |
```

**Step 3: Commit**

```bash
git add skills/video-quick-create/
git commit -m "feat: add video-quick-create skill"
```

---

## 执行顺序

1. Task 1: 重命名 video-create → video-standard-create
2. Task 2: 创建 video-text-storyboard
3. Task 3: 创建 video-quick-create
