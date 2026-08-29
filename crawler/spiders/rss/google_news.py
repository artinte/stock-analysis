from __future__ import annotations

from urllib.parse import quote

from .base_rss import RSSSpider


class GoogleNewsSpider(RSSSpider):
    """
    Google 新闻 RSS。

    默认：
        简体中文
        中国大陆
        财经/综合新闻
    """

    name = "Google新闻"
    category = "新闻"

    def __init__(self, keyword: str | None = None):
        self.keyword = keyword

        if keyword:
            query = quote(keyword)

            self.start_url = (
                "https://news.google.com/rss/search"
                f"?q={query}"
                "&hl=zh-CN"
                "&gl=CN"
                "&ceid=CN:zh-Hans"
            )
        else:
            self.start_url = (
                "https://news.google.com/rss" "?hl=zh-CN" "&gl=CN" "&ceid=CN:zh-Hans"
            )


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = GoogleNewsSpider("贵州茅台")

        await browser_manager.start()

        try:
            items = await spider.run()

            for i, item in enumerate(items, 1):
                print(f"{i}. {item.title}")
                print(f"   {item.published_at}")
                print(f"   {item.url}")
                print()

        finally:
            await browser_manager.stop()

    asyncio.run(run())
