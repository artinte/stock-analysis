from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class MOFCOMPolicySpider(BaseSpider):
    name = "商务部官网"
    start_url = "https://wms.mofcom.gov.cn/zcfb/wmgl/index.html"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []
        await page.wait_for_selector(".listCon", timeout=15000)

        links_locator = page.locator(".listCon a")
        count = await links_locator.count()
        keywords = ["公告", "通知", "目录", "细则", "名单", "公示"]

        for i in range(count):
            link_element = links_locator.nth(i)
            title = (await link_element.inner_text()).strip()
            href = await link_element.get_attribute("href")

            if not href or not title:
                continue

            if any(k in title for k in keywords):
                full_url = self.build_url(href)

                items.append(
                    ArticleItem(
                        source_name=self.name,
                        title=title,
                        url=full_url,
                        summary="",
                        category="外贸管理政策",
                    )
                )

        return items