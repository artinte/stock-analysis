from typing import Optional
from playwright.async_api import Browser, Page, async_playwright


class BrowserManager:
    """全局单例浏览器管理器，避免反复启动 Browser 实例耗尽内存"""

    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def start(self):
        if not self._browser:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox"],
            )

    async def get_page(self) -> Page:
        # 复用 Browser，独立创建 Context，隔离 Cookie 和 Session
        context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        return await context.new_page()

    async def stop(self):
        if self._browser:
            await self._browser.close()
            await self._playwright.stop()


# 实例化全局单例
browser_manager = BrowserManager()