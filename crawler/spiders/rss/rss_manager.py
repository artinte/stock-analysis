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
        - 自动重试
        - 错误隔离
        - 耗时统计
        - 最终汇总

    RSS 本身通过 HTTP 抓取。
    """

    def __init__(
        self,
        feeds: list[RSSFeed],
        concurrency: int = 4,
        retries: int = 2,
    ):
        self.feeds = [
            feed
            for feed in feeds
            if feed.enabled
        ]

        self.concurrency = max(
            1,
            concurrency,
        )

        self.retries = max(
            0,
            retries,
        )

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
                last_error = ""

                for attempt in range(
                    self.retries + 1
                ):

                    try:

                        print(
                            f"  → [{feed.name}] "
                            f"正在抓取 "
                            f"(第 {attempt + 1} 次)"
                        )

                        spider = RSSFeedSpider(
                            feed
                        )

                        items = await spider.parse()

                        elapsed = (
                            time.perf_counter()
                            - start
                        )

                        print(
                            f"  ✓ [{feed.name}] "
                            f"{len(items)} 条 "
                            f"({elapsed:.2f}s)"
                        )

                        return RSSResult(
                            name=feed.name,
                            success=True,
                            items=items,
                            elapsed=elapsed,
                        )

                    except Exception as e:

                        last_error = (
                            f"{type(e).__name__}: {e}"
                        )

                        print(
                            f"  ⚠️ [{feed.name}] "
                            f"第 {attempt + 1} 次失败: "
                            f"{last_error}"
                        )

                        # 还可以重试
                        if attempt < self.retries:

                            # 1s、2s、4s……
                            delay = min(
                                2 ** attempt,
                                8,
                            )

                            await asyncio.sleep(
                                delay
                            )

                elapsed = (
                    time.perf_counter()
                    - start
                )

                print(
                    f"  ❌ [{feed.name}] "
                    f"最终失败 "
                    f"({elapsed:.2f}s)"
                )

                return RSSResult(
                    name=feed.name,
                    success=False,
                    items=[],
                    elapsed=elapsed,
                    error=last_error,
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