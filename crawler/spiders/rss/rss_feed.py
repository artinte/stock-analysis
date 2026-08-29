from __future__ import annotations

import time
from typing import Optional

import httpx

from crawler.config.rss_feeds import RSSFeed
from crawler.core.models import ArticleItem
from crawler.spiders.rss.rss_parser import RSSParser


class RSSFeedSpider:
    """
    通用 RSS 爬虫。

    RSS 是纯 HTTP + XML 数据，
    不使用 Playwright。

    负责：

        HTTP 请求
        ↓
        XML
        ↓
        RSSParser
        ↓
        ArticleItem
    """

    def __init__(
        self,
        feed: RSSFeed,
        retries: int = 2,
    ):
        self.feed = feed
        self.retries = retries

        self.name = feed.name

    async def parse(self) -> list[ArticleItem]:

        start_time = time.perf_counter()

        last_error: Optional[Exception] = None

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/122.0.0.0 "
                "Safari/537.36"
            ),
            "Accept": (
                "application/rss+xml, "
                "application/xml, "
                "text/xml, "
                "*/*"
            ),
        }

        timeout = httpx.Timeout(
            self.feed.timeout / 1000
        )

        async with httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        ) as client:

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

                    response = await client.get(
                        self.feed.url
                    )

                    response.raise_for_status()

                    xml_text = response.text

                    if not xml_text:
                        raise RuntimeError(
                            "RSS 内容为空"
                        )

                    print(
                        f"  Content-Type: "
                        f"{response.headers.get('content-type')}"
                    )

                    print(
                        f"  Content-Length: "
                        f"{len(xml_text)}"
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

