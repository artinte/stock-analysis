from .base_rss import RSSSpider


class CNBCSpider(RSSSpider):
    """
    CNBC 财经新闻 RSS。
    """

    name = "CNBC"
    category = "国际财经"

    start_url = "https://www.cnbc.com/" "id/10000664/device/rss/rss.html"


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = CNBCSpider()

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
