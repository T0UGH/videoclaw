# 社交媒体发布功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现视频发布到抖音、快手功能，包含 CLI 命令和 Skill

**Architecture:** 使用 Playwright 浏览器自动化，实现 publisher 模块 + CLI 命令 + Skills

**Tech Stack:** Python, Click, Playwright

---

## Task 1: 添加 playwright 依赖

**Files:**
- Modify: `pyproject.toml`

**Step 1: 添加依赖**

修改 `pyproject.toml`，在 dependencies 中添加：

```toml
playwright>=1.40.0
```

**Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: 添加 playwright 依赖"
```

---

## Task 2: 创建 publisher 模块基类

**Files:**
- Create: `videoclaw/publisher/__init__.py`
- Create: `videoclaw/publisher/base.py`

**Step 1: 创建 __init__.py**

```python
"""Publisher 模块 - 社交媒体发布"""

from videoclaw.publisher.base import Publisher

__all__ = ["Publisher"]
```

**Step 2: 创建 base.py**

```python
"""Publisher 基类"""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    video_url: Optional[str] = None
    error: Optional[str] = None


class Publisher(ABC):
    """Publisher 基类"""

    def __init__(self, cookie_dir: Path, headless: bool = True):
        self.cookie_dir = cookie_dir
        self.headless = headless

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名称"""
        pass

    @property
    @abstractmethod
    def creator_url(self) -> str:
        """创作者中心 URL"""
        pass

    @property
    @abstractmethod
    def upload_url(self) -> str:
        """上传页面 URL"""
        pass

    def get_cookie_path(self, account: str = "default") -> Path:
        """获取 cookie 文件路径"""
        return self.cookie_dir / f"{account}.json"

    def cookie_exists(self, account: str = "default") -> bool:
        """检查 cookie 是否存在"""
        return self.get_cookie_path(account).exists()

    @abstractmethod
    async def login(self, account: str = "default") -> bool:
        """登录账号"""
        pass

    @abstractmethod
    async def publish(
        self,
        video_path: Path,
        title: str,
        tags: list[str],
        cover_path: Optional[Path] = None,
        account: str = "default",
    ) -> PublishResult:
        """发布视频"""
        pass
```

**Step 3: Commit**

```bash
git add videoclaw/publisher/
git commit -m "feat(publisher): 添加 publisher 模块基类"
```

---

## Task 3: 创建 cookie_manager 模块

**Files:**
- Create: `videoclaw/publisher/cookie_manager.py`

**Step 1: 创建 cookie_manager.py**

```python
"""Cookie 管理模块"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


async def login_and_save_cookie(
    url: str,
    cookie_path: Path,
    headless: bool = False,
) -> bool:
    """登录并保存 cookie

    Args:
        url: 登录页面 URL
        cookie_path: 保存 cookie 的路径
        headless: 是否使用 headless 模式

    Returns:
        登录是否成功
    """
    cookie_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)
        await page.pause()  # 用户扫码登录

        await context.storage_state(path=str(cookie_path))
        await browser.close()

        return cookie_path.exists()


async def validate_cookie(
    url: str,
    cookie_path: Path,
    headless: bool = True,
) -> bool:
    """验证 cookie 是否有效

    Args:
        url: 验证页面 URL
        cookie_path: cookie 文件路径
        headless: 是否使用 headless 模式

    Returns:
        cookie 是否有效
    """
    if not cookie_path.exists():
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(storage_state=str(cookie_path))
        page = await context.new_page()

        await page.goto(url)
        await asyncio.sleep(2)

        # 检查是否跳转到登录页
        if "login" in page.url.lower():
            return False

        await browser.close()
        return True
