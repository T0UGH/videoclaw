# video-quick-create Seedance 2.0 改造实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement.

**Goal:** 改造 video-quick-create 工作流，全面适配 Seedance 2.0 的多模态输入能力和结构化提示词格式。

**Architecture:**
1. 重写 video-quick-create skill（4步流程）
2. 增强 i2v 命令支持多图 + 视频 + 音频输入

**Tech Stack:** Skill（Claude Code）, Click (CLI), Python

---

## Task 1: 创建故事大纲 prompt 模板

**Files:**
- Modify: `docs/plans/2026-02-22-video-quick-create-seedance2-design.md`

**Step 1: 添加故事大纲 prompt 模板**

在设计文档中添加：

```markdown
### 故事大纲 prompt 模板

用户描述视频想法后，使用以下 prompt 生成故事大纲：

```
你是一个专业的视频策划专家。请根据用户的想法生成一个简化的故事大纲。

用户想法：<用户输入>

请生成以下格式的故事大纲：

【视频主题】一句话概括视频核心内容

【核心剧情】2-3句话描述视频的主要情节

【角色设定】
- 角色1：描述（包括外貌、性格）
- 角色2：描述
（如果没有明确角色，可省略）

【时长】X秒（默认15秒）

【风格偏好】用户指定的风格，如果没有则留空
```

```

**Step 2: Commit**

```bash
git add docs/plans/2026-02-22-video-quick-create-seedance2-design.md
git commit -m "docs: add story outline prompt template to design doc"
```

---

## Task 2: 创建素材需求推断 prompt 模板

**Files:**
- Modify: `docs/plans/2026-02-22-video-quick-create-seedance2-design.md`

**Step 1: 添加素材需求推断 prompt 模板**

```markdown
### 素材需求推断 prompt 模板

根据故事大纲推断需要哪些素材：

```
基于以下故事大纲，分析需要哪些素材：

故事大纲：
<故事大纲内容>

请列出：

【角色素材】
- 需要几个角色？
- 每个角色需要什么类型的图片？（正面、侧面、背面、特写等）

【场景素材】
- 需要什么场景？
- 是否需要背景图？

【参考素材】（可选）
- 是否需要视频参考？（运镜/动作）
- 是否需要音频参考？（配乐/对白）

请用清晰的列表格式回复。
```

```

**Step 2: Commit**

```bash
git add docs/plans/2026-02-22-video-quick-create-seedance2-design.md
git commit -m "docs: add material requirements inference prompt template"
```

---

## Task 3: 重写 video-quick-create skill

**Files:**
- Modify: `skills/video-quick-create/SKILL.md`

**Step 1: 备份并重写 SKILL.md**

将现有 SKILL.md 替换为新版本：

```markdown
---
name: video-quick-create
description: 快速创建视频，全面拥抱 Seedance 2.0。一步完成：故事大纲 → 素材准备 → 文本分镜 → i2v 生成视频。
---

# video-quick-create

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

## 触发场景

用户说"做一个xx视频"、"帮我生成一个视频"时触发。

## 流程概览

```
1. 故事大纲（用户描述 → AI 整理）
2. 素材准备（AI 推断需求 → 用户确认 → 素材处理）
3. 文本分镜（Seedance 2.0 格式）
4. i2v 生成视频
```

## 详细流程

### Step 1: 故事大纲

用 AskUserQuestion 询问用户：
> "请描述你想做的视频想法（如：宇航员在火星上发现外星遗迹）"
> - 用户输入想法

使用以下 prompt 生成故事大纲：

```
你是一个专业的视频策划专家。请根据用户的想法生成一个简化的故事大纲。

用户想法：<用户输入>

请生成以下格式的故事大纲：

【视频主题】一句话概括视频核心内容

【核心剧情】2-3句话描述视频的主要情节

【角色设定】
- 角色1：描述（包括外貌、性格）
- 角色2：描述
（如果没有明确角色，可省略）

【时长】X秒（默认15秒）

