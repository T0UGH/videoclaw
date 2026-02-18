# Phase 4: Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 创建给 Claude Code 使用的 Skills，帮助 Claude Code 调用 videoclaw CLI 完成视频创建工作流

**Architecture:** Skills 是 Markdown 格式的提示词，定义在项目内的 skills/ 目录

**Tech Stack:** Markdown

---

## Task 1: 创建 skills 目录结构

**Files:**
- Create: `skills/README.md`
- Create: `skills/video:create.md`

**Step 1: 创建 skills 目录**

```bash
mkdir -p skills
```

**Step 2: 创建 skills README**

```markdown
# Videoclaw Skills

给 Claude Code 使用的技能集合。

## 安装

```bash
# 将 skills 复制到 Claude Code 的 skills 目录
cp -r skills/* ~/.claude/skills/
```

## 技能列表

- `video:create` - 一句话创建完整视频
- `video:init` - 初始化项目
- `video:status` - 查看项目状态
```

**Step 3: Commit**

```bash
git add skills/
git commit -m "feat: 添加 skills 目录结构"
```

---

## Task 2: video:create 主技能

**Files:**
- Create: `skills/video:create.md`

**Step 1: 创建 video:create 技能**

```markdown
# video:create - 创建视频

## 概述
一句话创建完整视频，自动执行所有步骤。

## 使用方式

用户只需要描述想要创建的视频：
> "帮我做一个关于宇航员在火星上发现外星遗迹的短视频"

## 执行流程

1. 调用 `videoclaw init <project-name>` 初始化项目
2. 调用 `videoclaw analyze --script "<用户描述>" --project <project-name>` 分析脚本
3. 调用 `videoclaw assets --project <project-name>` 生成资产
4. 调用 `videoclaw storyboard --project <project-name>` 生成故事板
5. 调用 `videoclaw i2v --project <project-name>` 图生视频
6. 调用 `videoclaw audio --project <project-name>` 生成音频
7. 调用 `videoclaw merge --project <project-name>` 合并视频

## 状态检查

每步完成后检查 `videoclaw status --project <project-name>` 确认状态。

## 错误处理

如果某一步失败：
1. 查看日志了解错误原因
2. 尝试重新执行该步骤
3. 如需跳过，可以手动调用后续步骤
4. 失败超过 2 次后，将问题报告给用户

## 示例

```
用户: 做一个宇航员在火星的视频

Claude Code:
1. videoclaw init mars-video
2. videoclaw analyze --script "宇航员在火星上发现外星遗迹" --project mars-video
3. videoclaw assets --project mars-video
4. videoclaw storyboard --project mars-video
5. videoclaw i2v --project mars-video
6. videoclaw audio --project mars-video
7. videoclaw merge --project mars-video
```

## 配置

如需配置模型提供商，可以在项目配置中设置：

```bash
videoclaw config --project mars-video --set models.image.provider=dashscope
videoclaw config --project mars-video --set models.video.provider=volcengine
```
```

**Step 2: Commit**

```bash
git add skills/
git commit -m "feat: 添加 video:create 技能"
```

---

## Task 3: video:init 技能

**Files:**
- Create: `skills/video:init.md`

**Step 1: 创建 video:init 技能**

```markdown
# video:init - 初始化项目

## 概述
初始化新的视频项目，创建目录结构。

## 使用方式

```bash
videoclaw init my-project
```

## 创建的目录

- `.videoclaw/` - 配置和状态文件
- `assets/` - 角色和场景图片
- `storyboard/` - 故事板帧图片
- `videos/` - 生成的视频片段
- `audio/` - 音频文件

## 参数

- `project_name`: 项目名称（必填）

## 示例

```
用户: 创建一个新项目

Claude Code: videoclaw init my-video-project
```
```

**Step 2: Commit**

```bash
git add skills/
git commit -m "feat: 添加 video:init 技能"
```

---

## Task 4: video:analyze 技能

**Files:**
- Create: `skills/video:analyze.md`

**Step 1: 创建 video:analyze 技能**

```markdown
# video:analyze - 脚本分析

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
```

**Step 2: Commit**

```bash
git add skills/
git commit -m "feat: 添加 video:analyze 技能"
```

---

## Task 5: video:status 技能

**Files:**
- Create: `skills/video:status.md`

**Step 1: 创建 video:status 技能**

```markdown
# video:status - 查看项目状态

## 概述
查看当前项目的进度和状态。

## 使用方式

```bash
videoclaw status --project my-project
```

## 输出

- 项目名称
- 当前状态
- 各步骤状态（pending/in_progress/completed/failed）

## 示例

```
Claude Code: videoclaw status --project mars-video

输出:
项目: mars-video
状态: generating_video

步骤状态:
  analyze: completed
  assets: completed
  storyboard: completed
  i2v: in_progress
  audio: pending
  merge: pending
```
```

**Step 2: Commit**

```bash
git add skills/
git commit -m "feat: 添加 video:status 技能"
```

---

## Task 6: 其他子技能（简化版）

**Files:**
- Create: `skills/video:assets.md`
- Create: `skills/video:storyboard.md`
- Create: `skills/video:i2v.md`
- Create: `skills/video:audio.md`
- Create: `skills/video:merge.md`
- Create: `skills/video:preview.md`
- Create: `skills/video:config.md`

**Step 1: 创建简化版子技能**

每个子技能包含：
- 概述
- 使用方式
- 参数
- 示例

示例（video:assets.md）:

```markdown
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
```

**Step 2: Commit**

```bash
git add skills/
git commit -m "feat: 添加其他子技能"
```

---

## 下一步

Skills 完成后，可以开始实现具体的厂商后端（DashScope、VolcEngine 等）。