```

**Step 2: Commit**

```bash
git add videoclaw/publisher/cookie_manager.py
git commit -m "feat(publisher): 添加 cookie 管理模块"
```

---

## Task 4: 创建抖音发布器

**Files:**
- Create: `videoclaw/publisher/douyin.py`

**Step 1: 创建 douyin.py**

```python
"""抖音发布器"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright

from videoclaw.publisher.base import Publisher, PublishResult
from videoclaw.publisher.cookie_manager import validate_cookie


class DouYinPublisher(Publisher):
    """抖音发布器"""

    @property
    def platform_name(self) -> str:
        return "douyin"

    @property
    def creator_url(self) -> str:
        return "https://creator.douyin.com/"

    @property
    def upload_url(self) -> str:
        return "https://creator.douyin.com/creator-micro/content/upload"

    async def login(self, account: str = "default") -> bool:
        """登录抖音账号"""
        from videoclaw.publisher.cookie_manager import login_and_save_cookie
        return await login_and_save_cookie(
            url=self.creator_url,
            cookie_path=self.get_cookie_path(account),
            headless=False,
        )

    async def publish(
        self,
        video_path: Path,
        title: str,
        tags: list[str],
        cover_path: Optional[Path] = None,
        account: str = "default",
    ) -> PublishResult:
        """发布视频到抖音"""
        cookie_path = self.get_cookie_path(account)

        if not cookie_path.exists():
            return PublishResult(
                success=False,
                error=f"请先登录: videoclaw publish login douyin --account {account}"
            )

        # 验证 cookie
        valid = await validate_cookie(self.upload_url, cookie_path, self.headless)
        if not valid:
            return PublishResult(
                success=False,
                error="Cookie 已失效，请重新登录"
            )

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(storage_state=str(cookie_path))
            page = await context.new_page()

            try:
                # 1. 访问上传页面
                await page.goto(self.upload_url)

                # 2. 上传视频
                await page.wait_for_selector('input[type="file"]', timeout=10000)
                await page.set_input_files('input[type="file"]', str(video_path))

                # 3. 等待上传完成
                await asyncio.sleep(5)  # 简化处理

                # 4. 填写标题
                title_input = page.locator('input[placeholder*="标题"]')
                if await title_input.count():
                    await title_input.fill(title[:100])

                # 5. 填写话题
                for tag in tags:
                    await page.keyboard.type(f"#{tag}")
                    await page.keyboard.press("Space")

                # 6. 上传封面（如果有）
                if cover_path and cover_path.exists():
                    # TODO: 实现封面上传
                    pass

                # 7. 点击发布
                publish_btn = page.locator('button:has-text("发布")')
                await publish_btn.click()

                # 8. 等待发布完成
                await page.wait_for_url("**/success**", timeout=30000)

                return PublishResult(success=True)

            except Exception as e:
                return PublishResult(success=False, error=str(e))
            finally:
                await browser.close()
```

**Step 2: Commit**

```bash
git add videoclaw/publisher/douyin.py
git commit -m "feat(publisher): 添加抖音发布器"
```

---

## Task 5: 创建快手发布器

**Files:**
- Create: `videoclaw/publisher/kuaishou.py`

**Step 1: 创建 kuaishou.py**

```python
"""快手发布器"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from videoclaw.publisher.base import Publisher, PublishResult


class KuaishouPublisher(Publisher):
    """快手发布器"""

    @property
    def platform_name(self) -> str:
        return "kuaishou"

    @property
    def creator_url(self) -> str:
        return "https://cp.kuaishou.com/"

    @property
    def upload_url(self) -> str:
        return "https://cp.kuaishou.com/feed/publish"

    async def login(self, account: str = "default") -> bool:
        """登录快手账号"""
        from videoclaw.publisher.cookie_manager import login_and_save_cookie
        return await login_and_save_cookie(
            url=self.creator_url,
            cookie_path=self.get_cookie_path(account),
            headless=False,
        )

    async def publish(
        self,
        video_path: Path,
        title: str,
        tags: list[str],
        cover_path: Optional[Path] = None,
        account: str = "default",
    ) -> PublishResult:
        """发布视频到快手"""
        # TODO: 实现快手发布逻辑
        return PublishResult(success=False, error="快手发布器尚未实现")
