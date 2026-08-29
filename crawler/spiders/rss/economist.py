from .base_rss import RSSSpider


class EconomistFinanceSpider(RSSSpider):
    """
    The Economist 财经 RSS。
    """

    name = "TheEconomist"
    category = "宏观财经"

    start_url = "https://www.economist.com/" "finance-and-economics/rss.xml"


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = EconomistFinanceSpider()

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
