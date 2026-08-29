from .base_rss import RSSSpider


class YahooFinanceSpider(RSSSpider):
    """
    Yahoo 股市 RSS。

    默认抓取：
        最新新闻
    """

    name = "Yahoo股市"
    category = "财经新闻"

    start_url = (
        "https://tw.stock.yahoo.com/rss"
        "?category=news"
    )


class YahooMarketSpider(RSSSpider):
    """
    Yahoo 台股动态。
    """

    name = "Yahoo台股"
    category = "台股新闻"

    start_url = (
        "https://tw.stock.yahoo.com/rss"
        "?category=tw-market"
    )


class YahooInternationalSpider(RSSSpider):
    """
    Yahoo 国际财经。
    """

    name = "Yahoo国际财经"
    category = "国际财经"

    start_url = (
        "https://tw.stock.yahoo.com/rss"
        "?category=intl-markets"
    )


class YahooResearchSpider(RSSSpider):
    """
    Yahoo 研究报告。
    """

    name = "Yahoo研究报告"
    category = "研究报告"

    start_url = (
        "https://tw.stock.yahoo.com/rss"
        "?category=research"
    )


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = YahooFinanceSpider()

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

