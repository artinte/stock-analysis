from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from crawler.config.rss_feeds import RSSFeed
from crawler.core.models import ArticleItem
from crawler.spiders.rss.rss_feed import RSSFeedSpider


@dataclass(slots=True)
class RSSResult:
    """
    单个 RSS 数据源执行结果。
    """

    name: str
    success: bool
    items: list[ArticleItem]
    elapsed: float
    error: str = ""


class RSSFeedManager:
    """
    RSS 批量抓取管理器。

    负责：

        - 批量抓取
        - 并发控制
        - 错误隔离
        - 耗时统计
        - 最终汇总
    """

    def __init__(
        self,
        feeds: list[RSSFeed],
        concurrency: int = 4,
    ):
        self.feeds = [
            feed
            for feed in feeds
            if feed.enabled
        ]

        self.concurrency = concurrency

    async def run(
        self,
    ) -> tuple[
        list[ArticleItem],
        list[RSSResult],
    ]:

        semaphore = asyncio.Semaphore(
            self.concurrency
        )

        async def worker(
            feed: RSSFeed,
        ) -> RSSResult:

            async with semaphore:

                start = time.perf_counter()

                try:

                    spider = RSSFeedSpider(
                        feed
                    )

                    items = await spider.parse()

                    elapsed = (
                        time.perf_counter()
                        - start
                    )

                    return RSSResult(
                        name=feed.name,
                        success=True,
                        items=items,
                        elapsed=elapsed,
                    )

                except Exception as e:

                    elapsed = (
                        time.perf_counter()
                        - start
                    )

                    return RSSResult(
                        name=feed.name,
                        success=False,
                        items=[],
                        elapsed=elapsed,
                        error=str(e),
                    )

        results = await asyncio.gather(
            *[
                worker(feed)
                for feed in self.feeds
            ]
        )

        all_items: list[ArticleItem] = []

        for result in results:
            all_items.extend(
                result.items
            )

        return all_items, results

