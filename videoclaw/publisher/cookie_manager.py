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

        await page.goto(url, timeout=120000)  # 2分钟超时

        print("\n请在浏览器中扫码登录，程序将自动检测登录状态...")

        # 等待用户扫码登录，检测 localStorage 中的登录状态
        max_wait = 120  # 最多等待2分钟
        waited = 0
        while waited < max_wait:
            await asyncio.sleep(2)
            try:
                # 检查 localStorage 中的登录状态
                login_status = await page.evaluate("() => localStorage.getItem('LOGIN_STATUS')")
                if login_status and "logintype" in login_status:
                    print("检测到登录成功!")
                    break
            except Exception:
                pass
            waited += 2
            if waited % 10 == 0:
                print(f"等待登录中... ({waited}秒)")
        else:
            print("登录超时，请重试")
            await browser.close()
            return False

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

        await page.goto(url, timeout=120000)  # 2分钟超时
        await asyncio.sleep(2)

        # 检查是否跳转到登录页
        if "login" in page.url.lower():
            return False

        await browser.close()
        return True
