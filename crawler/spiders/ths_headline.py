from datetime import datetime
from typing import List

from playwright.async_api import Page

from crawler.core.base_spider import BaseSpider
from crawler.core.models import ArticleItem

"""
同花顺头条新闻爬虫。

抓取同花顺「头条」栏目中的新闻：

    - 标题
    - 链接
    - 发布时间

并转换为统一的 ArticleItem。

支持独立运行：

    python -m spiders.ths_headline
"""


class THSHeadlineSpider(BaseSpider):
    name = "同花顺"
    start_url = "https://www.10jqka.com.cn/?type=title"

    async def parse(
        self,
        page: Page,
    ) -> List[ArticleItem]:

        items: List[ArticleItem] = []

        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ==========================================================
        # 1. 页面加载
        # ==========================================================

        await page.goto(
            self.start_url,
            wait_until="domcontentloaded",
            timeout=20000,
        )

        # 不等待 networkidle
        # 同花顺页面存在大量持续请求，networkidle 容易一直等
        await page.wait_for_timeout(2000)

        # ==========================================================
        # 2. 找新闻链接
        #
        # 先从页面上的新闻链接中提取。
        # 不再等待「头条」文字，避免页面卡住。
        # ==========================================================

        selectors = [
            "a[href*='/news/']",
            "a[href*='/article/']",
            "a[href*='news.10jqka.com.cn']",
        ]

        links = None

        for selector in selectors:

            locator = page.locator(selector)

            try:
                count = await locator.count()

                if count > 0:
                    links = locator
                    print(f"  ✓ [同花顺] " f"找到 {count} 个新闻链接")
                    break

            except Exception:
                continue

        if links is None:
            print("  ⚠️ [同花顺] 没找到新闻链接")
            return items

        # ==========================================================
        # 3. 解析新闻
        # ==========================================================

        count = await links.count()

        seen_urls = set()

        for i in range(count):

            try:
                link = links.nth(i)

                title = (
                    (await link.inner_text())
                    .strip()
                    .replace(
                        "\n",
                        " ",
                    )
                )

                href = await link.get_attribute("href")

                if not title or not href:
                    continue

                # ==================================================
                # 过滤
                # ==================================================

                if len(title) < 6:
                    continue

                full_url = self.build_url(href)

                if not full_url:
                    continue

                if full_url in seen_urls:
                    continue

                seen_urls.add(full_url)

                # ==================================================
                # 排除明显不是新闻的内容
                # ==================================================

                blacklist = [
                    "login",
                    "register",
                    "passport",
                    "download",
                    "javascript:",
                ]

                if any(keyword in full_url.lower() for keyword in blacklist):
                    continue

                # ==================================================
                # ArticleItem
                # ==================================================

                items.append(
                    ArticleItem(
                        source_name=self.name,
                        title=title,
                        url=full_url,
                        summary="",
                        content="",
                        category="头条",
                        published_at=crawl_time,
                    )
                )

            except Exception as e:

                print(f"  ⚠️ [同花顺] " f"第 {i + 1} 条解析失败: {e}")

        print(f"  ✓ [同花顺] 共获取 {len(items)} 条头条")

        return items
