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
                await page.goto(self.upload_url, timeout=120000)

                # 2. 上传视频
                await page.wait_for_selector('input[type="file"]', timeout=60000)
                await page.set_input_files('input[type="file"]', str(video_path))

                # 3. 等待上传完成 (等待视频封面出现表示上传完成)
                await page.wait_for_selector('.video-info, .upload-item, img[src*="video"]', timeout=120000)
                await asyncio.sleep(2)  # 额外等待确保上传完成

                # 4. 填写标题 (使用 .first 处理可能有多个匹配的情况)
                title_input = page.locator('input[placeholder*="标题"]').first
                if await title_input.is_visible():
                    await title_input.fill(title[:100])

                # 5. 填写话题
                for tag in tags:
                    await page.keyboard.type(f"#{tag}")
                    await page.keyboard.press("Space")

                # 6. 上传封面（如果有）
                if cover_path and cover_path.exists():
                    # TODO: 实现封面上传
                    pass

                # 7. 点击发布 (使用精确匹配，避免匹配到"高清发布")
                publish_btn = page.locator('button:has-text("发布"):not(:has-text("高清"))')
                await publish_btn.click()

                # 等待可能的弹窗
                await asyncio.sleep(2)

                # 8. 等待发布完成 (跳转管理页即表示成功)
                await page.wait_for_url("**/manage**", timeout=30000)

                return PublishResult(success=True)

            except Exception as e:
                return PublishResult(success=False, error=str(e))
            finally:
                await browser.close()
