import os
import asyncio
from typing import List, Union
from playwright.async_api import async_playwright, Page, BrowserContext


class XiaohongshuArticlePublisher:
    """小红书专栏/文章（纯文本）全自动发布脚本"""

    def __init__(self, user_data_dir: str = "./xhs_cookie_store"):
        self.user_data_dir = os.path.abspath(user_data_dir)
        # 文章/专栏发布入口 URL
        self.entry_url = (
            "https://creator.xiaohongshu.com/publish/publish?from=menu&target=article"
        )

    async def init_context(self, playwright, headless: bool = False) -> BrowserContext:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            viewport={"width": 1440, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        return context

    async def check_login(self, page: Page) -> bool:
        await page.goto("https://creator.xiaohongshu.com/new/home")
        await page.wait_for_timeout(2000)
        return "login" not in page.url

    async def locate_and_fill_title(self, page: Page, title: str):
        """精准定位并填写标题"""
        print("[*] 1. 正在定位并填写标题...")

        title_selectors = [
            ".rich-editor-title textarea",
            "textarea[placeholder*='标题']",
            ".rich-editor-title .d-text",
            "textarea.d-text",
        ]

        title_element = None
        for selector in title_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.is_visible(timeout=3000):
                    title_element = locator
                    print(f"    [+] 使用选择器定位到标题框: {selector}")
                    break
            except Exception:
                continue

        if not title_element:
            raise RuntimeError("❌ 未能定位到标题输入框，请检查页面是否加载完成。")

        await title_element.click()
        await page.wait_for_timeout(300)
        await title_element.fill(title)
        await page.wait_for_timeout(500)

    async def locate_and_fill_content(
        self, page: Page, content_str: str, tags: List[str] = None
    ):
        """精准定位并填写正文（针对 Tiptap / ProseMirror 编辑器）"""
        print("[*] 2. 正在定位并填写正文...")

        content_selectors = [
            ".rich-editor-content .tiptap.ProseMirror",
            ".tiptap.ProseMirror",
            ".rich-editor-content [contenteditable='true']",
            "div[contenteditable='true']",
        ]

        editor_element = None
        for selector in content_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.is_visible(timeout=3000):
                    editor_element = locator
                    print(f"    [+] 使用选择器定位到正文框: {selector}")
                    break
            except Exception:
                continue

        if not editor_element:
            raise RuntimeError("❌ 未能定位到正文富文本编辑器。")

        await editor_element.click()
        await page.wait_for_timeout(300)

        # 逐字输入模拟真实用户操作
        await editor_element.press_sequentially(content_str, delay=15)

        # 添加话题标签
        if tags:
            print("[*] 3. 正在添加话题标签...")
            for tag in tags:
                await editor_element.press_sequentially(f" #{tag}", delay=30)
                await page.wait_for_timeout(600)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(400)

    async def process_layout_next_and_publish(self, page: Page):
        """三步全自动：点击一键排版 -> 点击下一步 -> 点击悬浮发布按钮"""

        # ----------------- Step A: 点击【一键排版】 -----------------
        print("[*] 4. 正在准备点击【一键排版】...")
        layout_btn_selectors = [
            "button:has-text('一键排版')",
            "button.next-btn",
            "button:has-text('排版')",
        ]

        layout_btn = None
        for selector in layout_btn_selectors:
            try:
                loc = page.locator(selector).first
                if await loc.is_visible(timeout=3000):
                    layout_btn = loc
                    break
            except Exception:
                continue

        if not layout_btn:
            raise RuntimeError("❌ 未找到【一键排版】按钮！")

        await layout_btn.click()
        print("[+] 已点击【一键排版】，开始智能等待排版渲染完成...")

        # ----------------- Step B: 等待并点击【下一步】 -----------------
        print("[*] 5. 正在等待【下一步】按钮可点击...")
        next_btn_selectors = [
            "button:has-text('下一步')",
            "button.next-btn",
            "button.ce-btn.bg-red:has-text('下一步')",
        ]

        next_btn = None
        # 轮询等待排版完成，直到“下一步”按钮变成可点击状态（最长等待 30 秒）
        for _ in range(15):
            for selector in next_btn_selectors:
                try:
                    loc = page.locator(selector).first
                    if await loc.is_visible(timeout=1000) and await loc.is_enabled():
                        text = await loc.inner_text()
                        if "下一步" in text:
                            next_btn = loc
                            break
                except Exception:
                    continue
            if next_btn:
                break
            await page.wait_for_timeout(2000)

        if not next_btn:
            raise RuntimeError("❌ 等待一键排版超时，未能出现【下一步】按钮！")

        print("[+] 排版完成，正在点击【下一步】...")
        await next_btn.click()

        # ----------------- Step C: 定位并点击悬浮的【发布】按钮 -----------------
        print("[*] 6. 等待页面加载，定位悬浮【发布】按钮...")

        # 针对您提供的 exact HTML DOM 精准定位：
        # <button type="button" class="ce-btn bg-red" aria-busy="false" aria-disabled="false">发布</button>
        publish_btn_selectors = [
            "button.ce-btn.bg-red:has-text('发布')",
            "button.ce-btn:has-text('发布')",
            "button[aria-disabled='false']:has-text('发布')",
            "button.bg-red:has-text('发布')",
        ]

        publish_btn = None
        for _ in range(12):  # 等待页面动画及悬浮层加载，最长等待 12 秒
            for selector in publish_btn_selectors:
                try:
                    loc = page.locator(selector).first
                    if await loc.is_visible(timeout=1000):
                        aria_disabled = await loc.get_attribute("aria-disabled")
                        if aria_disabled != "true":
                            publish_btn = loc
                            print(f"    [+] 成功精准定位到悬浮【发布】按钮: {selector}")
                            break
                except Exception:
                    continue
            if publish_btn:
                break
            await page.wait_for_timeout(1000)

        if not publish_btn:
            raise RuntimeError("❌ 未能定位到悬浮的【发布】按钮！")

        print("[+] 正在点击悬浮【发布】按钮...")
        # 防遮挡点击策略：强制触发点击事件
        await publish_btn.click(force=True)

        # ----------------- Step D: 校验发布结果 -----------------
        print("[*] 7. 等待系统响应发布结果...")
        try:
            await page.wait_for_url("**/new/home**", timeout=15000)
            print("🎉🎉🎉 恭喜！全流程自动化执行完成，文章已成功发布！")
        except Exception:
            await page.wait_for_timeout(3000)
            print("✅ 发布指令已成功发送！")

    async def publish_article(
        self,
        title: str,
        content: Union[str, tuple, list],
        tags: List[str] = None,
    ):
        """发布文章完整全自动主流程"""
        if isinstance(content, (tuple, list)):
            content_str = (
                "\n".join(content) if isinstance(content, list) else "".join(content)
            )
        else:
            content_str = str(content)

        async with async_playwright() as p:
            context = await self.init_context(p, headless=False)
            page = context.pages[0] if context.pages else await context.new_page()

            # 1. 登录校验
            if not await self.check_login(page):
                print("[!] 未检测到有效登录状态，请在打开的浏览器中扫码登录...")
                await page.goto("https://creator.xiaohongshu.com/login")
                await page.wait_for_url("**/new/home", timeout=120000)
                print("[+] 登录成功！")

            # 2. 导航到专栏/文章发布入口
            print("[*] 正在导航至文章发布页面...")
            await page.goto(self.entry_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            # 3. 处理“新的创作”弹窗
            try:
                create_btn = page.locator("text='新的创作'").first
                if await create_btn.is_visible(timeout=3000):
                    await create_btn.click()
                    await page.wait_for_timeout(1000)
            except Exception:
                pass

            # 4. 填写标题和正文
            await self.locate_and_fill_title(page, title)
            await self.locate_and_fill_content(page, content_str, tags)
            await page.wait_for_timeout(1000)

            # 5. 执行：一键排版 -> 下一步 -> 悬浮发布按钮
            await self.process_layout_next_and_publish(page)

            await page.wait_for_timeout(3000)
            await context.close()


if __name__ == "__main__":
    publisher = XiaohongshuArticlePublisher(user_data_dir="./xhs_cookie_store")

    test_title = "杭氧股份 2026 Q2 业绩预测硬核拆解"
    test_content = (
        "截至目前，我会给杭氧股份 2026Q2：\n\n"
        "营收：39.5～41.5亿元\n"
        "归母净利润：2.95～3.20亿元\n"
        "中性预测：营收40.5亿元，归母净利润约3.08亿元\n\n"
        "我认为：\n"
        "2.8亿以下：偏弱\n"
        "3.0亿左右：合理\n"
        "3.1亿左右：我目前最倾向\n"
        "3.2亿以上：偏强\n"
        "3.3亿以上：需要明显超预期\n"
    )
    test_tags = ["杭氧股份", "股票分析"]

    asyncio.run(
        publisher.publish_article(
            title=test_title,
            content=test_content,
            tags=test_tags,
        )
    )
