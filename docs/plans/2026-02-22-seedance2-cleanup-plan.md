# Seedance 2.0 清理实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 删除标准流程相关代码，全面拥抱 Seedance 2.0

**Architecture:** 分阶段删除：先删除 skills 目录，再删除 CLI 命令，最后删除状态管理模块

**Tech Stack:** Python, Click (CLI)

---

## Task 1: 删除 skills 目录

**Files:**
- Delete: `skills/video-standard-create/`
- Delete: `skills/video-assets/`
- Delete: `skills/video-storyboard/`
- Delete: `skills/video-status/`

**Step 1: 删除目录**

```bash
rm -rf skills/video-standard-create
rm -rf skills/video-assets
rm -rf skills/video-storyboard
rm -rf skills/video-status
```

**Step 2: 验证删除**

Run: `ls skills/ | grep -E 'video-(standard-create|assets|storyboard|status)'`
Expected: 无输出（目录已删除）

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: 删除标准流程相关的 skills 目录"
```

---

## Task 2: 删除 CLI 命令文件

**Files:**
- Delete: `videoclaw/cli/commands/assets.py`
- Delete: `videoclaw/cli/commands/storyboard.py`
- Delete: `videoclaw/cli/commands/i2v_from_storyboard.py`

**Step 1: 删除文件**

```bash
rm videoclaw/cli/commands/assets.py
rm videoclaw/cli/commands/storyboard.py
rm videoclaw/cli/commands/i2v_from_storyboard.py
```

**Step 2: Commit**

```bash
git add -A
git commit -m "chore: 删除标准流程相关的 CLI 命令文件"
```

---

## Task 3: 修改 audio.py 移除状态管理

**Files:**
- Modify: `videoclaw/cli/commands/audio.py`

**Step 1: 读取当前文件**

```bash
cat videoclaw/cli/commands/audio.py
```

**Step 2: 修改代码**

移除以下代码：
```python
from videoclaw.state import StateManager  # 删除导入

state = StateManager(project_path)  # 删除实例化

# 删除状态检查
i2v_step = state.get_step("i2v")
if not i2v_step or i2v_step.get("status") != "completed":
    click.echo("错误: 请先完成视频生成", err=True)
    return

