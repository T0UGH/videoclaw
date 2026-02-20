# Skill 驱动架构改造计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 移除 `videoclaw analyze` CLI 命令，改为 skill 直接分析，新增 `videoclaw validate` 命令

**Architecture:**
- 删除 video-analyze skill，相关分析逻辑合并到 video-create skill
- 删除 analyze CLI 命令，但 state.json 仍保留 analyze 数据（由 skill 写入）
- 新增 validate 命令验证 JSON 格式

**Tech Stack:** Click (CLI), Claude Code Skills

---

## 影响范围

| 类型 | 文件 | 操作 |
|------|------|------|
| Skill | `skills/video-analyze/` | 删除 |
| Skill | `skills/video-create/SKILL.md` | 修改 |
| Skill | `skills/video-assets/SKILL.md` | 修改 |
| Skill | `skills/video-status/SKILL.md` | 修改 |
| CLI | `videoclaw/cli/commands/analyze.py` | 删除 |
| CLI | `videoclaw/cli/main.py` | 修改 |
| CLI | `videoclaw/cli/commands/validate.py` | 新增 |

---

## Task 1: 删除 video-analyze Skill

**Files:**
- Delete: `skills/video-analyze/`

**Step 1: 删除目录**

```bash
rm -rf skills/video-analyze
```

**Step 2: 确认删除**

```bash
ls skills/
```

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: remove video-analyze skill (now handled by video-create)"
```

---

## Task 2: 修改 video-create Skill

**Files:**
- Modify: `skills/video-create/SKILL.md`

**Step 1: 更新执行流程**

将第 19 行：
```
2. 调用 `videoclaw analyze --script "<用户描述>" --project <project-name>` 分析脚本
```

改为：
```
2. 直接使用 Claude 能力分析脚本，生成 JSON 并写入 `<project>/.videoclaw/state.json` 的 `steps.analyze.output` 字段
```

**Step 2: 更新示例**

将第 45 行：
```
2. videoclaw analyze --script "宇航员在火星上发现外星遗迹" --project mars-video
```

改为：
```
2. 直接分析脚本，生成 JSON：
   {
     "script": "宇航员在火星上发现外星遗迹",
     "characters": [...],
     "scenes": [...],
     "frames": [...]
   }
   保存到 .videoclaw/state.json
```

**Step 3: 添加 JSON 格式说明**

在文件末尾添加：

```markdown
## 分析结果格式

分析结果直接写入 `<project>/.videoclaw/state.json`：

```json
{
  "script": "原始脚本描述",
  "characters": [
    {"name": "角色名", "description": "角色描述", "appearance": "外观描述"}
  ],
  "scenes": [
    {"name": "场景名", "description": "场景描述", "time": "时间"}
  ],
  "frames": [
    {
      "id": 1,
      "scene": "场景名",
      "description": "画面描述",
      "duration": 5
    }
  ]
}
```
```

**Step 4: Commit**

```bash
git add skills/video-create/SKILL.md
git commit -m "feat: update video-create skill to handle analysis directly"
```

---

## Task 3: 修改 video-assets Skill

**Files:**
- Modify: `skills/video-assets/SKILL.md`

**Step 1: 移除 analyze 依赖说明**

删除第 23 行：
```
需要先完成 `video:analyze`
```

改为：
```
分析结果已在 video-create 时生成，保存在 state.json 中
```

**Step 2: Commit**

```bash
git add skills/video-assets/SKILL.md
git commit -m "docs: update video-assets skill to reference state.json"
```

---

## Task 4: 修改 video-status Skill

**Files:**
- Modify: `skills/video-status/SKILL.md`

**Step 1: 检查并更新 analyze 状态说明**

如果文件中有提到 analyze 步骤需要先完成 CLI 命令，改为由 skill 直接完成。

**Step 2: Commit**

```bash
git add skills/video-status/SKILL.md
git commit -m "docs: update video-status skill"
```

---

## Task 5: 删除 analyze CLI 命令

**Files:**
- Delete: `videoclaw/cli/commands/analyze.py`
- Modify: `videoclaw/cli/main.py`

**Step 1: 删除 analyze.py**

```bash
rm videoclaw/cli/commands/analyze.py
```

**Step 2: 从 main.py 移除 analyze 命令**

在 `main.py` 中找到并删除 analyze 相关的函数和命令注册（约第 83 行开始的 analyze 函数，以及命令注册）。

**Step 3: 运行测试确认没有破坏**

```bash
pytest tests/ -v
```

**Step 4: Commit**

```bash
git add videoclaw/cli/
git commit -m "chore: remove videoclaw analyze CLI command"
```

---

## Task 6: 新增 validate CLI 命令

**Files:**
- Create: `videoclaw/cli/commands/validate.py`
- Modify: `videoclaw/cli/main.py`

**Step 1: 创建 validate.py**

```python
"""validate 命令 - 验证 JSON 格式"""
import json
import click
from pathlib import Path


@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--strict", is_flag=True, help="严格模式：检查必需字段")
def validate(project: str, strict: bool):
    """验证项目 state.json 格式"""
    config_dir = Path.home() / "videoclaw-projects" / project / ".videoclaw"
    state_file = config_dir / "state.json"

    if not state_file.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        click.echo(f"未找到: {state_file}", err=True)
        raise click.Abort()

    try:
        with open(state_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"错误: JSON 格式无效", err=True)
        click.echo(str(e), err=True)
        raise click.Abort()

    # 基础验证
    if "script" not in data:
        click.echo("警告: 缺少 script 字段", err=True)

    if "steps" not in data:
        click.echo("错误: 缺少 steps 字段", err=True)
        raise click.Abort()

    # 严格模式验证
    if strict:
        required_fields = ["script", "characters", "scenes", "frames"]
        for field in required_fields:
            if field not in data:
                click.echo(f"错误: 严格模式下必须包含 {field} 字段", err=True)
                raise click.Abort()

    click.echo(f"✓ 项目 {project} 的 state.json 格式有效")

    # 显示关键信息
    if "script" in data:
        click.echo(f"脚本: {data['script'][:50]}...")
    if "characters" in data:
        click.echo(f"角色数: {len(data.get('characters', []))}")
    if "scenes" in data:
        click.echo(f"场景数: {len(data.get('scenes', []))}")
    if "frames" in data:
        click.echo(f"帧数: {len(data.get('frames', []))}")
```

**Step 2: 在 main.py 注册 validate 命令**

在 main.py 中添加：

```python
from videoclaw.cli.commands.validate import validate

# 在 cli 装饰器中添加
cli.add_command(validate)
```

**Step 3: 测试 validate 命令**

```bash
# 先初始化一个项目测试
videoclaw init test-validate
videoclaw validate --project test-validate

# 测试严格模式
videoclaw validate --project test-validate --strict
```

**Step 4: Commit**

```bash
git add videoclaw/cli/commands/validate.py videoclaw/cli/main.py
git commit -m "feat: add videoclaw validate command"
```

---

## Task 7: 最终验证

**Step 1: 运行完整测试**

```bash
pytest tests/ -v
```

**Step 2: 验证 CLI 可用命令**

```bash
videoclaw --help
# 确认 analyze 已移除，validate 已添加
```

**Step 3: 确认 skills 目录**

```bash
ls skills/
# 确认 video-analyze 已删除
```

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: complete skill-driven architecture refactor"
```