【风格偏好】用户指定的风格，如果没有则留空
```

生成后用 AskUserQuestion 询问：
> "故事大纲如下，满意吗？"
> - 满意 → 继续 Step 2
> - 调整 → 询问具体要改什么

### Step 2: 素材准备

#### 2.1 推断素材需求

根据故事大纲推断需要哪些素材：

```
基于以下故事大纲，分析需要哪些素材：

故事大纲：
<故事大纲内容>

请列出：

【角色素材】
- 需要几个角色？
- 每个角色需要什么类型的图片？

【场景素材】
- 需要什么场景？
- 是否需要背景图？

【参考素材】（可选）
- 是否需要视频参考？（运镜/动作）
- 是否需要音频参考？（配乐/对白）

请用清晰的列表格式回复。
```

#### 2.2 用户确认素材

用 AskUserQuestion 询问：
> "根据故事大纲，建议准备以下素材：
> - 角色：xxx
> - 场景：xxx
> - 参考视频：可选
> - 参考音频：可选
>
> 你有这些素材吗？需要补充什么？"
> - 确认现有素材
> - 添加新素材
> - 跳过某些素材

#### 2.3 素材处理

对于每个需要的素材：

**角色图**：
- 用户提供 → 跳过生成
- 无参考图 → T2I 模式生成
- 有参考图 → I2I 模式生成

**场景图**：
- 用户提供 → 跳过
- 需要生成 → T2I 模式

生成后用 AskUserQuestion 确认：
> "素材已准备好，满意吗？"

### Step 3: 文本分镜

使用 Seedance 2.0 格式生成文本分镜：

```
基于以下故事大纲和素材，生成 Seedance 2.0 格式的文本分镜提示词。

故事大纲：
<故事大纲内容>

素材：
- 角色图：<路径>
- 场景图：<路径>
- 参考视频：<路径>（如有）
- 参考音频：<路径>（如有）

请生成以下格式：

【风格】<风格>，<时长>秒，<比例>，<氛围>

【时间轴】
0-X秒：[镜头] + [画面] + [动作] + [特效]
...

【声音】<配乐> + <音效> + <对白>

【参考】
@图片1 <角色/场景描述>
@图片2 <角色/场景描述>
@视频1 <运镜/动作参考>（如有）
@音频1 <配乐参考>（如有）

注意：
- 写意图、不写细节
- 每个镜头只安排一个简单动作
- 使用 @图片N、@视频N、@音频N 引用素材
- 10秒以上使用分时段描述
```

生成后用 AskUserQuestion 确认：
> "文本分镜如下，满意吗？"
> - 满意 → 继续 Step 4
> - 调整 → 询问具体要改什么

### Step 4: i2v 生成视频

执行 i2v 命令：

```bash
videoclaw i2v -p <project> \
  -i <角色图> \
  -i <场景图> \
  --video-ref <参考视频> \
  --audio-ref <参考音频> \
  -t "<文本分镜内容>"
```

生成后用 AskUserQuestion 询问：
> "视频已生成，满意吗？"
> - 满意 → 结束
> - 重新生成 → 重试
> - 调整 → 修改后重试

## Seedance 2.0 提示词格式参考

```
【风格】电影级写实，15秒，16:9，温馨治愈

【时间轴】
0-3秒：全景镜头，阳光明媚的小镇广场，主人公走入画面
3-6秒：中景，主人公停下脚步，环顾四周
6-10秒：特写，主人公表情惊讶，发现神秘遗迹
10-15秒：远景，遗迹发出光芒，镜头拉远

【声音】舒缓的钢琴配乐 + 神秘音效

【参考】
@图片1 主人公形象
@图片2 遗迹场景
```

## 常见错误

❌ 引用模糊：不要只写"参考@视频1"，必须说明参考什么（运镜？动作？特效？）

✅ 明确引用：参考 @视频1 的运镜效果，参考 @视频2 的动作编排

---

❌ 内容过载：4-5秒内塞入太多场景

✅ 精简内容：一个镜头只安排一个简单动作

---

❌ 忽视音频：音效设计能大幅提升质量

✅ 加入声音：背景音乐 + 音效 + 对白
```

