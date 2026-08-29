from .base_rss import RSSSpider


class BloombergMarketSpider(RSSSpider):
    """
    Bloomberg 市场新闻。
    """

    name = "Bloomberg"
    category = "国际市场"

    start_url = "https://feeds.bloomberg.com/" "markets/news.rss"


class BloombergTechnologySpider(RSSSpider):
    """
    Bloomberg 科技新闻。
    """

    name = "Bloomberg科技"
    category = "科技新闻"

    start_url = "https://feeds.bloomberg.com/" "technology/news.rss"


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = BloombergMarketSpider()

        await browser_manager.start()

        try:
            items = await spider.run()

            for i, item in enumerate(items, 1):
                print(f"{i}. {item.title}")
                print(f"   {item.url}")
                print()

        finally:
            await browser_manager.stop()

    asyncio.run(run())
