from __future__ import annotations

import re
from datetime import datetime
from html import unescape
from typing import Optional
from xml.etree import ElementTree

from crawler.core.models import ArticleItem


class RSSParser:
    """
    通用 RSS / Atom 解析器。

    不负责网络请求，只负责：

        XML → ArticleItem
    """

    @staticmethod
    def parse(
        xml_text: str,
        source_name: str,
        category: str,
        max_items: Optional[int] = None,
    ) -> list[ArticleItem]:

        items: list[ArticleItem] = []

        crawl_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        try:
            root = ElementTree.fromstring(xml_text)

        except ElementTree.ParseError as e:
            raise ValueError(
                f"RSS XML 解析失败: {e}"
            ) from e

        # RSS 2.0
        elements = root.findall(
            "./channel/item"
        )

        # Atom
        if not elements:
            elements = RSSParser._find_atom_entries(
                root
            )

        for element in elements:

            if (
                max_items is not None
                and len(items) >= max_items
            ):
                break

            try:
                item = RSSParser._parse_item(
                    element,
                    source_name,
                    category,
                    crawl_time,
                )

                if item is not None:
                    items.append(item)

            except Exception:
                continue

        return items

    @staticmethod
    def _parse_item(
        element,
        source_name: str,
        category: str,
        crawl_time: str,
    ) -> Optional[ArticleItem]:

        title = RSSParser._get_text(
            element,
            "title",
        )

        if not title or len(title) < 3:
            return None

        url = RSSParser._get_url(element)

        if not url:
            return None

        published_at = (
            RSSParser._get_text(
                element,
                "pubDate",
            )
            or RSSParser._get_text(
                element,
                "published",
            )
            or RSSParser._get_text(
                element,
                "updated",
            )
            or crawl_time
        )

        content = (
            RSSParser._get_text(
                element,
                "description",
            )
            or RSSParser._get_text(
                element,
                "summary",
            )
            or ""
        )

        content = RSSParser.clean_html(
            content
        )

        summary = content[:500]

        if len(content) > 500:
            summary += "..."

        return ArticleItem(
            source_name=source_name,
            title=title,
            url=url,
            summary=summary,
            content=content,
            category=category,
            published_at=published_at,
        )

    @staticmethod
    def _get_text(
        element,
        tag: str,
    ) -> str:

        child = element.find(tag)

        if child is not None:

            if child.text:
                return child.text.strip()

        return ""

    @staticmethod
    def _get_url(element) -> str:

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

                href = child.attrib.get(
                    "href"
                )

                if href:
                    return href.strip()

        return ""

    @staticmethod
    def _find_atom_entries(root):

        elements = []

        for element in root.iter():

            if element.tag.endswith("entry"):
                elements.append(element)

        return elements

    @staticmethod
    def clean_html(text: str) -> str:

        if not text:
            return ""

        text = unescape(text)

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

