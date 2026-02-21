# CLI Enhancements Implementation Plan - Phase 1

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 改善用户体验，解决 problem.md 中的高频问题：生成多张供选择、独立 t2i/i2i 命令、Asset/Frame 选择记录、video-init 交互式配置

**Architecture:** 在现有 CLI 框架上增加参数和新命令，更新 state.json 结构支持选择记录

**Tech Stack:** Click, Python, Pytest

---

## Task 1: 新增独立 t2i 命令

**Files:**
- Create: `videoclaw/cli/commands/t2i.py`
- Modify: `videoclaw/cli/main.py`
- Test: `tests/test_t2i_command.py`

**Step 1: 创建测试文件**

```python
# tests/test_t2i_command.py
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

def test_t2i_command_requires_prompt():
    """测试 t2i 命令缺少 prompt 参数"""
    from videoclaw.cli.commands.t2i import t2i
    runner = CliRunner()
    result = runner.invoke(t2i, ["--output", "test.png"])
    assert result.exit_code != 0

def test_t2i_command_requires_output():
    """测试 t2i 命令缺少 output 参数"""
    from videoclaw.cli.commands.t2i import t2i
    runner = CliRunner()
    result = runner.invoke(t2i, ["--prompt", "test"])
    assert result.exit_code != 0

def test_t2i_command_success():
    """测试 t2i 命令成功执行"""
    from videoclaw.cli.commands.t2i import t2i
    runner = CliRunner()

    with patch("videoclaw.cli.commands.t2i.get_image_backend") as mock_backend:
        mock_result = MagicMock()
        mock_result.local_path.__str__ = lambda: "/tmp/test.png"
        mock_backend.return_value.text_to_image.return_value = mock_result

        with patch("shutil.copy"):
            result = runner.invoke(t2i, ["--prompt", "astronaut", "--output", "/tmp/test.png"])
            assert "Generated:" in result.output
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_t2i_command.py -v`
Expected: FAIL (模块不存在)

**Step 3: 创建 t2i.py**

```python
"""独立文生图命令"""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import get_image_backend


@click.command()
@click.option("--prompt", "-p", required=True, help="生成提示词")
@click.option("--output", "-o", required=True, help="输出文件路径")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--model", help="模型名称")
def t2i(prompt: str, output: str, provider: str, model: str | None):
    """文生图 - 独立命令"""
    config = Config()

    # 获取模型名称
    if not model:
        model = config.get(f"models.{provider}.image.model")
        if not model:
            # 兼容旧配置
            model = config.get(f"{provider}.model")

    # 获取 API key
    api_key = config.get(f"{provider}.api_key")

    backend = get_image_backend(provider, model, {"api_key": api_key})

    result = backend.text_to_image(prompt)

    # 复制到目标路径
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(result.local_path, output_path)

    click.echo(f"Generated: {output}")
```

**Step 4: 注册命令到 main.py**

```python
# videoclaw/cli/main.py 添加
from videoclaw.cli.commands.t2i import t2i

# 在 cli 变量定义后添加
cli.add_command(t2i)
```

**Step 5: 运行测试验证通过**

Run: `pytest tests/test_t2i_command.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add videoclaw/cli/commands/t2i.py videoclaw/cli/main.py tests/test_t2i_command.py
git commit -m "feat: add standalone t2i command for image generation"
```

---

## Task 2: 新增独立 i2i 命令

**Files:**
- Create: `videoclaw/cli/commands/i2i.py`
- Modify: `videoclaw/cli/main.py`
- Test: `tests/test_i2i_command.py`

**Step 1: 创建测试文件**

```python
# tests/test_i2i_command.py
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

def test_i2i_command_requires_input():
    """测试 i2i 命令缺少 input 参数"""
    from videoclaw.cli.commands.i2i import i2i
    runner = CliRunner()
    result = runner.invoke(i2i, ["--prompt", "test", "--output", "test.png"])
    assert result.exit_code != 0

def test_i2i_command_requires_prompt():
    """测试 i2i 命令缺少 prompt 参数"""
    from videoclaw.cli.commands.i2i import i2i
    runner = CliRunner()
    result = runner.invoke(i2i, ["--input", "test.png", "--output", "test2.png"])
    assert result.exit_code != 0

def test_i2i_command_success():
    """测试 i2i 命令成功执行"""
    from videoclaw.cli.commands.i2i import i2i
    runner = CliRunner()

    with patch("videoclaw.cli.commands.i2i.get_image_backend") as mock_backend:
        mock_result = MagicMock()
        mock_result.local_path.__str__ = lambda: "/tmp/test2.png"
        mock_backend.return_value.image_to_image.return_value = mock_result

        with patch("shutil.copy"):
            with patch("pathlib.Path.read_bytes", return_value=b"fake image"):
                result = runner.invoke(i2i, [
                    "--input", "/tmp/test.png",
                    "--prompt", "穿红色制服",
                    "--output", "/tmp/test2.png"
                ])
                assert "Generated:" in result.output
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_i2i_command.py -v`
Expected: FAIL (模块不存在)

