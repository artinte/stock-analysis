from .base_rss import RSSSpider


class MarketWatchSpider(RSSSpider):
    """
    MarketWatch 市场新闻。
    """

    name = "MarketWatch"
    category = "国际财经"

    start_url = (
        "https://feeds.marketwatch.com/"
        "marketwatch/topstories/"
    )


class MarketWatchStockSpider(RSSSpider):
    """
    MarketWatch 股票市场新闻。
    """

    name = "MarketWatch股票"
    category = "股票新闻"

    start_url = (
        "https://feeds.marketwatch.com/"
        "marketwatch/marketpulse/"
    )


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = MarketWatchSpider()

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
