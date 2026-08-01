from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class CCTVFinanceSpider(BaseSpider):
    name = "央视财经"
    start_url = "https://finance.cctv.com/"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []
        content_area = page.locator(
            ".content, .list, .con_left, #page_body, .text_box"
        )
        await content_area.first.wait_for(state="visible", timeout=15000)

        # 触发懒加载
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(1000)

        links_locator = page.locator(
            '.content a, .list a, .con_left a, .text_box a, a[href*="ARTI"]'
        )
        count = await links_locator.count()

        blacklist = [
            "rmlx",
            "app.cctv",
            "english.cctv",
            "worldcup",
            "passport",
            "mn.cctv",
            "live",
        ]

        for i in range(count):
            item = links_locator.nth(i)
            title = (await item.inner_text()).strip().replace("\n", " ")
            href = await item.get_attribute("href")

            if not href or not title:
                continue

            full_url = self.build_url(href)

            # 过滤规则
            if "ARTI" not in full_url and "/202" not in full_url:
                continue
            if any(k in full_url for k in blacklist):
                continue
            if (
                len(title) < 6
                or title in ["更多", "详细", "点击查看"]
                or title.startswith("http")
            ):
                continue

            summary = (await item.get_attribute("title") or "").strip()

            items.append(
                ArticleItem(
                    source_name=self.name,
                    title=title,
                    url=full_url,
                    summary=summary if summary != title else "",
                    category="核心新闻",
                )
            )

        return items