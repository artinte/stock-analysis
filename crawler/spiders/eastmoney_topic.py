from datetime import datetime
from typing import List
from playwright.async_api import Page
from crawler.core.base_spider import BaseSpider
from crawler.core.models import ArticleItem

"""
东方财富热门话题爬虫。

抓取东方财富热门话题的标题、链接、摘要及发布时间，
并转换为统一的 ArticleItem 数据结构。

支持独立运行：
    python -m spiders.eastmoney_topic
"""


class EastMoneyTopicSpider(BaseSpider):
    name = "东方财富网"
    start_url = "https://gubatopic.eastmoney.com/"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 东方财富热点话题的完整卡片
        target_locator = page.locator(".hotTopicMsg")

        await target_locator.first.wait_for(state="visible", timeout=15000)

        await page.evaluate("window.scrollBy(0, 400)")
        await page.wait_for_timeout(1000)

        count = await target_locator.count()

        blacklist = [
            "passport",
            "login",
            "register",
            "user.eastmoney",
        ]

        for i in range(count):
            card = target_locator.nth(i)

            try:
                # 1. 提取标题
                title_el = card.locator(".topic_title a").first

                if await title_el.count() > 0:
                    title = (await title_el.inner_text()).strip().replace("\n", " ")
                else:
                    title = ""

                # 2. 提取链接
                href = None

                if await title_el.count() > 0:
                    href = await title_el.get_attribute("href")

                full_url = self.build_url(href) if href else self.start_url

                # 3. 过滤黑名单和无效标题
                if any(k in full_url for k in blacklist):
                    continue

                if not title or len(title) < 3:
                    continue

                # 4. 提取热点正文 / 摘要
                summary_el = card.locator(".item_desc").first
                content = ""

                if await summary_el.count() > 0:
                    content = (await summary_el.inner_text()).strip()

                # 5. 清理标题中可能重复的正文
                if content and content in title:
                    title = title.replace(content, "").strip()

                # 6. summary
                if len(content) < 200:
                    summary = content
                else:
                    summary = ""

                items.append(
                    ArticleItem(
                        source_name=self.name,
                        title=title,
                        url=full_url,
                        summary=summary,
                        content=content,
                        category="热门话题",
                        published_at=crawl_time,
                    )
                )

            except Exception as e:
                print(f"  ⚠️ [东方财富网] 第 {i + 1} 个热点解析失败: {e}")
                continue

        return items


if __name__ == "__main__":
    import asyncio
    from core.browser import browser_manager

    async def run():
        spider = EastMoneyTopicSpider()

        await browser_manager.start()

        try:
            items = await spider.run()

            for i, item in enumerate(items, 1):
                print(f"{i}. {item.title}")
                print(f"   日期: {item.published_at}")
                print(f"   链接: {item.url}")
                print(f"   摘要: {item.summary}")
                print("-" * 60)

        finally:
            await browser_manager.stop()

    asyncio.run(run())
