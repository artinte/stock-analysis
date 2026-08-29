from __future__ import annotations

from datetime import datetime
from html import unescape
from typing import List
from xml.etree import ElementTree

from playwright.async_api import Page

from crawler.core.base_spider import BaseSpider
from crawler.core.models import ArticleItem


class RSSSpider(BaseSpider):
    """
    通用 RSS 爬虫。

    子类只需要定义：

        name
        start_url
        category

    即可自动解析 RSS / Atom。
    """

    category = "财经新闻"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items: List[ArticleItem] = []

        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            response = await page.goto(
                self.start_url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            if response is None:
                print(f"  ❌ [{self.name}] 没有获取到响应")
                return items

            if not response.ok:
                print(f"  ❌ [{self.name}] HTTP 请求失败: " f"{response.status}")
                return items

            xml_text = await response.text()

            if not xml_text:
                print(f"  ❌ [{self.name}] RSS 内容为空")
                return items

        except Exception as e:
            print(f"  ❌ [{self.name}] RSS 请求失败: {e}")
            return items

        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as e:
            print(f"  ❌ [{self.name}] XML 解析失败: {e}")
            return items

        # RSS 2.0
        rss_items = root.findall("./channel/item")

        # Atom
        if not rss_items:
            namespace = {"atom": "http://www.w3.org/2005/Atom"}

            rss_items = root.findall(
                "./atom:entry",
                namespace,
            )

        print(f"  ✓ [{self.name}] " f"获取 {len(rss_items)} 条新闻")

        for index, element in enumerate(rss_items, 1):
            try:
                item = self._parse_item(
                    element=element,
                    crawl_time=crawl_time,
                )

                if item is None:
                    continue

                items.append(item)

            except Exception as e:
                print(f"  ⚠️ [{self.name}] " f"第 {index} 条解析失败: {e}")

        return items

    def _parse_item(
        self,
        element,
        crawl_time: str,
    ) -> ArticleItem | None:
        """
        解析单条 RSS / Atom 新闻。
        """

        title = self._get_text(
            element,
            "title",
        )

        if not title or len(title) < 3:
            return None

        url = self._get_url(element)

        if not url:
            return None

        # RSS
        published_at = (
            self._get_text(element, "pubDate")
            or self._get_text(element, "published")
            or self._get_text(element, "updated")
            or crawl_time
        )

        # RSS description
        content = (
            self._get_text(element, "description")
            or self._get_text(element, "summary")
            or self._get_text(element, "content")
            or ""
        )

        content = self.clean_html(content)

        summary = content

        if len(summary) > 500:
            summary = summary[:500] + "..."

        return ArticleItem(
            source_name=self.name,
            title=title,
            url=url,
            summary=summary,
            content=content,
            category=self.category,
            published_at=published_at,
        )

    @staticmethod
    def _get_text(element, tag: str) -> str:
        """
        获取普通 XML 标签文本。
        """

        child = element.find(tag)

        if child is not None and child.text:
            return child.text.strip()

        return ""

    @staticmethod
    def _get_url(element) -> str:
        """
        同时兼容：

            RSS:
                <link>https://...</link>

            Atom:
                <link href="https://..." />
        """

        # RSS
        link = element.find("link")

        if link is not None:
            if link.text:
                return link.text.strip()

            href = link.attrib.get("href")

            if href:
                return href.strip()

        # Atom
        for child in element:
            if child.tag.endswith("link"):
                href = child.attrib.get("href")

                if href:
                    return href.strip()

        return ""

    @staticmethod
    def clean_html(text: str) -> str:
        """
        清理 RSS description 中的 HTML。
        """

        if not text:
            return ""

        text = unescape(text)

        # 去 HTML 标签
        import re

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        # 合并空白
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()
