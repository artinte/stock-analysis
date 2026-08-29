from .base_rss import RSSSpider


class SeekingAlphaSpider(RSSSpider):
    """
    Seeking Alpha 新闻 RSS。
    """

    name = "SeekingAlpha"
    category = "投资研究"

    start_url = "https://seekingalpha.com/feed.xml"


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = SeekingAlphaSpider()

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
