# CLI 增强设计 - 阶段一

> **目标**: 改善用户体验，解决 problem.md 中的高频问题

## 问题背景

| # | 问题 | 现状 |
|---|------|------|
| 1 | 生成多张供选择 | 每个 asset/storyboard 只生成 1 张 |
| 2-3 | 独立 t2i/i2i 命令 | 缺失，agent 只能写临时脚本 |
| 6 | Asset/Frame 选择记录 | 无相关字段 |
| 7 | video-init 无交互配置 | 只有基本 init |

---

## 设计方案

### Task 1: CLI 增加 `--num-variants` 参数

**目标**: asset/storyboard 命令支持一次生成多张候选

#### 修改文件

- `videoclaw/cli/commands/assets.py`
- `videoclaw/cli/commands/storyboard.py`

#### 实现细节

```python
# assets.py / storyboard.py 新增参数
@click.option("--num-variants", "-n", default=1, type=int, help="生成候选数量 (默认1)")
```

**生成逻辑**:
```python
# 生成 n 张候选
variants = []
for i in range(num_variants):
    result = image_backend.text_to_image(prompt)
    # 存储为 character_name_{i+1}.png
    dest = dest_path.parent / f"{stem}_{i+1}{suffix}"
    shutil.copy(result.local_path, dest)
    variants.append(str(dest))

# 如果有多张，写入 state.json
if num_variants > 1:
    state_manager.update_step("assets", {
        "status": "completed",
        "variants": variants,  # 所有候选
        "chosen": variants[0]   # 默认选第一张
    })
```

**文件命名**:
- `character_astronaut.png` → `character_astronaut_1.png`, `character_astronaut_2.png` ...

#### 注意事项

- 视频生成（i2v）不使用此参数，保持单张生成（费钱）
- 记录所有 variants 到 state.json，供后续选择

---

### Task 2: 新增独立 t2i/i2i 命令

**目标**: 提供独立 CLI 命令供 agent 调用微调

#### 新增文件

- `videoclaw/cli/commands/t2i.py`
- `videoclaw/cli/commands/i2i.py`

#### t2i.py 设计

```python
"""独立文生图命令"""
import click
from pathlib import Path
from videoclaw.config.loader import Config
from videoclaw.models.factory import get_image_backend


@click.command()
@click.option("--prompt", "-p", required=True, help="生成提示词")
@click.option("--output", "-o", required=True, help="输出文件路径")
@click.option("--provider", default="volcengine", help="模型提供商: dashscope, volcengine, gemini, mock")
@click.option("--model", help="模型名称")
def t2i(prompt, output, provider, model):
    """文生图 - 独立命令"""
    config = Config()
    model = model or config.get(f"models.{provider}.model")

    backend = get_image_backend(provider, model, {
        "api_key": config.get(f"{provider}.api_key"),
    })

    result = backend.text_to_image(prompt)
    shutil.copy(result.local_path, output)
    click.echo(f"Generated: {output}")
```

#### i2i.py 设计

```python
"""独立图生图命令"""
import click
from pathlib import Path
from videoclaw.config.loader import Config
from videoclaw.models.factory import get_image_backend


@click.command()
@click.option("--input", "-i", "input_path", required=True, help="输入图片路径")
@click.option("--prompt", "-p", required=True, help="生成提示词")
@click.option("--output", "-o", required=True, help="输出文件路径")
@click.option("--provider", default="volcengine", help="模型提供商")
@click.option("--model", help="模型名称")
def i2i(input_path, prompt, output, provider, model):
    """图生图 - 独立命令"""
    config = Config()
    model = model or config.get(f"models.{provider}.model")

    backend = get_image_backend(provider, model, {
        "api_key": config.get(f"{provider}.api_key"),
    })

    image_bytes = Path(input_path).read_bytes()
    result = backend.image_to_image(image_bytes, prompt)
    shutil.copy(result.local_path, output)
    click.echo(f"Generated: {output}")
```

#### 注册命令

在 `main.py` 中注册:
```python
from videoclaw.cli.commands import t2i, i2v

cli.add_command(t2i.t2i)
cli.add_command(i2i.i2i)
```

---

### Task 3: Asset/Frame 选择记录

**目标**: 在 state.json 中记录用户的选择和候选

#### 修改文件

- `videoclaw/state/manager.py`

#### 新增数据结构

```python
# state.json 新增 selections 字段
{
    "project_id": "demo",
    "status": "assets_completed",
    "steps": {
        "assets": {
            "status": "completed",
            "output": {...}
        }
    },
    "selections": {
        "assets": {
            "chosen": "assets/character_astronaut_1.png",
            "alternatives": [
                "assets/character_astronaut_1.png",
                "assets/character_astronaut_2.png",
                "assets/character_astronaut_3.png",
                "assets/character_astronaut_4.png"
            ]
        },
        "storyboard": {
            "chosen": "storyboard/frame_001_1.png",
            "alternatives": [...]
        }
    }
}
```

#### 实现

```python
class StateManager:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.state_file = project_path / ".videoclaw" / "state.json"
        self._load()

    def update_selection(self, step: str, chosen: str, alternatives: list):
        """更新用户选择"""
        if "selections" not in self._state:
            self._state["selections"] = {}

        self._state["selections"][step] = {
            "chosen": chosen,
            "alternatives": alternatives
        }
        self._save()

    def get_selection(self, step: str) -> Optional[dict]:
        """获取选择"""
        return self._state.get("selections", {}).get(step)

    def get_all_alternatives(self) -> list:
        """获取所有候选（可用于参考）"""
        alternatives = []
        for step, data in self._state.get("selections", {}).items():
            alternatives.extend(data.get("alternatives", []))
        return alternatives
```

---

### Task 4: video-init 交互式配置

**目标**: 初始化时让用户配置 provider、API key、存储方式

#### 修改文件

- `videoclaw/cli/commands/init.py`

#### 实现

```python
import click
from videoclaw.config.loader import Config


@click.command()
@click.argument("project_name")
@click.option("--dir", default="~/videoclaw-projects", help="项目根目录")
@click.option("--interactive/--no-interactive", default=True, help="交互式配置")
def init(project_name, dir, interactive):
    """初始化项目"""
    # ... 现有逻辑 ...

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
        # 非交互模式使用默认值
        config = {...}

    # 写入配置
    config_path = project_dir / ".videoclaw" / "config.yaml"
    # ...
```

---

### Task 5: 更新 Skill 文档

**目标**: 在 video-create SKILL.md 中说明四选一规则

#### 修改文件

- `skills/video-create/SKILL.md`

#### 新增内容

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

---

## 实现顺序

1. Task 2: 独立 t2i/i2i 命令（最简单，先做）
2. Task 1: `--num-variants` 参数
3. Task 3: 选择记录
4. Task 4: video-init 交互式配置
5. Task 5: 更新 Skill 文档

---

## 测试验证

```bash
# 测试 t2i 命令
videoclaw t2i --prompt "宇航员" --output /tmp/test.png

# 测试 i2i 命令
videoclaw i2i --input /tmp/test.png --prompt "穿红色制服" --output /tmp/test2.png

# 测试多候选生成
videoclaw assets --project test --num-variants 4

# 测试交互式 init
videoclaw init new-project
```
