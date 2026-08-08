import re
from datetime import datetime, timedelta
from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class SseAnnouncementSpider(BaseSpider):
    name = "上海证券交易所上市公司公告"
    start_url = "http://www.sse.com.cn/disclosure/listedinfo/announcement/"

    # 复用日期正则匹配
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

        # 1. 等待上交所公告列表容器渲染完成
        try:
            # 该页面公告表格的典型 Selector
            table_tbody = page.locator(
                ".js_announceTable tbody, table.table tbody"
            ).first
            await table_tbody.wait_for(state="visible", timeout=15000)
        except Exception:
            # 超时未找到列表说明页面加载异常或网络超时
            return items

        # 2. 遍历数据行
        rows = page.locator(".js_announceTable tbody tr, table.table tbody tr")
        count = await rows.count()

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        recent_2_days = [today.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")]

        for i in range(count):
            row = rows.nth(i)
            cols = row.locator("td")
            col_count = await cols.count()

            # 上交所公告表格每行标准为 5 列：[代码, 简称, 公告标题, 下载, 时间]
            if col_count < 5:
                continue

            # 3. 提取各个单元格
            sec_code = (await cols.nth(0).inner_text()).strip()
            sec_name = (await cols.nth(1).inner_text()).strip()

            # 公告标题节点
            title_node = cols.nth(2).locator("a").first
            if await title_node.count() > 0:
                title = (await title_node.inner_text()).strip()
            else:
                title = (await cols.nth(2).inner_text()).strip()

            # 获取 PDF 文件下载地址（优先取“下载”列的 <a> 标签，其次取标题 <a> 标签）
            download_node = cols.nth(3).locator("a").first
            pdf_href = ""
            if await download_node.count() > 0:
                pdf_href = await download_node.get_attribute("href") or ""
            elif await title_node.count() > 0:
                pdf_href = await title_node.get_attribute("href") or ""

            if not pdf_href or not title:
                continue

            # URL 协议头与绝对路径拼接
            full_url = self.build_url(pdf_href)
            if full_url.startswith("http://"):
                full_url = full_url.replace("http://", "https://")

            # 提取发布时间
            raw_date_text = (await cols.nth(4).inner_text()).strip()
            publish_at = self.extract_date(raw_date_text)

            # 过滤近 2 天数据（可按需调整/移除）
            if publish_at and not any(publish_at.startswith(d) for d in recent_2_days):
                continue

            # 结构化填充 ArticleItem
            full_title = f"[{sec_code} {sec_name}] {title}"
            # summary = f"证券代码: {sec_code} | 证券简称: {sec_name} | 公告标题: {title} | 发布日期: {publish_at}"
            # content = f"证券代码：{sec_code}\n证券简称：{sec_name}\n公告标题：{title}\n发布日期：{publish_at}\n附件下载地址：{full_url}"

            items.append(
                ArticleItem(
                    source_name=self.name,
                    title=full_title,
                    url=full_url,
                    published_at=publish_at,
                    category="上交所公告",
                )
            )

        return items
