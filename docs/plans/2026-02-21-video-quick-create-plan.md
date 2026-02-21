# video-quick-create 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or executing-plans to implement.

**Goal:** 创建简化版视频生成流程：用户描述想法 → AI 生成文本分镜 → 图片 → 视频

**Architecture:** 新增 video-text-storyboard 和 video-quick-create 两个 skill，复用现有 CLI 命令

**Tech Stack:** Skill（Claude Code）, Gemini T2I, 火山 i2v

---

## 任务列表

### Task 1: 重命名 video-create 为 video-standard-create

**Files:**
- Create: `skills/video-standard-create/SKILL.md` (从 video-create 复制)
- Delete: `skills/video-create/SKILL.md`
- Delete: `skills/video-create/` 目录

**Step 1: 复制现有 skill 文件**

```bash
cp -r skills/video-create skills/video-standard-create
```

**Step 2: 修改 SKILL.md 标题**

将 `video-create` 改为 `video-standard-create`

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

**Step 1: 创建 skill 目录和文件**

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

使用 Claude API（或项目配置的 LLM）生成文本分镜。

## 示例

输入：Q版小怪兽打篮球

输出：
```
创意要点
• 视频主题：Q版小怪兽与精英运动员的跨次元篮球对决
• 核心内容：...
• 视觉风格：...
...

剧本内容（13s）

镜头1：...
镜头2：...
```
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

**Step 1: 创建 skill 目录和文件**

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
1. 生成文本分镜 (video-text-storyboard)
2. 生成图片 (Gemini T2I)
3. 生成视频 (火山 i2v)

## 使用方式

用户只需要描述想要创建的视频：
> "帮我做一个Q版小怪兽打篮球的搞笑视频"

## 执行流程

1. 调用 `videoclaw init <project-name>` 初始化项目
2. 解析用户输入，提取关键信息
3. 调用 video-text-storyboard 生成文本分镜
4. 根据文本分镜生成关键帧图片（Gemini）
5. 调用火山 i2v 生成视频
6. 输出最终视频

## 与 video-standard-create 的区别

| 特性 | standard-create | quick-create |
|------|----------------|--------------|
| 交互 | 多轮交互确认 | 一次性生成 |
| 图片 | 多张候选 | 1张直接输出 |
| 分镜 | 图片故事板 | 文本分镜 |
```

**Step 3: Commit**

```bash
git add skills/video-quick-create/
git commit -m "feat: add video-quick-create skill"
```

---

### Task 4: 更新文档（如需要）

**Files:**
- Modify: `CLAUDE.md` (可选)

如果需要更新项目文档说明新的 skill 结构。

---

## 执行顺序

1. Task 1: 重命名 video-create → video-standard-create
2. Task 2: 创建 video-text-storyboard
3. Task 3: 创建 video-quick-create
4. Task 4: 更新文档（可选）

---

## 备注

- 这是一个 skill 层面的任务，不涉及 CLI 代码修改
- 复用现有 CLI 命令 (t2i, i2v)
- 所有交互在 skill 层处理
