from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class EastMoneyTopicSpider(BaseSpider):
    name = "东方财富网"
    start_url = "https://gubatopic.eastmoney.com/"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []
        target_locator = page.locator(
            'a[href*="topic"], .topic_item, .topic_list, .list_item'
        )
        await target_locator.first.wait_for(state="visible", timeout=15000)

        await page.evaluate("window.scrollBy(0, 400)")
        await page.wait_for_timeout(1000)

        count = await target_locator.count()
        blacklist = ["passport", "login", "register", "user.eastmoney"]

        for i in range(count):
            item = target_locator.nth(i)
            title = (await item.inner_text()).strip().replace("\n", " ")
            href = await item.get_attribute("href")

            full_url = self.build_url(href) if href else self.start_url

            if any(k in full_url for k in blacklist):
                continue

            if not title or len(title) < 3:
                continue

            summary_el = item.locator(".brief, .desc, .topic_desc")
            summary = ""
            if await summary_el.count() > 0:
                summary = (await summary_el.first.inner_text()).strip()

            items.append(
                ArticleItem(
                    source_name=self.name,
                    title=title,
                    url=full_url,
                    summary=summary,
                    category="热门话题",
                )
            )

        return items