```

**Step 2: Commit**

```bash
git add videoclaw/publisher/kuaishou.py
git commit -m "feat(publisher): 添加快手发布器"
```

---

## Task 6: 创建 factory 模块

**Files:**
- Create: `videoclaw/publisher/factory.py`

**Step 1: 创建 factory.py**

```python
"""Publisher 工厂函数"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from videoclaw.publisher.base import Publisher
from videoclaw.publisher.douyin import DouYinPublisher
from videoclaw.publisher.kuaishou import KuaishouPublisher


def get_publisher(
    platform: str,
    cookie_dir: Optional[Path] = None,
    headless: bool = True,
) -> Publisher:
    """获取发布器实例

    Args:
        platform: 平台名称 (douyin, kuaishou)
        cookie_dir: cookie 目录
        headless: 是否使用 headless 模式

    Returns:
        发布器实例

    Raises:
        ValueError: 不支持的平台
    """
    if cookie_dir is None:
        cookie_dir = Path.home() / ".videoclaw" / "cookies" / platform

    if platform == "douyin":
        return DouYinPublisher(cookie_dir, headless)
    elif platform == "kuaishou":
        return KuaishouPublisher(cookie_dir, headless)
    else:
        raise ValueError(f"不支持的平台: {platform}")
```

**Step 2: Commit**

```bash
git add videoclaw/publisher/factory.py
git commit -m "feat(publisher): 添加 publisher 工厂函数"
```

---

## Task 7: 创建 CLI publish 命令

**Files:**
- Create: `videoclaw/cli/commands/publish.py`
- Modify: `videoclaw/cli/main.py`

**Step 1: 创建 publish.py**

```python
"""Publish 命令"""
from __future__ import annotations

import asyncio
import click
from pathlib import Path

from videoclaw.publisher.factory import get_publisher


@click.group()
def publish():
    """社交媒体发布命令"""
    pass


@publish.command()
@click.argument("platform")
@click.option("--account", default="default", help="账号名称")
def login(platform: str, account: str):
    """登录社交媒体账号

    示例:
        videoclaw publish login douyin
        videoclaw publish login kuaishou --account my_account
    """
    if platform not in ["douyin", "kuaishou"]:
        click.echo(f"不支持的平台: {platform}", err=True)
        return

    click.echo(f"正在打开 {platform} 登录页面，请扫码登录...")
    click.echo("登录成功后会自动保存 cookie")

    publisher = get_publisher(platform)

    async def run():
        success = await publisher.login(account)
        if success:
            click.echo(f"登录成功！Cookie 已保存到: {publisher.get_cookie_path(account)}")
        else:
            click.echo("登录失败", err=True)

    asyncio.run(run())


@publish.command()
@click.argument("platform")
@click.option("--video", "-v", required=True, help="视频文件路径")
@click.option("--title", "-t", required=True, help="视频标题")
@click.option("--tags", help="话题标签，逗号分隔")
@click.option("--cover", help="封面图片路径")
@click.option("--account", default="default", help="账号名称")
def upload(
    platform: str,
    video: str,
    title: str,
    tags: str,
    cover: str,
    account: str,
):
    """发布视频到社交媒体

    示例:
        videoclaw publish douyin -v video.mp4 -t "我的视频" --tags "tag1,tag2"
    """
    if platform not in ["douyin", "kuaishou"]:
        click.echo(f"不支持的平台: {platform}", err=True)
        return

    video_path = Path(video)
    if not video_path.exists():
        click.echo(f"视频文件不存在: {video}", err=True)
        return

    cover_path = Path(cover) if cover else None
    if cover_path and not cover_path.exists():
        click.echo(f"封面文件不存在: {cover}", err=True)
        return

    tags_list = [t.strip() for t in tags.split(",")] if tags else []

    publisher = get_publisher(platform)

    click.echo(f"正在发布视频到 {platform}...")

    async def run():
        result = await publisher.publish(
            video_path=video_path,
            title=title,
            tags=tags_list,
            cover_path=cover_path,
            account=account,
        )

        if result.success:
            click.echo(f"发布成功！")
            if result.video_url:
                click.echo(f"视频链接: {result.video_url}")
        else:
            click.echo(f"发布失败: {result.error}", err=True)

    asyncio.run(run())


@publish.command()
def status():
    """查看已登录账号状态"""
    click.echo("已登录的账号:")
    for platform in ["douyin", "kuaishou"]:
        cookie_dir = Path.home() / ".videoclaw" / "cookies" / platform
        if cookie_dir.exists():
            for cookie_file in cookie_dir.glob("*.json"):
                click.echo(f"  {platform}: {cookie_file.stem}")
```

**Step 2: 修改 main.py**

在 `videoclaw/cli/main.py` 中添加导入和注册命令：

```python
from videoclaw.cli.commands.publish import publish
# ...
main.add_command(publish)
```

**Step 3: Commit**

```bash
git add videoclaw/cli/commands/publish.py videoclaw/cli/main.py
git commit -m "feat(cli): 添加 publish 命令"
```

---

## Task 8: 安装 playwright 浏览器

**Step 1: 安装浏览器**

```bash
playwright install chromium
```

**Step 2: Commit**

```bash
git add -A
git commit -m "chore: 安装 playwright 浏览器"
```

---

## Task 9: 创建 video-publish-douyin Skill

**Files:**
- Create: `skills/video-publish-douyin/SKILL.md`

**Step 1: 创建 SKILL.md**

```markdown
---
description: 发布视频到抖音平台
---

# video-publish-douyin

发布视频到抖音平台。

## 使用方法

```
videoclaw publish douyin -v <video_path> -t "<title>" --tags "<tag1,tag2>"
```

## 参数

- `video_path`: 视频文件路径
- `title`: 视频标题
- `tags`: 话题标签，逗号分隔（可选）
- `cover`: 封面图片路径（可选）
- `account`: 账号名称，默认 default（可选）

## 示例

发布视频:
```
videoclaw publish douyin -v /path/to/video.mp4 -t "精彩视频"
```

带话题:
```
videoclaw publish douyin -v /path/to/video.mp4 -t "精彩视频" --tags "搞笑,日常"
```

## 前提条件

需要先登录抖音账号:
```
videoclaw publish login douyin
```
```

**Step 2: Commit**

```bash
git add skills/video-publish-douyin/
git commit -m "feat(skill): 添加 video-publish-douyin skill"
```

---

## Task 10: 创建 video-publish-kuaishou Skill

**Files:**
- Create: `skills/video-publish-kuaishou/SKILL.md`

**Step 1: 创建 SKILL.md**

```markdown
---
description: 发布视频到快手平台
---

# video-publish-kuaishou

发布视频到快手平台。

## 使用方法

```
videoclaw publish kuaishou -v <video_path> -t "<title>" --tags "<tag1,tag2>"
```

## 参数

- `video_path`: 视频文件路径
- `title`: 视频标题
- `tags`: 话题标签，逗号分隔（可选）
- `cover`: 封面图片路径（可选）
- `account`: 账号名称，默认 default（可选）

## 示例

发布视频:
```
videoclaw publish kuaishou -v /path/to/video.mp4 -t "精彩视频"
```

## 前提条件

需要先登录快手账号:
```
videoclaw publish login kuaishou
```
```

**Step 2: Commit**

```bash
git add skills/video-publish-kuaishou/
git commit -m "feat(skill): 添加 video-publish-kuaishou skill"
```

---

## Task 11: 验证功能

**Step 1: 测试 CLI 命令**

```bash
# 查看 publish 命令帮助
videoclaw publish --help

# 查看登录命令帮助
videoclaw publish login --help

# 查看上传命令帮助
videoclaw publish upload --help
```

**Step 2: 验证发布功能（可选，需要真实账号）**

```bash
# 登录抖音
videoclaw publish login douyin

# 发布视频
videoclaw publish douyin -v test.mp4 -t "测试视频"
```

**Step 3: Commit**

```bash
git add -A
git commit -m "test: 验证 publish 功能"
```
