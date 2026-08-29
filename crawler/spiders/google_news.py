from datetime import datetime
from typing import List
from xml.etree import ElementTree

from playwright.async_api import Page

from crawler.core.base_spider import BaseSpider
from crawler.core.models import ArticleItem

"""
Google 新闻简体中文 RSS 爬虫。

抓取 Google News RSS 中的新闻：
    - 标题
    - 链接
    - 摘要
    - 发布时间
    - 来源

RSS:
    https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans

支持独立运行：
    python -m spiders.google_news
"""


class GoogleNewsSpider(BaseSpider):
    name = "Google新闻"
    start_url = "https://news.google.com/rss" "?hl=zh-CN" "&gl=CN" "&ceid=CN:zh-Hans"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []

        # 抓取时间
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # RSS 是 XML，不是普通 HTML 页面
            response = await page.goto(
                self.start_url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            if response is None:
                print("  ❌ [Google新闻] 未获取到响应")
                return items

            if not response.ok:
                print(f"  ❌ [Google新闻] HTTP 请求失败: " f"{response.status}")
                return items

            # 直接读取 RSS 原始 XML
            xml_text = await response.text()

            if not xml_text:
                print("  ❌ [Google新闻] RSS 内容为空")
                return items

            # 解析 XML
            root = ElementTree.fromstring(xml_text)

        except Exception as e:
            print(f"  ❌ [Google新闻] RSS 获取失败: {e}")
            return items

        # RSS 标准结构：
        #
        # <rss>
        #   <channel>
        #       <item>
        #           <title>...</title>
        #           <link>...</link>
        #           <pubDate>...</pubDate>
        #           <description>...</description>
        #           <source>...</source>
        #       </item>
        #   </channel>
        # </rss>
        channel = root.find("channel")

        if channel is None:
            print("  ❌ [Google新闻] RSS 中没有 channel")
            return items

        rss_items = channel.findall("item")

        print(f"  ✓ [Google新闻] 获取 {len(rss_items)} 条新闻")

        for i, item in enumerate(rss_items, 1):
            try:
                # 1. 标题
                title_el = item.find("title")
                title = (
                    title_el.text.strip()
                    if title_el is not None and title_el.text
                    else ""
                )

                # 2. 链接
                link_el = item.find("link")
                url = (
                    link_el.text.strip() if link_el is not None and link_el.text else ""
                )

                # 3. 发布时间
                pub_date_el = item.find("pubDate")
                published_at = (
                    pub_date_el.text.strip()
                    if pub_date_el is not None and pub_date_el.text
                    else crawl_time
                )

                # 4. 摘要 / 正文
                description_el = item.find("description")
                content = (
                    description_el.text.strip()
                    if description_el is not None and description_el.text
                    else ""
                )

                # 5. 来源
                source_el = item.find("source")
                source_name = (
                    source_el.text.strip()
                    if source_el is not None and source_el.text
                    else "Google新闻"
                )

                # 过滤无效数据
                if not title or len(title) < 3:
                    continue

                if not url:
                    continue

                # Google News RSS 的 description
                # 通常包含 HTML，ArticleItem 先保留原始内容。
                summary = content

                # 防止 summary 过长
                if len(summary) > 500:
                    summary = summary[:500] + "..."

                items.append(
                    ArticleItem(
                        source_name=source_name,
                        title=title,
                        url=url,
                        summary=summary,
                        content=content,
                        category="新闻",
                        published_at=published_at,
                    )
                )

            except Exception as e:
                print(f"  ⚠️ [Google新闻] " f"第 {i} 条新闻解析失败: {e}")
                continue

        return items


if __name__ == "__main__":
    import asyncio

    from core.browser import browser_manager

    async def run():
        spider = GoogleNewsSpider()

        await browser_manager.start()

        try:
            items = await spider.run()

            print()
            print(f"Google新闻：共 {len(items)} 条")
            print()

            for i, item in enumerate(items, 1):
                print(f"{i}. {item.title}")
                print(f"   来源: {item.source_name}")
                print(f"   日期: {item.published_at}")
                print(f"   链接: {item.url}")
                print(f"   摘要: {item.summary}")
                print("-" * 60)

        finally:
            await browser_manager.stop()

    asyncio.run(run())
