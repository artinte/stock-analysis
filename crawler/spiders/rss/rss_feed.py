from __future__ import annotations

import time
from typing import Optional

from playwright.async_api import Page

from crawler.config.rss_feeds import RSSFeed
from crawler.core.base_spider import BaseSpider
from crawler.core.models import ArticleItem
from crawler.spiders.rss.base_rss import RSSParser


class RSSFeedSpider(BaseSpider):
    """
    配置驱动 RSS 爬虫。

    一个 RSSFeed 对应一个数据源。

    例如：

        feed = RSSFeed(
            name="Google新闻",
            url="https://news.google.com/rss?...",
            category="新闻",
        )

        spider = RSSFeedSpider(feed)
    """

    name = "RSS"
    start_url = ""

    def __init__(
        self,
        feed: RSSFeed,
        retries: int = 2,
    ):
        self.feed = feed
        self.retries = retries

        self.name = feed.name
        self.start_url = feed.url

    async def parse(
        self,
        page: Page,
    ) -> list[ArticleItem]:

        start_time = time.perf_counter()

        last_error: Optional[Exception] = None

        for attempt in range(
            1,
            self.retries + 2,
        ):

            try:

                print(
                    f"  → [{self.name}] "
                    f"正在抓取 "
                    f"(第 {attempt} 次)"
                )

                response = await page.goto(
                    self.start_url,
                    wait_until="domcontentloaded",
                    timeout=self.feed.timeout,
                )

                if response is None:
                    raise RuntimeError(
                        "没有获取到 HTTP 响应"
                    )

                if not response.ok:
                    raise RuntimeError(
                        f"HTTP {response.status}"
                    )

                xml_text = await response.text()

                if not xml_text:
                    raise RuntimeError(
                        "RSS 内容为空"
                    )

                items = RSSParser.parse(
                    xml_text=xml_text,
                    source_name=self.feed.name,
                    category=self.feed.category,
                    max_items=self.feed.max_items,
                )

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                print(
                    f"  ✓ [{self.name}] "
                    f"{len(items)} 条 "
                    f"({elapsed:.2f}s)"
                )

                return items

            except Exception as e:

                last_error = e

                print(
                    f"  ⚠️ [{self.name}] "
                    f"第 {attempt} 次失败: {e}"
                )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        print(
            f"  ❌ [{self.name}] "
            f"最终失败 "
            f"({elapsed:.2f}s): "
            f"{last_error}"
        )

        return []

