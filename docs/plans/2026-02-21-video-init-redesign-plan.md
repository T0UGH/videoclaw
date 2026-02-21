# video-init 交互重构实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 CLI init 命令改为非交互式，将交互逻辑移到 video-init skill 层，并修复配置加载逻辑。

**Architecture:** CLI 工具只负责执行命令，交互在 skill 层用 AskUserQuestion 实现。配置加载使用深度合并，优先级：环境变量 > 项目配置 > 全局配置。

**Tech Stack:** Python Click, YAML, AskUserQuestion

---

### Task 1: 修改 CLI init 命令 - 改为非交互式

**Files:**
- Modify: `videoclaw/cli/main.py:48-127`

**Step 1: 修改默认行为**

将 `init` 命令的 `--interactive/--no-interactive` 默认值从 `True` 改为 `False`：

```python
@click.option("--interactive/--no-interactive", default=False, help="交互式配置")
```

**Step 2: 移除 click.prompt 交互逻辑**

删除第 70-95 行的交互选择逻辑（provider 选择部分）。

**Step 3: 修复目录存在时的 bug**

修改第 57-59 行：

```python
if project_path.exists():
    # 检查配置文件是否存在，不存在则创建
    config_file = project_path / ".videoclaw" / "config.yaml"
    if config_file.exists():
        click.echo(f"项目 {project_name} 已存在", err=True)
        return
    # 目录存在但没有配置文件，继续创建
else:
    project_path.mkdir(parents=True)
    (project_path / ".videoclaw").mkdir()
    (project_path / "assets").mkdir()
    (project_path / "storyboard").mkdir()
    (project_path / "videos").mkdir()
    (project_path / "audio").mkdir()
```

**Step 4: 简化默认配置**

将第 106-111 行的默认配置改为使用更合理的默认值：

```python
config = {
    "project_name": project_name,
    "version": "0.1.0",
    "models": {
        "image": {"provider": "dashscope"},  # 默认 dashscope
        "video": {"provider": "dashscope"},
    },
    "storage": {"provider": "local"}
}
```

**Step 5: 提交**

```bash
git add videoclaw/cli/main.py
git commit -m "fix: init 命令改为非交互式，修复目录存在时配置缺失 bug"
```

---

### Task 2: 优化配置加载逻辑 - 深度合并

**Files:**
- Modify: `videoclaw/config/loader.py`

**Step 1: 添加深度合并辅助函数**

在 `_load` 方法前添加：

```python
def _deep_merge(base: dict, override: dict) -> dict:
    """深度合并两个字典，override 优先"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
```

**Step 2: 修改 _load 方法实现正确优先级**

```python
def _load(self):
    # 1. 加载全局配置
    global_config = {}
    global_config_path = Path.home() / ".videoclaw" / "config.yaml"
    if global_config_path.exists():
        with open(global_config_path) as f:
            global_config = yaml.safe_load(f) or {}

    # 2. 加载项目配置
    project_config = {}
    if self._project_path:
        project_config_path = self._project_path / ".videoclaw" / "config.yaml"
        if project_config_path.exists():
            with open(project_config_path) as f:
                project_config = yaml.safe_load(f) or {}

    # 3. 合并：全局 + 项目（项目覆盖全局）
    self._config = _deep_merge(global_config, project_config)
```

**Step 3: 修改 get 方法简化环境变量检查**

```python
def get(self, key: str, default: Any = None) -> Any:
    """获取配置值，环境变量优先级最高"""
    # 环境变量映射
    env_mappings = {
        "dashscope.api_key": "DASHSCOPE_API_KEY",
        "volcengine.ark_api_key": "ARK_API_KEY",
        "google.api_key": "GOOGLE_API_KEY",
    }

    # 1. 先检查环境变量（最高优先级）
    if key in env_mappings:
        env_key = env_mappings[key]
        if env_key in os.environ:
            return os.environ[env_key]

    # 通用的环境变量映射 VIDEOCLAW_XXX
    env_key = f"VIDEOCLAW_{key.upper().replace('.', '_')}"
    if env_key in os.environ:
        return os.environ[env_key]

    # 2. 返回已合并的配置值
    keys = key.split(".")
    value = self._config
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
    return value if value is not None else default
```

