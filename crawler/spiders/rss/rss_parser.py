from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Optional
from xml.etree import ElementTree

from crawler.core.models import ArticleItem


class RSSParser:
    """
    通用 RSS / Atom 解析器。

    不负责网络请求，只负责：

        XML → ArticleItem

    支持：

        RSS 2.0
        RSS 1.0
        Atom
        XML Namespace
        RFC 822 / RFC 1123 日期
        ISO 8601 日期
    """

    @staticmethod
    def parse(
        xml_text: str,
        source_name: str,
        category: str,
        max_items: Optional[int] = None,
    ) -> list[ArticleItem]:

        items: list[ArticleItem] = []

        crawl_time = datetime.now(
            timezone.utc
        )

        if not xml_text:
            return items

        # ========================================================
        # XML 解析
        # ========================================================

        try:

            root = ElementTree.fromstring(
                xml_text
            )

        except ElementTree.ParseError as e:

            raise ValueError(
                f"RSS XML 解析失败: {e}"
            ) from e

        # ========================================================
        # 查找 RSS / Atom 条目
        # ========================================================

        elements = RSSParser._find_items(
            root
        )

        print(
            f"  RSSParser: "
            f"找到 {len(elements)} 个条目"
        )

        # ========================================================
        # 逐条解析
        # ========================================================

        for index, element in enumerate(
            elements,
            1,
        ):

            if (
                max_items is not None
                and len(items) >= max_items
            ):
                break

            try:

                item = RSSParser._parse_item(
                    element=element,
                    source_name=source_name,
                    category=category,
                    crawl_time=crawl_time,
                )

                if item is not None:
                    items.append(item)

                else:

                    print(
                        f"  ⚠️ [{source_name}] "
                        f"第 {index} 条新闻无法解析"
                    )

            except Exception as e:

                print(
                    f"  ⚠️ [{source_name}] "
                    f"第 {index} 条新闻解析失败: {e}"
                )

        return items

    # ============================================================
    # 单条新闻
    # ============================================================

    @staticmethod
    def _parse_item(
        element,
        source_name: str,
        category: str,
        crawl_time: datetime,
    ) -> Optional[ArticleItem]:

        # --------------------------------------------------------
        # 标题
        # --------------------------------------------------------

        title = RSSParser._get_text(
            element,
            "title",
        )

        title = RSSParser.clean_text(
            title
        )

        if not title or len(title) < 2:
            return None

        # --------------------------------------------------------
        # URL
        # --------------------------------------------------------

        url = RSSParser._get_url(
            element
        )

        if not url:
            return None

        # --------------------------------------------------------
        # 发布时间
        # --------------------------------------------------------

        published_text = (
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
        )

        published_at = (
            RSSParser.parse_datetime(
                published_text
            )
            if published_text
            else crawl_time
        )

        # 如果日期解析失败，使用抓取时间
        if published_at is None:
            published_at = crawl_time

        # --------------------------------------------------------
        # 正文 / 摘要
        # --------------------------------------------------------

        content = (
            RSSParser._get_text(
                element,
                "description",
            )
            or RSSParser._get_text(
                element,
                "summary",
            )
            or RSSParser._get_text(
                element,
                "content",
            )
            or ""
        )

        content = RSSParser.clean_html(
            content
        )

        # --------------------------------------------------------
        # 摘要
        # --------------------------------------------------------

        if len(content) <= 500:

            summary = content

        else:

            summary = (
                content[:500]
                + "..."
            )

        # --------------------------------------------------------
        # ArticleItem
        # --------------------------------------------------------

        return ArticleItem(
            source_name=source_name,
            title=title,
            url=url,
            summary=summary,
            content=content,
            category=category,
            published_at=published_at,
        )

    # ============================================================
    # 查找 RSS / Atom 条目
    # ============================================================

    @staticmethod
    def _find_items(root):

        items = []

        for element in root.iter():

            tag = RSSParser._local_name(
                element.tag
            )

            if tag in (
                "item",
                "entry",
            ):

                items.append(element)

        return items

    # ============================================================
    # 获取 XML 文本
    # ============================================================

    @staticmethod
    def _get_text(
        element,
        tag: str,
    ) -> str:

        target = tag.lower()

        for child in element:

            child_tag = RSSParser._local_name(
                child.tag
            )

            if child_tag != target:
                continue

            # 普通文本

            if child.text:

                return child.text.strip()

            # 嵌套文本

            text = "".join(
                child.itertext()
            ).strip()

            if text:
                return text

        return ""

    # ============================================================
    # 获取 URL
    # ============================================================

    @staticmethod
    def _get_url(
        element,
    ) -> str:

        for child in element:

            tag = RSSParser._local_name(
                child.tag
            )

            if tag != "link":
                continue

            # RSS 2.0
            #
            # <link>
            #     https://example.com
            # </link>

            if child.text:

                url = child.text.strip()

                if url:
                    return url

            # Atom
            #
            # <link href="https://example.com"/>

            href = child.attrib.get(
                "href"
            )

            if href:
                return href.strip()

        # 某些 RSS 使用 guid 作为 URL

        guid = RSSParser._get_text(
            element,
            "guid",
        )

        if guid.startswith(
            (
                "http://",
                "https://",
            )
        ):
            return guid

        return ""

    # ============================================================
    # 日期解析
    # ============================================================

    @staticmethod
    def parse_datetime(
        value: str,
    ) -> Optional[datetime]:
        """
        解析 RSS / Atom 常见日期格式。

        支持：

            Sat, 29 Aug 2026 10:17:00 GMT

            Sat, 29 Aug 2026 10:17:00 +0000

            2026-08-29T10:17:00Z

            2026-08-29T10:17:00+00:00

            2026-08-29 10:17:00
        """

        if not value:
            return None

        value = value.strip()

        # --------------------------------------------------------
        # 1. RFC 822 / RFC 1123
        #
        # Google / Yahoo / CNBC 等大量 RSS 使用
        # --------------------------------------------------------

        try:

            dt = parsedate_to_datetime(
                value
            )

            if dt is not None:

                # 没有时区时统一视为 UTC

                if dt.tzinfo is None:

                    dt = dt.replace(
                        tzinfo=timezone.utc
                    )

                return dt

        except (TypeError, ValueError):

            pass

        # --------------------------------------------------------
        # 2. ISO 8601
        # --------------------------------------------------------

        iso_value = value

        # 末尾 Z
        if iso_value.endswith("Z"):

            iso_value = (
                iso_value[:-1]
                + "+00:00"
            )

        try:

            dt = datetime.fromisoformat(
                iso_value
            )

            if dt.tzinfo is None:

                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt

        except ValueError:

            pass

        # --------------------------------------------------------
        # 3. 常见无时区格式
        # --------------------------------------------------------

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d",
        ]

        for fmt in formats:

            try:

                dt = datetime.strptime(
                    value,
                    fmt,
                )

                return dt.replace(
                    tzinfo=timezone.utc
                )

            except ValueError:

                continue

        # --------------------------------------------------------
        # 无法解析
        # --------------------------------------------------------

        return None

    # ============================================================
    # XML Namespace
    # ============================================================

    @staticmethod
    def _local_name(
        tag,
    ) -> str:

        if not isinstance(
            tag,
            str,
        ):
            return ""

        # {namespace}item

        if "}" in tag:

            tag = tag.rsplit(
                "}",
                1,
            )[-1]

        # namespace:item

        if ":" in tag:

            tag = tag.rsplit(
                ":",
                1,
            )[-1]

        return tag.lower()

    # ============================================================
    # 清理 HTML
    # ============================================================

    @staticmethod
    def clean_html(
        text: str,
    ) -> str:

        if not text:
            return ""

        # HTML entity

        text = unescape(text)

        # script

        text = re.sub(
            r"<script.*?</script>",
            " ",
            text,
            flags=re.IGNORECASE
            | re.DOTALL,
        )

        # style

        text = re.sub(
            r"<style.*?</style>",
            " ",
            text,
            flags=re.IGNORECASE
            | re.DOTALL,
        )

        # HTML 标签

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        # 空白

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ============================================================
    # 清理普通文本
    # ============================================================

    @staticmethod
    def clean_text(
        text: str,
    ) -> str:

        if not text:
            return ""

        text = unescape(text)

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

