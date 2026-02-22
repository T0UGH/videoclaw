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