# 删除状态更新
state.set_status("generating_audio")
state.update_step("audio", "in_progress")
state.update_step("audio", "completed", result)
state.set_status("audio_generated")
```

改为直接接收参数：
```python
@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商")
@click.option("--text", "-t", help="TTS 文本内容")
@click.option("--duration", default=30, help="背景音乐时长")
def audio(project: str, provider: str, text: str, duration: int):
    """生成音频（TTS、音效、背景音乐）"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    config = Config(project_path)
    audio_backend = get_audio_backend(provider, config.get_all())

    audio_dir = project_path / "audio"
    audio_dir.mkdir(exist_ok=True)

    # 直接使用命令行参数，不再从 state 读取
    ...
```

**Step 3: 验证修改**

Run: `grep -n "StateManager" videoclaw/cli/commands/audio.py`
Expected: 无输出

**Step 4: Commit**

```bash
git add videoclaw/cli/commands/audio.py
git commit -m "refactor: audio 命令移除状态管理依赖"
```

---

## Task 4: 修改 merge.py 移除状态管理

**Files:**
- Modify: `videoclaw/cli/commands/merge.py`

**Step 1: 读取当前文件**

```bash
cat videoclaw/cli/commands/merge.py
```

**Step 2: 修改代码**

移除 StateManager 相关代码，改为接收命令行参数：
```python
@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--videos", "-v", multiple=True, required=True, help="视频文件路径")
@click.option("--audio", "-a", help="背景音乐文件")
@click.option("--output", "-o", default="final.mp4", help="输出文件名")
def merge(project: str, videos: tuple, audio: str, output: str):
    """合并视频片段"""
    project_path = DEFAULT_PROJECTS_DIR / project

    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    config = Config(project_path)

    # 直接使用命令行参数，不再从 state 读取
    video_files = list(videos)
    bgm_file = audio
    ...
```

**Step 3: 验证修改**

Run: `grep -n "StateManager" videoclaw/cli/commands/merge.py`
Expected: 无输出

**Step 4: Commit**

```bash
git add videoclaw/cli/commands/merge.py
git commit -m "refactor: merge 命令移除状态管理依赖"
```

---

## Task 5: 修改 main.py 移除命令注册

**Files:**
- Modify: `videoclaw/cli/main.py`

**Step 1: 读取当前文件**

```bash
cat videoclaw/cli/main.py
```

**Step 2: 修改导入部分**

移除：
```python
from videoclaw.cli.commands.assets import assets
from videoclaw.cli.commands.storyboard import storyboard
from videoclaw.cli.commands.i2v_from_storyboard import i2v_from_storyboard
```

**Step 3: 修改命令注册部分**

移除：
```python
cli.add_command(assets)
cli.add_command(storyboard)
cli.add_command(i2v_from_storyboard)
```

**Step 4: 验证修改**

Run: `grep -E "(assets|storyboard|i2v_from_storyboard)" videoclaw/cli/main.py`
Expected: 无输出

**Step 5: Commit**

```bash
git add videoclaw/cli/main.py
git commit -m "chore: main.py 移除标准流程命令注册"
```

---

## Task 6: 删除状态管理模块

**Files:**
- Delete: `videoclaw/state/manager.py`
- Delete: `videoclaw/state/__init__.py`
- Delete: `videoclaw/pipeline/orchestrator.py`

**Step 1: 删除目录和文件**

```bash
rm -rf videoclaw/state/
rm videoclaw/pipeline/orchestrator.py
```

**Step 2: 检查是否有其他文件引用**

Run: `grep -r "from videoclaw.state" videoclaw/`
Expected: 无输出

Run: `grep -r "from videoclaw.pipeline" videoclaw/`
Expected: 无输出

**Step 3: 删除空的 pipeline 目录（如果有）**

```bash
ls videoclaw/pipeline/
# 如果为空，删除
rmdir videoclaw/pipeline/
```

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: 删除状态管理模块和 pipeline"
```

---

## Task 7: 删除相关测试文件

**Files:**
- Delete: `tests/test_state.py`
- Delete: `tests/test_state_selections.py`
- Delete: `tests/test_storyboard_num_variants.py`
- Delete: `tests/test_assets_num_variants.py`
- Delete: `tests/test_pipeline.py`

**Step 1: 删除文件**

```bash
rm tests/test_state.py
rm tests/test_state_selections.py
rm tests/test_storyboard_num_variants.py
rm tests/test_assets_num_variants.py
rm tests/test_pipeline.py
```

**Step 2: Commit**

```bash
git add -A
git commit -m "chore: 删除状态管理相关测试文件"
```

---

## Task 8: 验证 CLI 正常工作

**Step 1: 运行 CLI 帮助**

Run: `python -m videoclaw.cli.main --help`
Expected: 输出帮助信息，不包含 assets/storyboard/i2v-from-storyboard

**Step 2: 验证保留的命令**

Run: `python -m videoclaw.cli.main --help | grep -E "(t2i|i2i|i2v|audio|merge)"`
Expected: 显示 t2i, i2i, i2v, audio, merge 命令

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: 完成 Seedance 2.0 清理"
```

---

## Task 9: 恢复已删除的 skills 目录

**注意：** 由于 Task 1 已经删除了 skills 目录，需要恢复。检查 git 状态。

**Step 1: 检查 git 状态**

```bash
git status
```

**Step 2: 如果目录已删除但未提交，恢复**

```bash
# 如果 Task 1 的删除尚未 commit，恢复
git checkout -- skills/
```

---

**Plan complete and saved to `docs/plans/2026-02-22-seedance2-cleanup-plan.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
