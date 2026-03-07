# video-text-storyboard 优化实施计划

> **For Claude:** Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 优化 video-text-storyboard 和 video-quick-create 中的分镜生成模板，输出专业的结构化分镜

**Architecture:** 将分镜模板移到 references/stories.md，实现故事类分镜的标准化输出

---

### Task 1: 创建 references/stories.md 模板文件

**Files:**
- Create: `skills/video-text-storyboard/references/stories.md`

**Step 1: 创建目录和文件**

```bash
mkdir -p skills/video-text-storyboard/references
touch skills/video-text-storyboard/references/stories.md
```

**Step 2: 写入模板内容**

```markdown
# 故事类分镜模板

## 模板结构

【素材介绍】：
【图1】<角色/物体描述>
【图2】<角色/物体描述>
【图3】<角色/物体描述>

【场景描写】：
<整体背景描述，可选>

【背景音】：
<整体背景音描述，可选>

【分镜】：
【镜头标题】（X-Y秒）
画面：<包含动作、台词、情绪的完整描述>
音效：<此镜头的音效>

【镜头标题】（X-Y秒）
画面：...
音效：...

【注意事项】：
- 角色设定：<关键角色特征>
- 氛围：<整体氛围要求>
- 动作节奏：<节奏要求>
- 细节还原：<关键细节>
```

**Step 3: 添加完整示例**

写入用户提供的冰霜王分镜示例

---

### Task 2: 更新 video-text-storyboard SKILL.md

**Files:**
- Modify: `skills/video-text-storyboard/SKILL.md`

**Step 1: 更新生成要点**

在"生成要点"部分添加新的模板说明

**Step 2: 更新示例**

替换为新的结构化示例

**Step 3: 添加引用说明**

说明使用 references/stories.md 中的模板

---

### Task 3: 同步更新 video-quick-create 分镜部分

**Files:**
- Modify: `skills/video-quick-create/SKILL.md`

**Step 1: 更新文本分镜 prompt**

在 Step 3 中使用新的分镜模板格式

**Step 2: 更新 Seedance 2.0 提示词格式参考**

使用新的结构化格式

---

### Task 4: 验证

**Step 1: 测试生成**

使用新模板生成分镜，确认格式正确

**Step 2: 提交**

```bash
git add skills/video-text-storyboard/ skills/video-quick-create/
git commit -m "feat: 优化分镜模板为结构化格式"
```
