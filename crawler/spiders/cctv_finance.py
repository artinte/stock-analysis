# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from typing import List
from playwright.async_api import Page
from crawler.core.base_spider import BaseSpider
from crawler.core.models import ArticleItem

"""
央视财经新闻爬虫。

抓取央视财经近期新闻的标题、链接、发布时间、摘要和正文，
并转换为统一的 ArticleItem 数据结构。

支持独立运行：
    python -m spiders.cctv_finance
"""


class CCTVFinanceSpider(BaseSpider):
    name = "央视财经"
    start_url = "https://finance.cctv.com/"

    def __init__(self, use_first_paragraph_summary: bool = False):
        super().__init__()
        self.use_first_paragraph_summary = use_first_paragraph_summary

    # 正则提取日期函数
    def extract_date(self, text: str) -> str:
        if not text:
            return ""

        # 匹配年月日和时间
        # 示例: "2026年08月07日 10:15" 或 "2026-08-07 10:15:00"
        match = re.search(
            r"(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?\s*" r"(\d{2}:\d{2}(?::\d{2})?)?",
            text,
        )
        if not match:
            return ""

        year, month, day, time_part = match.groups()

        # 补齐月份和日期的双位数
        month = month.zfill(2)
        day = day.zfill(2)

        # 如果没有具体时间，补充 00:00:00
        if not time_part:
            time_part = "00:00:00"
        elif len(time_part.split(":")) == 2:
            time_part = f"{time_part}:00"

        return f"{year}-{month}-{day} {time_part}"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []

        content_area = page.locator(
            ".content, .list, .con_left, #page_body, .text_box")

        await content_area.first.wait_for(
            state="visible",
            timeout=15000,
        )

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

        junk_keywords = [
            "举报电话",
            "违法和不良信息",
            "投诉举报",
            "帮助中心",
            "联系我们",
            "关于我们",
            "版权声明",
            "用户协议",
            "隐私政策",
        ]

        # 用于避免同一篇新闻在不同栏目中重复抓取
        seen_urls = set()
        seen_titles = set()

        for i in range(count):
            item = links_locator.nth(i)

            title = (await item.inner_text()).strip().replace("\n", " ")

            href = await item.get_attribute("href")

            if not href or not title:
                continue

            # 如果标题中包含垃圾关键词，直接跳过
            if any(kw in title for kw in junk_keywords):
                continue

            full_url = self.build_url(href)

            # URL 去重
            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)

            # 标题去重
            if title in seen_titles:
                continue

            seen_titles.add(title)

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

            detail_page = await page.context.new_page()
            content = ""
            publish_at = ""

            try:
                # 1. 打开详情页
                await detail_page.goto(
                    full_url,
                    wait_until="domcontentloaded",
                    timeout=12000,
                )

                # 方案 A：从页面节点提取发布时间
                try:
                    info_text = await detail_page.locator(
                        ".info_1, .info, .source"
                    ).first.inner_text(timeout=2000)

                    publish_at = self.extract_date(info_text)

                except Exception:
                    pass

                # 方案 B：读取 window.publishTime
                if not publish_at:
                    try:
                        raw_js_time = await detail_page.evaluate(
                            "window.publishTime || ''"
                        )

                        publish_at = self.extract_date(str(raw_js_time))

                    except Exception:
                        pass

                # 方案 C：从 URL 中提取日期
                if not publish_at:
                    publish_at = self.extract_date(full_url)

                today = datetime.now()
                yesterday = today - timedelta(days=1)

                recent_2_days = [
                    today.strftime("%Y-%m-%d"),
                    yesterday.strftime("%Y-%m-%d"),
                ]
                if not publish_at or not any(
                    publish_at.startswith(d) for d in recent_2_days
                ):
                    continue

                # 2. 直接拿正文区域的文本
                content = await detail_page.locator("#content_area").inner_text(
                    timeout=3000
                )
                content = content.strip()
            except Exception:
                # 兜底方案：读取央视网全局变量 cntText
                try:
                    content = await detail_page.evaluate("window.cntText || ''")
                    content = content.strip()
                except Exception:
                    content = ""
            finally:
                await detail_page.close()

            summary = ""
            if self.use_first_paragraph_summary:
                if content:
                    paragraphs = [p.strip()
                                  for p in content.split("\n") if p.strip()]

                    valid_parts = []

                    for p in paragraphs:
                        # 规则 A：跳过短于 25 字且包含署名词汇的行
                        is_reporter_tag = len(p) < 25 and any(
                            k in p
                            for k in [
                                "记者",
                                "讯",
                                "电",
                                "消息",
                                "编辑",
                                "来源",
                            ]
                        )
                        if is_reporter_tag:
                            continue

                        # 规则 B：累加有效段落
                        valid_parts.append(p)
                        combined_text = " ".join(valid_parts)

                        if len(combined_text) >= 40:
                            summary = combined_text
                            break
                    if not summary:
                        summary = content
                else:
                    summary = title

            items.append(
                ArticleItem(
                    source_name=self.name,
                    title=title,
                    url=full_url,
                    published_at=publish_at,
                    summary=summary if summary != title else "",
                    content=content,
                    category="核心新闻",
                )
            )

        return items


if __name__ == "__main__":
    import asyncio
    from core.browser import browser_manager

    async def run():
        spider = CCTVFinanceSpider()

        await browser_manager.start()

        try:
            items = await spider.run()

            for i, item in enumerate(items, 1):
                print(f"{i}. {item.title}")
                print(f"   日期: {item.published_at}")
                print(f"   链接: {item.url}")
                print(f"   摘要: {item.summary}")
                print(f"   内容: {item.content[:100]}...")
                print("-" * 60)

        finally:
            await browser_manager.stop()

    asyncio.run(run())