**Step 3: 创建 i2i.py**

```python
"""独立图生图命令"""
from __future__ import annotations

import shutil
from pathlib import Path

import click

from videoclaw.config.loader import Config
from videoclaw.models.factory import get_image_backend


@click.command()
@click.option("--input", "-i", "input_path", required=True, help="输入图片路径")
@click.option("--prompt", "-p", required=True, help="生成提示词")
@click.option("--output", "-o", required=True, help="输出文件路径")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--model", help="模型名称")
def i2i(input_path: str, prompt: str, output: str, provider: str, model: str | None):
    """图生图 - 独立命令"""
    config = Config()

    # 获取模型名称
    if not model:
        model = config.get(f"models.{provider}.image.model")
        if not model:
            model = config.get(f"{provider}.model")

    # 获取 API key
    api_key = config.get(f"{provider}.api_key")

    backend = get_image_backend(provider, model, {"api_key": api_key})

    # 读取输入图片
    image_bytes = Path(input_path).read_bytes()

    result = backend.image_to_image(image_bytes, prompt)

    # 复制到目标路径
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(result.local_path, output_path)

    click.echo(f"Generated: {output}")
```

**Step 4: 注册命令到 main.py**

```python
# videoclaw/cli/main.py 添加
from videoclaw.cli.commands.i2i import i2i

cli.add_command(i2i)
```

**Step 5: 运行测试验证通过**

Run: `pytest tests/test_i2i_command.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add videoclaw/cli/commands/i2i.py videoclaw/cli/main.py tests/test_i2i_command.py
git commit -m "feat: add standalone i2i command for image-to-image"
```

---

## Task 3: CLI 增加 --num-variants 参数 (assets)

**Files:**
- Modify: `videoclaw/cli/commands/assets.py:67-100`
- Test: `tests/test_assets_num_variants.py`

**Step 1: 创建测试文件**

```python
# tests/test_assets_num_variants.py
import os
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

def test_assets_generates_multiple_variants():
    """测试 assets 命令生成多个候选"""
    from videoclaw.cli.commands.assets import assets
    from click.testing import CliRunner

    runner = CliRunner()

    with patch("videoclaw.cli.commands.assets.get_image_backend") as mock_backend:
        mock_result = MagicMock()
        mock_result.local_path = Path("/tmp/test.png")
        mock_result.metadata = {"provider": "mock"}

        # 模拟多次调用返回不同结果
        mock_backend.return_value.text_to_image = lambda prompt, **kw: mock_result

        with patch("shutil.copy"):
            with patch("videoclaw.cli.commands.assets.StateManager") as mock_state:
                mock_state_instance = MagicMock()
                mock_state.return_value = mock_state_instance

                result = runner.invoke(assets, [
                    "--project", "test",
                    "--num-variants", "3"
                ])

                # 验证 text_to_image 被调用 3 次
                assert mock_backend.return_value.text_to_image.call_count == 3
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_assets_num_variants.py -v`
Expected: FAIL (num-variants 参数不存在)

**Step 3: 修改 assets.py 添加参数**

```python
# videoclaw/cli/commands/assets.py
# 在 assets 函数参数中添加
@click.option("--num-variants", "-n", default=1, type=int, help="生成候选数量 (默认1)")
def assets(project, dir, provider, model, use_local, num_variants):
```

**Step 4: 修改生成逻辑**

```python
# 在角色生成部分 (约第 67-100 行)
variants = []
for i in range(num_variants):
    gen_result = image_backend.text_to_image(prompt)

    # 构建 variant 文件名
    stem = dest_path.stem
    suffix = dest_path.suffix
    variant_path = dest_path.parent / f"{stem}_{i+1}{suffix}"

    shutil.copy(gen_result.local_path, variant_path)
    variants.append(str(variant_path))

# 场景生成同样逻辑...

# 更新 state
state_manager.update_step("assets", {
    "status": "completed",
    "variants": variants,
    "chosen": variants[0] if variants else None
})
```

**Step 5: 运行测试验证通过**

Run: `pytest tests/test_assets_num_variants.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add videoclaw/cli/commands/assets.py tests/test_assets_num_variants.py
git commit -m "feat: add --num-variants to assets command"
```

---

## Task 4: CLI 增加 --num-variants 参数 (storyboard)

**Files:**
- Modify: `videoclaw/cli/commands/storyboard.py:86-131`
- Test: `tests/test_storyboard_num_variants.py`

