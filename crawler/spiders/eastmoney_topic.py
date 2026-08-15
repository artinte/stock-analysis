from datetime import datetime
from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class EastMoneyTopicSpider(BaseSpider):
    name = "东方财富网"
    start_url = "https://gubatopic.eastmoney.com/"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []
        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            # 1. 尝试精准提取标题（避免 inner_text 把正文摘要也塞进 title 里）
            title_el = item.locator(".title, .topic_title, h3, a").first
            if await title_el.count() > 0:
                title = (await title_el.inner_text()).strip().replace("\n", " ")
            else:
                title = (await item.inner_text()).strip().replace("\n", " ")

            # 2. 提取链接
            href = await item.get_attribute("href")
            if not href and await title_el.count() > 0:
                href = await title_el.get_attribute("href")

            full_url = self.build_url(href) if href else self.start_url

            # 3. 过滤黑名单和无效标题
            if any(k in full_url for k in blacklist):
                continue

            if not title or len(title) < 3:
                continue

            # 4. 提取卡片上的正文/摘要
            card = item.locator(
                "xpath=ancestor::div[contains(@class, 'hotTopicMsg')]"
            ).first

            summary_el = card.locator(".item_desc")
            content = ""

            if await summary_el.count() > 0:
                content = (await summary_el.first.inner_text()).strip()

            # 5. 如果抓到了 summary，但没有抓到单独的 title，说明卡片整体就是文本
            # 清理标题中可能重叠的正文部分
            if content and content in title:
                title = title.replace(content, "").strip()

            if len(content) < 200:
                summary = content
            else:
                summary = ""

            items.append(
                ArticleItem(
                    source_name=self.name,
                    title=title,
                    url=full_url,
                    summary=summary,
                    content=content,
                    category="热门话题",
                    published_at=crawl_time,
                )
            )

        return items
