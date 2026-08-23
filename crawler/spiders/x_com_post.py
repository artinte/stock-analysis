import os
import re
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from playwright.async_api import async_playwright, Page, BrowserContext

# ==============================================================================
# 引入项目中已存在的基类与数据模型
# ==============================================================================
from crawler.core.base_spider import BaseSpider
from crawler.core.models import ArticleItem


# ==============================================================================
# 1. X (原 Twitter) 抓取通用基类 (支持登录态复用与时间范围过滤)
# ==============================================================================
class BaseXSpider(BaseSpider):
    username: str = ""
    auth_state_path: str = "x_auth.json"  # Cookies 配置文件

    def __init__(self):
        super().__init__()
        if self.username:
            self.start_url = f"https://x.com/{self.username}"

    async def create_context(self, browser) -> BrowserContext:
        """创建携带防封 User-Agent 以及登录凭证的上下文环境"""
        kwargs = {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "viewport": {"width": 1280, "height": 900},
        }

        # 加载本地 Cookies/StorageState 避免弹出强制登录卡片
        if os.path.exists(self.auth_state_path):
            kwargs["storage_state"] = self.auth_state_path

        return await browser.new_context(**kwargs)

    def parse_datetime(self, datetime_str: Optional[str]) -> str:
        """解析 ISO 时间戳 (如 2026-08-10T12:34:56.000Z) 为标准时间格式"""
        if not datetime_str:
            return ""
        try:
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []

        # 1. 访问用户主页
        print(f"[{self.name}] 正在打开 x.com 主页: {self.start_url}")
        try:
            await page.goto(self.start_url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"[{self.name}] 打开页面时遭遇警告/超时: {e}")

        # 2. 等待帖文 DOM 树加载
        try:
            await page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
            # 适度下翻一屏，激活 x.com 的惰性加载机制
            await page.evaluate("window.scrollBy(0, 600)")
            await page.wait_for_timeout(2000)
        except Exception:
            print(f"[{self.name}] ⚠️ 未检测到帖文组件！可能是未登录拦截或触发了 x.com 的风控。")
            return items

        # 3. 检索页面内所有帖文卡片
        tweet_locators = page.locator('article[data-testid="tweet"]')
        count = await tweet_locators.count()
        print(f"[{self.name}] 检索到 {count} 条潜在帖文，开始解析...")

        # 设定期限：>= 昨天 00:00:00（包含今天及未来挂出/置顶的帖文）
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        for i in range(count):
            tweet = tweet_locators.nth(i)

            # 区分是否为转帖 (Repost)
            is_repost = await tweet.locator('div[data-testid="socialContext"]').count() > 0

            # 4. 提取发布时间节点
            time_node = tweet.locator("time").first
            if await time_node.count() == 0:
                continue

            iso_time = await time_node.get_attribute("datetime")
            published_at = self.parse_datetime(iso_time)

            # 时间过滤逻辑：早于昨天的帖文直接过滤
            if published_at:
                pub_date_str = published_at.split(" ")[0]
                if pub_date_str < start_date:
                    continue

            # 5. 提取帖文 URL
            a_node = time_node.locator("xpath=..")
            tweet_href = await a_node.get_attribute("href") or ""
            full_url = f"https://x.com{tweet_href}" if tweet_href else self.start_url

            # 6. 提取文本内容
            text_node = tweet.locator('div[data-testid="tweetText"]').first
            tweet_text = ""
            if await text_node.count() > 0:
                tweet_text = (await text_node.inner_text()).strip()

            if not tweet_text and not tweet_href:
                continue

            # 清理多余空格与换行
            clean_text = re.sub(r"\s+", " ", tweet_text)
            prefix = "[转帖] " if is_repost else ""
            display_title = f"[{self.name}] {prefix}{clean_text[:120]}"

            items.append(
                ArticleItem(
                    source_name=f"x.com-{self.name}",
                    title=display_title,
                    url=full_url,
                    related_companies=[self.name],
                    published_at=published_at,
                    category="社交媒体",
                )
            )

        return items


# ==============================================================================
# 2. 拓展具体名人爬虫类 (只需指定 name 和 username 即可快速拓展)
# ==============================================================================
class ElonMuskXSpider(BaseXSpider):
    name = "埃隆·马斯克"
    username = "elonmusk"


class TimCookXSpider(BaseXSpider):
    name = "蒂姆·库克"
    username = "tim_cook"


class SamAltmanXSpider(BaseXSpider):
    name = "山姆·奥特曼"
    username = "sama"


# ==============================================================================
# 3. 辅助工具：初始化保存 x.com 登录凭证
# ==============================================================================
async def init_x_session(save_path: str = "x_auth.json"):
    """第一次运行或 Cookies 失效时，调用此函数手动登录并保存 State"""
    async with async_playwright() as p:
        print("🚀 正在启动有头浏览器，请在弹出的窗口中登录 x.com...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://x.com/i/flow/login")
        print("⌛ 请在浏览器中完成登录操作（限时 60 秒）...")
        await page.wait_for_timeout(60000)

        await context.storage_state(path=save_path)
        print(f"🎉 登录状态成功导出保存至: {save_path}")
        await browser.close()


# ==============================================================================
# 4. 独立运行测试逻辑
# ==============================================================================
if __name__ == "__main__":
    AUTH_FILE = "x_auth.json"

    async def run_spiders():
        # 如果未登录过，先引导用户登录生成 Session 文件
        if not os.path.exists(AUTH_FILE):
            print("未找到 x.com 登录凭证，准备进行首次可视化登录步骤...")
            await init_x_session(AUTH_FILE)

        # 待执行的名人爬虫列表（扩展名人时加在这里）
        spiders_to_run = [
            ElonMuskXSpider(),
            TimCookXSpider(),
            SamAltmanXSpider(),
        ]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            for spider in spiders_to_run:
                # 针对每个名人独立创建带凭证的 Context 和 Page
                context = await spider.create_context(browser)
                page = await context.new_page()

                results = await spider.parse(page)

                print(f"\n================ [{spider.name}] 抓取结果 ({len(results)} 条) ================")
                for item in results:
                    print(f"📌 标题: {item.title}")
                    print(f"🔗 链接: {item.url}")
                    print(f"🕒 时间: {item.published_at}")
                    print("-" * 50)

                await context.close()

            await browser.close()

    # 启动抓取工作流
    asyncio.run(run_spiders())
