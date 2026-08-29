from __future__ import annotations

import httpx

from crawler.config.rss_feeds import RSSFeed
from crawler.core.models import ArticleItem
from crawler.spiders.rss.rss_parser import RSSParser


class RSSFeedSpider:
    """
    通用 RSS / Atom 爬虫。

    RSS 抓取采用 HTTP 方式。

    流程：

        RSSFeed
            ↓
        HTTP GET
            ↓
        RSS XML
            ↓
        RSSParser
            ↓
        ArticleItem
    """

    def __init__(self, feed: RSSFeed):
        self.feed = feed

    async def parse(self) -> list[ArticleItem]:
        """
        获取并解析 RSS。
        """

        xml_text = await self._fetch()

        items = RSSParser.parse(
            xml_text=xml_text,
            source_name=self.feed.name,
            category=self.feed.category,
            max_items=self.feed.max_items,
        )

        print(
            f"    RSSParser: 找到 {len(items)} 个条目"
        )

        return items

    async def _fetch(self) -> str:
        """
        HTTP 获取 RSS XML。
        """

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "application/rss+xml,"
                "application/atom+xml,"
                "application/xml,"
                "text/xml,"
                "*/*"
            ),
            "Accept-Language": (
                "zh-CN,zh;q=0.9,en;q=0.8"
            ),
        }

        timeout = httpx.Timeout(
            self.feed.timeout
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                self.feed.url
            )

            print(
                f"    HTTP {response.status_code}"
            )

            content_type = response.headers.get(
                "content-type",
                "",
            )

            print(
                f"    Content-Type: {content_type}"
            )

            print(
                f"    Content-Length: "
                f"{len(response.content)}"
            )

            response.raise_for_status()

            if not response.content:
                raise ValueError(
                    "RSS 返回内容为空"
                )

            return response.text