# i2v 命令重构实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 `videoclaw i2v` 重构为两个独立命令：通用模式 `i2v`（接收 -i -t 参数）和 storyboard 模式 `i2v-from-storyboard`

**Architecture:** 重用现有 i2v 逻辑，将从 storyboard 读取帧的逻辑分离到新文件。通用 i2v 直接接收图片和 prompt 参数。

**Tech Stack:** Click (CLI), Python

---

### Task 1: 重命名现有 i2v.py 为 i2v_from_storyboard.py

**Files:**
- Modify: `videoclaw/cli/commands/i2v.py` → `videoclaw/cli/commands/i2v_from_storyboard.py`

**Step 1: 重命名文件**

```bash
mv videoclaw/cli/commands/i2v.py videoclaw/cli/commands/i2v_from_storyboard.py
```

**Step 2: 更新函数名和 docstring**

修改 `i2v_from_storyboard.py`:
- 函数名改为 `i2v_from_storyboard`
- docstring 改为 "从 storyboard 生成视频"

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/i2v_from_storyboard.py videoclaw/cli/commands/i2v.py
git mv videoclaw/cli/commands/i2v.py videoclaw/cli/commands/i2v_from_storyboard.py
git commit -m "refactor: rename i2v.py to i2v_from_storyboard.py"
```

---

### Task 2: 创建新的通用 i2v 命令

**Files:**
- Create: `videoclaw/cli/commands/i2v.py`

**Step 1: 创建 i2v.py**

```python
"""i2v 命令 - 通用图生视频"""
from __future__ import annotations

import click
import shutil
from pathlib import Path

from videoclaw.config import Config
from videoclaw.models.factory import get_video_backend
from videoclaw.utils.logging import get_logger
from videoclaw.storage.uploader import upload_to_cloud


DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--image", "-i", "images", multiple=True, required=True, help="图片路径，可多次指定")
@click.option("--prompt", "-t", "prompts", multiple=True, required=True, help="传给视频模型的 prompt")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--resolution", "-r", default=None, help="视频分辨率，如 1920x1080, 1280x720")
def i2v(project: str, images: tuple, prompts: tuple, provider: str, resolution: str):
    """图生视频（通用模式）"""
    if len(images) != len(prompts):
        click.echo("错误: --image 和 --prompt 数量必须一致", err=True)
        return

    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始图生视频，项目: {project}")

    config = Config(project_path)

    # 获取模型
    model = config.get("models.video.model", "")
    video_backend = get_video_backend(provider, model, config.get_all())

    # 确定分辨率
    final_resolution = resolution or config.get("models.video.resolution", "1280x720")
    logger.info(f"使用分辨率: {final_resolution}")

    videos_dir = project_path / "videos"
    videos_dir.mkdir(exist_ok=True)

    result = {"videos": []}

    # 为每张图片生成视频
    for idx, (image_path, prompt) in enumerate(zip(images, prompts)):
        image_path = Path(image_path)
        if not image_path.exists():
            click.echo(f"警告: 图片 {image_path} 不存在，跳过")
            continue

        click.echo(f"生成视频片段 {idx + 1}: {prompt[:30]}...", nl=False)

        # 读取图片
        with open(image_path, "rb") as f:
            image_data = f.read()

        # 调用模型生成视频
        gen_result = video_backend.image_to_video(image_data, prompt)

        # 保存到项目目录
        dest_path = videos_dir / f"video_{idx:03d}.mp4"
        if gen_result.local_path:
            shutil.copy(gen_result.local_path, dest_path)
            result["videos"].append({
                "index": idx,
                "path": str(dest_path),
                "prompt": prompt
            })
            click.echo(f" 已保存: {dest_path.name}")

            # 上传到云盘
            cloud_url = upload_to_cloud(
                dest_path,
                f"videoclaw/{project}/videos/{dest_path.name}",
                config,
                project
            )
            if cloud_url:
                click.echo(f" 云盘链接: {cloud_url}")

    click.echo("\n视频生成完成!")
```

**Step 2: 运行测试验证**

```bash
# 检查语法
python -m py_compile videoclaw/cli/commands/i2v.py
```

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/i2v.py
git commit -m "feat: add generic i2v command with -i and -t parameters"
```

---

### Task 3: 注册两个命令到 main.py

**Files:**
- Modify: `videoclaw/cli/main.py`

**Step 1: 添加导入**

在文件顶部添加:
```python
from videoclaw.cli.commands.i2v_from_storyboard import i2v_from_storyboard
```

**Step 2: 注册命令**

找到 `main.add_command(i2v)` 行，改为:
```python
main.add_command(i2v)
main.add_command(i2v_from_storyboard)
```

**Step 3: 验证命令可用**

```bash
videoclaw --help
# 应该看到 i2v 和 i2v-from-storyboard 两个命令
```

**Step 4: Commit**

```bash
git add videoclaw/cli/main.py
git commit -m "feat: register i2v and i2v-from-storyboard commands"
```

---

### Task 4: 更新 skill 文档

**Files:**
- Modify: `skills/video-quick-create/SKILL.md`
- Modify: `skills/video-standard-create/SKILL.md`

**Step 1: 更新 video-quick-create**

将:
```bash
videoclaw i2v -p <project>
```
改为:
```bash
videoclaw i2v -p <project> -i <assets/image1.png> -t "镜头1描述" -i <assets/image2.png> -t "镜头2描述"
```

**Step 2: 更新 video-standard-create**

将 i2v 步骤改为:
```bash
videoclaw i2v-from-storyboard -p <project>
```

**Step 3: Commit**

```bash
git add skills/
git commit -m "docs: update skill docs for new i2v commands"
```

---

### 总结

完成所有任务后，你将拥有:

1. `videoclaw i2v` - 通用模式，接收 `-i` 图片和 `-t` prompt
2. `videoclaw i2v-from-storyboard` - 从 storyboard 读取

**Plan complete and saved to `docs/plans/2026-02-21-i2v-redesign.md`. Two execution options:**

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
