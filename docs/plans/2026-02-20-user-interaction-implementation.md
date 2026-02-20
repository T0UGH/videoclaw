# 用户交互增强实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在视频创建 pipeline 中增加用户交互：Analyze 阶段 AI 追问、Assets/Storyboard 阶段生成确认与提示词优化、多图选择

**Architecture:** 修改 CLI 命令（assets.py, storyboard.py）和 video-create skill，增加交互式确认流程

**Tech Stack:** Click CLI, AskUserQuestion, StateManager

---

## Task 1: 添加配置支持

**Files:**
- Modify: `videoclaw/config/loader.py`

**Step 1: 查看现有配置加载逻辑**

```bash
head -50 videoclaw/config/loader.py
```

**Step 2: 添加 get_nested 方法**

在 Config 类中添加支持嵌套配置读取的方法：

```python
def get_nested(self, key_path: str, default=None):
    """支持点分隔的嵌套key读取，如 'assets.variants'"""
    keys = key_path.split('.')
    value = self._config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value or default
```

**Step 3: 测试**

```python
# 测试
config = Config(project_path)
print(config.get_nested("assets.variants", 1))
```

**Step 4: Commit**

```bash
git add videoclaw/config/loader.py
git commit -m "feat: add nested config get method"
```

---

## Task 2: 修改 video-create skill 支持交互式 Analyze

**Files:**
- Modify: `skills/video-create/SKILL.md`

**Step 1: 更新 skill 文档**

在执行流程中添加交互式分析步骤：

```markdown
## 执行流程

1. 调用 `videoclaw init <project-name>` 初始化项目
2. **交互式分析**：
   - 用户输入视频想法
   - AI 使用 AskUserQuestion 追问关键问题（一次一个）
   - 追问示例：
     - "这个视频想表达什么氛围？"（多选）
     - "大概多长时间？"
     - "需要几个主要角色？"
   - 追问完后确认："我理解你要做一个...的视频，这样对吗？"
   - 用户确认后生成 JSON
3. 调用 `videoclaw assets --project <project-name>` 生成资产
4. 调用 `videoclaw storyboard --project <project-name>` 生成故事板
5. 调用 `videoclaw i2v --project <project-name>` 图生视频
6. 调用 `videoclaw audio --project <project-name>` 生成音频
7. 调用 `videoclaw merge --project <project-name>` 合并视频
```

**Step 2: Commit**

```bash
git add skills/video-create/SKILL.md
git commit -m "feat: update video-create skill with interactive analyze"
```

---

## Task 3: 修改 assets 命令支持确认流程

**Files:**
- Modify: `videoclaw/cli/commands/assets.py`

**Step 1: 添加交互确认函数**

在 assets.py 中添加辅助函数：

```python
def ask_confirm_asset(image_path: str, item_name: str) -> bool:
    """询问用户生成的图片是否OK"""
    # 显示图片路径
    click.echo(f"生成完成: {image_path}")
    # 使用 AskUserQuestion
    # 这里需要调用方的上下文，所以返回让用户选择
    return None  # 占位，后续实现

def ask_adjustment() -> str:
    """询问用户哪里需要调整，返回用户输入"""
    # 使用 AskUserQuestion，开放式问题
    return None  # 占位
```

**Step 2: 修改生成角色图片逻辑**

在生成每个角色图片后添加确认循环：

```python
for char in characters:
    char_name = char.get("name", "character")
    char_desc = char.get("description", "")

    # 生成直到用户确认
    while True:
        prompt = f"宇航员角色，高清，{char_desc}"
        gen_result = image_backend.text_to_image(prompt)

        # 复制到项目目录
        dest_path = assets_dir / f"character_{char_name}.png"
        if gen_result.local_path:
            import shutil
            shutil.copy(gen_result.local_path, dest_path)

        # 询问确认（这里先显示路径）
        click.echo(f"生成角色图片: {char_name}")
        click.echo(f"  已保存: {dest_path}")
        click.echo(f"  提示词: {prompt}")

        # 询问继续还是调整
        # 暂时用 input() 代替，后续改用 AskUserQuestion
        answer = input("这个可以吗？(y/n/q退出/r调整): ")
        if answer.lower() == 'y':
            result["characters"][char_name] = str(dest_path)
            break
        elif answer.lower() == 'r':
            new_prompt = input("请输入调整后的提示词: ")
            if new_prompt:
                char_desc = new_prompt
            # 继续循环重新生成
        else:
            break
```

**Step 3: 同样修改场景生成逻辑**

类似角色生成的修改。

**Step 4: Commit**