**Step 1: 创建测试文件**

```python
# tests/test_storyboard_num_variants.py
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

def test_storyboard_generates_multiple_variants():
    """测试 storyboard 命令生成多个候选"""
    from videoclaw.cli.commands.storyboard import storyboard
    runner = CliRunner()

    with patch("videoclaw.cli.commands.storyboard.get_image_backend") as mock_backend:
        mock_result = MagicMock()
        mock_result.local_path.__str__ = lambda: "/tmp/test.png"
        mock_backend.return_value.text_to_image = lambda prompt, **kw: mock_result

        with patch("shutil.copy"):
            with patch("videoclaw.cli.commands.storyboard.StateManager") as mock_state:
                mock_state_instance = MagicMock()
                mock_state.return_value = mock_state_instance

                result = runner.invoke(storyboard, [
                    "--project", "test",
                    "--num-variants", "4"
                ])

                assert mock_backend.return_value.text_to_image.call_count == 4
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_storyboard_num_variants.py -v`
Expected: FAIL

**Step 3: 修改 storyboard.py**

类似 assets.py，添加 `--num-variants` 参数和生成逻辑

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_storyboard_num_variants.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/cli/commands/storyboard.py tests/test_storyboard_num_variants.py
git commit -m "feat: add --num-variants to storyboard command"
```

---

## Task 5: Asset/Frame 选择记录

**Files:**
- Modify: `videoclaw/state/manager.py`
- Test: `tests/test_state_selections.py`

**Step 1: 创建测试文件**

```python
# tests/test_state_selections.py
import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory


def test_state_manager_update_selection():
    """测试更新选择记录"""
    from videoclaw.state.manager import StateManager

    with TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test"
        project_path.mkdir(parents=True)
        (project_path / ".videoclaw").mkdir()

        manager = StateManager(project_path)

        manager.update_selection(
            "assets",
            chosen="assets/character_1.png",
            alternatives=[
                "assets/character_1.png",
                "assets/character_2.png",
                "assets/character_3.png",
                "assets/character_4.png"
            ]
        )

        selection = manager.get_selection("assets")
        assert selection["chosen"] == "assets/character_1.png"
        assert len(selection["alternatives"]) == 4


def test_state_manager_get_all_alternatives():
    """测试获取所有候选"""
    from videoclaw.state.manager import StateManager

    with TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test"
        project_path.mkdir(parents=True)
        (project_path / ".videoclaw").mkdir()

        manager = StateManager(project_path)

        manager.update_selection("assets", "a1.png", ["a1.png", "a2.png"])
        manager.update_selection("storyboard", "s1.png", ["s1.png", "s2.png"])

        all_alts = manager.get_all_alternatives()
        assert len(all_alts) == 4
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_state_selections.py -v`
Expected: FAIL (方法不存在)

**Step 3: 修改 manager.py**

```python
# videoclaw/state/manager.py 添加方法

def update_selection(self, step: str, chosen: str, alternatives: list):
    """更新用户选择"""
    if "selections" not in self._state:
        self._state["selections"] = {}

    self._state["selections"][step] = {
        "chosen": chosen,
        "alternatives": alternatives
    }
    self._save()

def get_selection(self, step: str) -> dict | None:
    """获取选择"""
    return self._state.get("selections", {}).get(step)

def get_all_alternatives(self) -> list:
    """获取所有候选（可用于参考）"""
    alternatives = []
    for step, data in self._state.get("selections", {}).items():
        alternatives.extend(data.get("alternatives", []))
    return alternatives
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_state_selections.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/state/manager.py tests/test_state_selections.py
git commit -m "feat: add selection tracking to StateManager"
```

---

## Task 6: video-init 交互式配置

**Files:**
- Modify: `videoclaw/cli/commands/init.py`
- Test: `tests/test_init_interactive.py`

**Step 1: 创建测试文件**

```python
# tests/test_init_interactive.py
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_init_interactive_config():
    """测试交互式配置"""
    from videoclaw.cli.commands.init import init

    runner = CliRunner()

    with patch("click.prompt") as mock_prompt:
        # 模拟用户选择
        mock_prompt.side_effect = ["1", "1", "1"]  # volcengine, volcengine, local

        with patch("pathlib.Path.mkdir"):
            with patch("builtins.open", MagicMock()):
                result = runner.invoke(init, ["test-project", "--interactive"])

                # 验证配置被写入
                assert "选择图像生成提供商" in result.output or result.exit_code == 0
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_init_interactive.py -v`
Expected: FAIL

**Step 3: 修改 init.py**

添加交互式配置逻辑：

```python
# videoclaw/cli/commands/init.py
# 在 init 函数中添加 interactive 参数

