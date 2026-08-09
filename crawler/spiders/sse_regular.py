import re
from datetime import datetime, timedelta
from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class SseRegularReportSpider(BaseSpider):
    name = "上海证券交易所定期报告"
    start_url = "https://www.sse.com.cn/disclosure/listedinfo/regular/"

    def extract_date(self, text: str) -> str:
        if not text:
            return ""

        match = re.search(
            r"(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?\s*(\d{2}:\d{2}(?::\d{2})?)?",
            text,
        )
        if not match:
            return ""

        year, month, day, time_part = match.groups()

        month = month.zfill(2)
        day = day.zfill(2)

        if not time_part:
            time_part = "00:00:00"
        elif len(time_part.split(":")) == 2:
            time_part = f"{time_part}:00"

        return f"{year}-{month}-{day} {time_part}"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []

        # 1. 精准等待规则报告表格 (.js_regular) 中的 td 填充
        try:
            await page.wait_for_selector(
                ".js_regular table.table tbody tr td",
                timeout=15000,
                state="attached",
            )
            await page.wait_for_timeout(1000)  # 留存 1 秒让 DOM 稳定
        except Exception:
            return items

        # 2. 获取数据行
        rows = page.locator(".js_regular table.table tbody tr")
        count = await rows.count()

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        recent_2_days = [today.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")]

        for i in range(count):
            row = rows.nth(i)
            cols = row.locator("td")
            col_count = await cols.count()

            # 修正 1：实际只有 4 列，少于 4 列的才是空行或分割行
            if col_count < 4:
                continue

            # 3. 按实际 4 列提取数据
            sec_code = (await cols.nth(0).inner_text()).strip()
            sec_name = (await cols.nth(1).inner_text()).strip()

            if not sec_code or sec_code == "暂无数据":
                continue

            # 修正 2：公告标题与 PDF 链接都在第 3 列 (index 2)
            title_td = cols.nth(2)
            title_node = title_td.locator("a").first

            if await title_node.count() > 0:
                title = (await title_node.inner_text()).strip()
                pdf_href = await title_node.get_attribute("href") or ""
            else:
                title = (await title_td.inner_text()).strip()
                pdf_href = ""

            if not pdf_href or not title:
                continue

            full_url = self.build_url(pdf_href)
            if full_url.startswith("http://"):
                full_url = full_url.replace("http://", "https://")

            # 修正 3：发布时间在第 4 列 (index 3)
            raw_date_text = (await cols.nth(3).inner_text()).strip()
            publish_at = self.extract_date(raw_date_text)

            # 过滤近 2 天数据
            if publish_at and not any(publish_at.startswith(d) for d in recent_2_days):
                continue

            full_title = f"[{sec_code} {sec_name}] {title}"

            items.append(
                ArticleItem(
                    source_name=self.name,
                    title=full_title,
                    url=full_url,
                    related_companies=[sec_name],
                    published_at=publish_at,
                    category="定期报告",
                )
            )

        return items