```bash
git add videoclaw/cli/commands/assets.py
git commit -m "feat: add confirmation loop in assets command"
```

---

## Task 4: 修改 storyboard 命令支持确认流程

**Files:**
- Modify: `videoclaw/cli/commands/storyboard.py`

**Step 1: 修改生成逻辑**

类似 assets.py，在每帧生成后添加确认循环：

```python
for frame in frames:
    frame_id = frame.get("frame_id", 0)
    frame_desc = frame.get("description", "")
    camera = frame.get("camera", "")

    # 生成直到用户确认
    while True:
        prompt = f"电影镜头，{camera}，{frame_desc}，高清，电影感"
        gen_result = image_backend.text_to_image(prompt)

        # 保存
        dest_path = storyboard_dir / f"frame_{frame_id:03d}.png"
        if gen_result.local_path:
            shutil.copy(gen_result.local_path, dest_path)

        click.echo(f"生成故事板帧 {frame_id}: {frame_desc[:30]}...")
        click.echo(f"  已保存: {dest_path}")
        click.echo(f"  提示词: {prompt}")

        answer = input("这帧可以吗？(y/n/q退出/r调整): ")
        if answer.lower() == 'y':
            result["frames"].append({...})
            break
        elif answer.lower() == 'r':
            new_prompt = input("请输入调整后的提示词: ")
            if new_prompt:
                frame_desc = new_prompt
        else:
            break
```

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/storyboard.py
git commit -m "feat: add confirmation loop in storyboard command"
```

---

## Task 5: 添加本地图片支持

**Files:**
- Modify: `videoclaw/cli/commands/assets.py`

**Step 1: 添加 --use-local 选项**

```python
@click.option("--use-local", is_flag=True, help="使用本地图片，不调用T2I")
def assets(project: str, provider: str, use_local: bool):
```

**Step 2: 添加自动检测逻辑**

在生成前检查目录是否有图片：

```python
# 检查本地图片
local_char_path = assets_dir / f"character_{char_name}.png"
if use_local or local_char_path.exists():
    if use_local and not local_char_path.exists():
        click.echo(f"错误: 指定了 --use-local 但本地没有 {char_name} 的图片")
        continue
    click.echo(f"使用本地图片: {local_char_path}")
    result["characters"][char_name] = str(local_char_path)
    continue
```

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/assets.py
git commit -m "feat: support local images in assets command"
```

---

## Task 6: 添加多图生成支持

**Files:**
- Modify: `videoclaw/cli/commands/assets.py`, `videoclaw/cli/commands/storyboard.py`

**Step 1: 添加 variants 配置读取**

```python
variants = config.get_nested("assets.variants", 1)
```

**Step 2: 循环生成多张**

```python
if variants > 1:
    # 生成多张
    generated = []
    for i in range(variants):
        gen_result = image_backend.text_to_image(prompt)
        dest_path = assets_dir / f"character_{char_name}_{i}.png"
        shutil.copy(gen_result.local_path, dest_path)
        generated.append((i, dest_path))

    # 让用户选择
    click.echo("生成了以下版本:")
    for i, path in generated:
        click.echo(f"  [{i+1}] {path}")
    choice = input("选择哪个？(1/2/3...): ")
    # 选择后复制到正式路径
```

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/assets.py videoclaw/cli/commands/storyboard.py
git commit -m "feat: support multiple variants generation and selection"
```

---

## Task 7: 完善 AskUserQuestion 集成

**Files:**
- Modify: `videoclaw/cli/commands/assets.py`, `videoclaw/cli/commands/storyboard.py`

**Step 1: 替换 input() 为 AskUserQuestion**

当前使用 input() 是临时方案，后续需要集成 AskUserQuestion。

**Step 2: 测试交互流程**

实际运行 assets 命令测试。

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/assets.py videoclaw/cli/commands/storyboard.py
git commit -m "refactor: integrate AskUserQuestion for user interaction"
```

---

## 执行顺序

1. Task 1: 添加配置支持
2. Task 2: 修改 video-create skill
3. Task 3: 修改 assets 命令（基础确认循环）
4. Task 4: 修改 storyboard 命令
5. Task 5: 添加本地图片支持
6. Task 6: 添加多图生成支持
7. Task 7: 完善 AskUserQuestion 集成

---

## 注意事项

- 交互逻辑需要考虑用户输入 'q' 退出
- 提示词调整后重新生成需要更新 prompt
- 多图选择时需要保存临时文件，正式选择后再复制
- CLI flag 允许跳过交互（如 `--yes` 自动确认）