**Step 4: 提交**

```bash
git add videoclaw/config/loader.py
git commit -m "feat: 配置加载使用深度合并，优先级环境变量>项目>全局"
```

---

### Task 3: 重写 video-init Skill 添加交互逻辑

**Files:**
- Modify: `skills/video-init/SKILL.md`

**Step 1: 重写 SKILL.md**

```markdown
---
name: video-init
description: Use when user wants to initialize a new video project with directory structure
---

# video-init - 初始化项目

## 概述

初始化新的视频项目，创建目录结构。**交互确认在 skill 层通过 AskUserQuestion 实现**。

## 使用方式

用户说"创建一个新项目"或"初始化项目"时触发。

## 交互流程

### Step 1: 询问项目名称

用 AskUserQuestion 询问：
- "请给项目起个名字？"

### Step 2: 询问图像生成提供商

```
已生成 {角色/场景} 图片，路径: {path}

这帧可以吗？还是需要调整提示词？
选项: "满意" / "调整提示词" / "重新生成"
```

### Step 3: 询问视频生成提供商

### Step 4: 询问存储方式

## 执行流程

1. 用 AskUserQuestion 收集配置（图像提供商、视频提供商、存储方式）
2. 调用 `videoclaw init <project-name>` 创建项目
3. 用 `videoclaw config --project <name> --set` 设置项目配置

## 示例

```
用户: 创建一个新项目

Claude Code:
  - 询问项目名称
  - 询问图像提供商
  - 询问视频提供商
  - 询问存储方式
  - videoclaw init my-video
  - videoclaw config --project my-video --set models.image.provider=volcengine
  - videocław config --project my-video --set models.video.provider=volcengine
  - videoclaw config --project my-video --set storage.provider=google_drive
```

## 参数

- `project_name`: 项目名称（必填）
- `--dir`: 项目目录路径（可选，默认 ~/videoclaw-projects）
```

**Step 2: 提交**

```bash
git add skills/video-init/SKILL.md
git commit -m "feat(video-init): skill 添加 AskUserQuestion 交互流程"
```

---

### Task 4: 更新 CLAUDE.md 文档

**Files:**
- Modify: `CLAUDE.md`

**Step 1: 更新配置说明**

在配置优先级部分添加更清晰的说明：

```markdown
### 配置优先级

1. **环境变量**（最高）：`DASHSCOPE_API_KEY`, `ARK_API_KEY`, `GOOGLE_API_KEY`, `VIDEOCLAW_*`
2. **项目配置**：`<project>/.videoclaw/config.yaml`
3. **全局配置**：`~/.videoclaw/config.yaml`

配置加载使用深度合并。
```

**Step 2: 提交**

```bash
git add CLAUDE.md
git commit -m "docs: 更新配置优先级说明"
```

---

### Task 5: 测试验证

**Step 1: 测试 init 命令默认非交互**

```bash
uvx videoclaw init test-project
# 应该不提示交互，直接创建项目
```

**Step 2: 测试项目配置创建**

```bash
cat ~/videoclaw-projects/test-project/.videoclaw/config.yaml
# 应该包含默认配置
```

**Step 3: 测试 video-init skill 交互**

```bash
# 用 skill 创建新项目，应该弹出 AskUserQuestion
```

**Step 4: 测试配置加载**

```bash
# 设置全局配置
videoclaw config --set models.image.provider=gemini

# 创建项目
videoclaw init test-project-2

# 验证项目使用全局配置
# （需要验证加载逻辑是否正确）
```

---

## 执行选择

**Plan complete and saved to `docs/plans/2026-02-21-video-init-redesign.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