**Step 2: Commit**

```bash
git add skills/video-quick-create/SKILL.md
git commit -m "feat: rewrite video-quick-create skill for seedance2.0"
```

---

## Task 4: 增强 i2v 命令支持多模态输入

**Files:**
- Modify: `videoclaw/cli/commands/i2v.py`
- Modify: `videoclaw/models/volcengine/seedance.py`

**Step 1: 修改 i2v.py 添加 --video-ref 和 --audio-ref 参数**

读取现有 i2v.py 文件，然后添加参数：

```python
@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--image", "-i", "images", multiple=True, required=True, help="图片路径，可多次指定")
@click.option("--prompt", "-t", "prompts", multiple=True, required=True, help="传给视频模型的 prompt")
@click.option("--video-ref", "-v", "video_refs", multiple=True, default=None, help="视频参考路径（运镜/动作）")
@click.option("--audio-ref", "-a", "audio_refs", multiple=True, default=None, help="音频参考路径（配乐/对白）")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--resolution", "-r", default=None, help="视频分辨率，如 1920x1080, 1280x720")
def i2v(project: str, images: tuple, prompts: tuple, video_refs: tuple, audio_refs: tuple, provider: str, resolution: str):
    """图生视频（支持多图+视频+音频输入）"""
    # ... 现有逻辑 ...
```

**Step 2: 修改 VolcEngineSeedance 支持多模态输入**

在 seedance.py 中修改 image_to_video 方法：

```python
def image_to_video(
    self,
    image: bytes | list[bytes],  # 支持单图或多图
    prompt: str,
    video_refs: list[str] = None,  # 视频参考路径
    audio_refs: list[str] = None,  # 音频参考路径
    **kwargs
) -> GenerationResult:
    """生成视频

    Args:
        image: 图片 bytes 或图片 bytes 列表（最多9张）
        prompt: Seedance 2.0 格式提示词
        video_refs: 视频参考文件路径列表（最多3个）
        audio_refs: 音频参考文件路径列表（最多3个）
    """
    # 处理多图输入
    images = image if isinstance(image, list) else [image]

    # 处理视频参考
    video_urls = []
    if video_refs:
        for vr in video_refs:
            # 上传视频获取 URL
            video_url = self._upload_file(vr)
            video_urls.append(video_url)

    # 处理音频参考
    audio_urls = []
    if audio_refs:
        for ar in audio_refs:
            # 上传音频获取 URL
            audio_url = self._upload_file(ar)
            audio_urls.append(audio_url)

    # 构建 content
    content = [{"type": "text", "text": prompt}]

    # 添加图片
    for img in images:
        b64_img = self._encode_image(img)
        content.append({"type": "image_url", "image_url": {"url": b64_img}})

    # 调用 API
    response = self.client.content_generation.tasks.create(
        model=self.model,
        content=content,
        # ... 其他参数
    )
```

**Step 3: 测试验证**

```bash
# 测试多图输入
python -m py_compile videoclaw/cli/commands/i2v.py
python -m py_compile videoclaw/models/volcengine/seedance.py
```

**Step 4: Commit**

```bash
git add videoclaw/cli/commands/i2v.py videoclaw/models/volcengine/seedance.py
git commit -m "feat: enhance i2v to support multi-modal input (image+video+audio)"
```

---

## Task 5: 更新 CLI 帮助文档

**Files:**
- Modify: `docs/configuration.md`（如需要）

**Step 1: 更新 i2v 命令帮助**

```bash
videoclaw i2v --help
```

确认显示新的参数：--video-ref, --audio-ref

**Step 2: Commit**

```bash
git commit -m "docs: update i2v command help for multi-modal input"
```

---

## 总结

完成所有任务后，video-quick-create 将支持：

1. ✅ 故事大纲生成
2. ✅ 素材需求推断和确认
3. ✅ Seedance 2.0 格式文本分镜
4. ✅ i2v 多模态输入（图片 + 视频 + 音频）

**Plan complete and saved to `docs/plans/2026-02-22-video-quick-create-seedance2-impl.md`. Two execution options:**

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?