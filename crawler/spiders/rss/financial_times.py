from .base_rss import RSSSpider


class FinancialTimesMarketSpider(RSSSpider):
    """
    Financial Times 市场新闻。
    """

    name = "FinancialTimes"
    category = "国际财经"

    start_url = "https://www.ft.com/markets" "?format=rss"


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = FinancialTimesMarketSpider()

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
