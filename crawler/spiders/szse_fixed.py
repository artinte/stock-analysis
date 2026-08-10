import re
from datetime import datetime, timedelta
from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class SzseRegularReportSpider(BaseSpider):
    name = "深圳证券交易所定期报告"
    start_url = "https://www.szse.cn/disclosure/listed/fixed/index.html"

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

    def clean_title(self, title: str) -> str:
        if not title:
            return ""
        # 匹配末尾的 (xxxxk) 或 (xxxxM/KB/MB) 等格式，并忽略周围的多余空格
        cleaned = re.sub(r"\s*\(\s*\d+(\.\d+)?\s*[kKmMgGbB]{1,2}\s*\)\s*$", "", title)
        return cleaned.strip()

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []

        # 1. 精准等待深交所公告表格及行数据渲染完成
        try:
            # 深交所常用的表格容器选择器，兼顾通用 class 及 table
            await page.wait_for_selector(
                "#disc-table table tbody tr td, table.table-disclosure tbody tr td, .table tbody tr td",
                timeout=15000,
                state="attached",
            )
            await page.wait_for_timeout(1000)  # 留存 1 秒让 DOM/数据完全渲染
        except Exception:
            return items

        # 2. 获取表格行数据
        rows = page.locator(
            "#disc-table table tbody tr, table.table-disclosure tbody tr, .table tbody tr"
        )
        count = await rows.count()

        # 设定允许提取的最小日期（昨日 00:00:00）
        # 保留昨天、今天，以及所有提前挂出/未来的日期（如 8 月 11 日等）
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        for i in range(count):
            row = rows.nth(i)
            cols = row.locator("td")
            col_count = await cols.count()

            # 深交所定期报告表格通常有 4 列：证券代码 | 证券简称 | 公告标题 | 公告时间
            if col_count < 4:
                continue

            # 3. 提取第 1 列（证券代码）与第 2 列（证券简称）
            sec_code = (await cols.nth(0).inner_text()).strip()
            sec_name = (await cols.nth(1).inner_text()).strip()

            if not sec_code or sec_code == "暂无数据" or "没有检索到" in sec_code:
                continue

            # 4. 提取第 3 列（公告标题与 PDF / 详情链接）
            title_td = cols.nth(2)
            title_node = title_td.locator("a").first

            if await title_node.count() > 0:
                title = (await title_node.inner_text()).strip()
                pdf_href = (
                    await title_node.get_attribute("href")
                    or await title_node.get_attribute("data-href")
                    or ""
                )
            else:
                title = (await title_td.inner_text()).strip()
                pdf_href = ""

            if not pdf_href or not title:
                continue

            # 过滤摘要类文件
            if "摘要" in title:
                continue

            # 拼接完整链接并补全 https 协议
            full_url = self.build_url(pdf_href)
            if full_url.startswith("http://"):
                full_url = full_url.replace("http://", "https://")

            # 5. 提取第 4 列（发布时间）
            raw_date_text = (await cols.nth(3).inner_text()).strip()
            publish_at = self.extract_date(raw_date_text)

            # 只要发布日期 >= 昨天，即予以保留（放弃上限判断）
            if publish_at:
                pub_date_str = publish_at.split(" ")[0]
                if pub_date_str < start_date:
                    continue

            title = self.clean_title(title)
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
