# Logging System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 Videoclaw 项目添加可配置的日志系统，支持多级别、双输出、按日期归档

**Architecture:**
- 使用 Python 标准库 logging
- 创建 Logger 工具类封装常用操作
- 双输出：控制台 (stdout) + 文件 (按日期)
- 支持通过配置文件设置日志级别

**Tech Stack:** Python logging 标准库

---

## Task 1: 创建日志工具模块

**Files:**
- Create: `videoclaw/utils/logging.py`

**Step 1: 创建 logging.py**

```python
"""日志工具模块"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class VideoclawLogger:
    """Videoclaw 日志工具类"""

    def __init__(self, project_path: Optional[Path] = None, name: str = "videoclaw"):
        self.name = name
        self.logger = None
        self.project_path = project_path

    def setup(
        self,
        console_level: int = logging.INFO,
        file_level: int = logging.INFO,
    ) -> logging.Logger:
        """设置日志器"""
        # 创建 logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)  # 最低级别，让 handler 过滤
        logger.handlers.clear()

        # 格式化
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台 Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件 Handler（如果提供了项目路径）
        if self.project_path:
            log_dir = self.project_path / ".videoclaw" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(file_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self.logger = logger
        return logger

    def get_logger(self) -> logging.Logger:
        """获取 logger"""
        if self.logger is None:
            return self.setup()
        return self.logger


# 全局 logger 缓存
_loggers: dict = {}


def get_logger(project_path: Optional[Path] = None, name: str = "videoclaw") -> logging.Logger:
    """获取项目日志器"""
    key = str(project_path) if project_path else "global"

    if key not in _loggers:
        logger_obj = VideoclawLogger(project_path, name)
        _loggers[key] = logger_obj.setup()

    return _loggers[key]
```

**Step 2: 写测试**

```python
# tests/test_logging.py
import pytest
from pathlib import Path
from videoclaw.utils.logging import get_logger, VideoclawLogger


def test_logger_creation():
    """测试日志器创建"""
    logger = get_logger(name="test")
    assert logger is not None
    assert logger.name == "test"


def test_logger_with_project(tmp_path):
    """测试带项目路径的日志器"""
    logger = get_logger(project_path=tmp_path, name="test-project")
    assert logger is not None
    # 检查日志目录是否创建
    log_dir = tmp_path / ".videoclaw" / "logs"
    assert log_dir.exists()
```

**Step 3: 运行测试**

```bash
python3 -m pytest tests/test_logging.py -v
```

**Step 4: Commit**

```bash
git add videoclaw/utils/logging.py tests/test_logging.py
git commit -m "feat: add logging utility module"
```

---

## Task 2: 在 CLI 命令中集成日志

**Files:**
- Modify: `videoclaw/cli/commands/assets.py`
- Modify: `videoclaw/cli/commands/storyboard.py`
- Modify: `videoclaw/cli/commands/i2v.py`
- Modify: `videoclaw/cli/commands/audio.py`
- Modify: `videoclaw/cli/commands/merge.py`

**Step 1: 修改 assets.py 添加日志**

在文件开头添加导入：
```python
from videoclaw.utils.logging import get_logger
```

在命令函数中添加：
```python
@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
def assets(project: str):
    """生成角色和场景图片资产"""
    project_path = DEFAULT_PROJECTS_DIR / project
    logger = get_logger(project_path)

    if not project_path.exists():
        logger.error(f"项目 {project} 不存在")
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    logger.info(f"开始生成资产，项目: {project}")
    # ... 原有代码 ...

    logger.info(f"资产生成完成")
```

**Step 2: 类似修改其他命令**

在 storyboard.py, i2v.py, audio.py, merge.py 中做类似修改。

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/
git commit -m "feat: integrate logging into CLI commands"
```

---

## Task 3: 在模型后端中添加日志

**Files:**
- Modify: `videoclaw/models/volcengine/seedream.py`
- Modify: `videoclaw/models/volcengine/seedance.py`
- Modify: `videoclaw/models/volcengine/tts.py`
- Modify: `videoclaw/models/dashscope/t2i.py`
- Modify: `videoclaw/models/dashscope/i2v.py`
- Modify: `videoclaw/models/dashscope/tts.py`

**Step 1: 修改 seedream.py**

在文件开头添加导入，然后在关键位置添加日志：
```python
from volcengine.utils.logging import get_logger

logger = get_logger(name="volcengine.seedream")

def text_to_image(self, prompt: str, **kwargs):
    logger.info(f"开始生成图片，prompt: {prompt[:50]}...")
    try:
        # ... API 调用 ...
        logger.info(f"图片生成成功")
    except Exception as e:
        logger.error(f"图片生成失败: {e}")
        raise
```

**Step 2: 类似修改其他模型文件**

**Step 3: Commit**

```bash
git add videoclaw/models/
git commit -m "feat: add logging to model backends"
```

---

## Task 4: 添加日志配置支持

**Files:**
- Modify: `videoclaw/config/loader.py` 或添加新配置逻辑
- Modify: `videoclaw/cli/commands/config.py`

**Step 1: 在配置中添加日志级别设置**

在 config.py 中添加日志相关配置项：
```python
@main.command()
@click.option("--project", "-p", help="项目名称")
@click.option("--get", "get_value", help="获取配置项")
@click.option("--set", "set_value", help="设置配置项 (key=value)")
def config(project: Optional[str], get_value: Optional[str], set_value: Optional[str]):
    # ... 现有代码 ...

    # 添加日志配置示例
    # videoclaw config --project my-project --set logging.level=DEBUG
```

**Step 2: 修改 get_logger 读取配置**

更新 `videoclaw/utils/logging.py` 的 `get_logger` 函数，读取配置中的日志级别：

```python
def get_logger(project_path: Optional[Path] = None, name: str = "videoclaw") -> logging.Logger:
    """获取项目日志器"""
    # 尝试读取配置
    console_level = logging.INFO
    file_level = logging.INFO

    if project_path:
        config_file = project_path / ".videoclaw" / "config.yaml"
        if config_file.exists():
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f) or {}
            console_level_str = config.get("logging", {}).get("level", "INFO")
            file_level_str = config.get("logging", {}).get("file_level", "INFO")
            console_level = getattr(logging, console_level_str, logging.INFO)
            file_level = getattr(logging, file_level_str, logging.INFO)

    # ... 后续代码 ...
```

**Step 3: Commit**

```bash
git add videoclaw/utils/logging.py videoclaw/cli/commands/config.py
git commit -m "feat: add logging configuration support"
```

---

## Task 5: 最终验证

**Step 1: 初始化新项目测试**

```bash
videoclaw init log-test
```

**Step 2: 检查日志目录**

```bash
ls -la ~/videoclaw-projects/log-test/.videoclaw/logs/
```

**Step 3: 运行命令并检查日志**

```bash
videoclaw assets --project log-test
cat ~/videoclaw-projects/log-test/.videoclaw/logs/$(date +%Y-%m-%d).log
```

**Step 4: 测试配置修改**

```bash
videoclaw config --project log-test --set logging.level=DEBUG
videoclaw assets --project log-test
# 检查 DEBUG 级别日志是否出现
```

**Step 5: 运行测试**

```bash
python3 -m pytest tests/ -v
```

**Step 6: Commit**

```bash
git add -A
git commit -m "chore: complete logging system implementation"
```