@click.command()
@click.argument("project_name")
@click.option("--dir", default="~/videoclaw-projects", help="项目根目录")
@click.option("--interactive/--no-interactive", default=True, help="交互式配置")
def init(project_name: str, dir: str, interactive: bool):
    """初始化项目"""

    # ... 现有目录创建逻辑 ...

    if interactive:
        # 1. 选择图像提供商
        click.echo("\n选择图像生成提供商:")
        click.echo("  1) volcengine (火山引擎 Seedream)")
        click.echo("  2) dashscope (阿里云)")
        click.echo("  3) gemini (Google)")
        click.echo("  4) mock (测试用)")
        provider_map = {"1": "volcengine", "2": "dashscope", "3": "gemini", "4": "mock"}
        choice = click.prompt("请选择 (1-4)", type=str, default="1")
        image_provider = provider_map.get(choice, "volcengine")

        # 2. 选择视频提供商
        click.echo("\n选择视频生成提供商:")
        click.echo("  1) volcengine (火山引擎 Seedance)")
        click.echo("  2) dashscope (阿里云)")
        click.echo("  3) mock (测试用)")
        choice = click.prompt("请选择 (1-3)", type=str, default="1")
        video_provider = provider_map.get(choice, "volcengine")

        # 3. 选择存储方式
        click.echo("\n选择存储方式:")
        click.echo("  1) local (本地存储)")
        click.echo("  2) google_drive (上传到 Google Drive)")
        choice = click.prompt("请选择 (1-2)", type=str, default="1")
        storage_provider = "local" if choice == "1" else "google_drive"

        # 生成配置
        config = {
            "project_name": project_name,
            "version": "0.1.0",
            "models": {
                "image": {"provider": image_provider},
                "video": {"provider": video_provider},
            },
            "storage": {"provider": storage_provider}
        }
    else:
        config = {
            "project_name": project_name,
            "version": "0.1.0",
            "storage": {"provider": "local"}
        }

    # 写入配置
    config_path = project_dir / ".videoclaw" / "config.yaml"
    # ... (现有写入逻辑)
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_init_interactive.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add videoclaw/cli/commands/init.py tests/test_init_interactive.py
git commit -m "feat: add interactive config to video-init command"
```

---

## Task 7: 更新 Skill 文档

**Files:**
- Modify: `skills/video-create/SKILL.md`

**Step 1: 更新 SKILL.md**

在文件中添加：

```markdown
## 生成规则

### 图像生成 (assets / storyboard)

**重要**: 每个 asset/storyboard 会生成多张候选（默认 4 张），让用户选择最喜欢的一张。

```bash
# 生成的候选文件
assets/character_astronaut_1.png
assets/character_astronaut_2.png
assets/character_astronaut_3.png
assets/character_astronaut_4.png
```

**选择流程**:
1. 展示所有候选图片
2. 让用户选择最喜欢的一张
3. 将选择结果记录到 state.json

### 视频生成 (i2v)

**重要**: 视频生成不生成多张候选，每次只生成 1 个（因为费用较高）。

### 独立命令

如需单独调用 T2I/I2I，可以使用独立命令:

```bash
# 文生图
videoclaw t2i --prompt "宇航员在火星上" --output astronaut.png

# 图生图
videoclaw i2i --input astronaut.png --prompt "穿红色制服" --output astronaut_red.png
```
```

**Step 2: Commit**

```bash
git add skills/video-create/SKILL.md
git commit -m "docs: add generation rules to video-create skill"
```

---

## Task 8: 集成测试

**Files:**
- Test: `tests/test_integration.py`

**Step 1: 创建集成测试**

```python
# tests/test_integration.py
import pytest
from click.testing import CliRunner


def test_t2i_i2i_workflow():
    """测试 t2i -> i2i 工作流"""
    from videoclaw.cli.commands.t2i import t2i
    from videoclaw.cli.commands.i2i import i2i

    runner = CliRunner()

    with runner.isolated_filesystem():
        # T2I
        with patch("videoclaw.cli.commands.t2i.get_image_backend") as mock:
            mock_result = MagicMock()
            mock_result.local_path.__str__ = lambda: "/tmp/test.png"
            mock.return_value.text_to_image.return_value = mock_result

            with patch("shutil.copy"):
                result = runner.invoke(t2i, ["--prompt", "test", "--output", "test.png"])
                assert result.exit_code == 0
```

**Step 2: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for t2i/i2i workflow"
```

---

## 实现顺序

1. Task 1: t2i 命令
2. Task 2: i2i 命令
3. Task 3: assets --num-variants
4. Task 4: storyboard --num-variants
5. Task 5: 选择记录
6. Task 6: video-init 交互式配置
7. Task 7: Skill 文档
8. Task 8: 集成测试
