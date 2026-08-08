import re
from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class CCTVFinanceSpider(BaseSpider):
    name = "央视财经"
    start_url = "https://finance.cctv.com/"

    # 正则提取日期函数
    def extract_date(self, text: str) -> str:
        if not text:
            return ""

        # 匹配年月日和时间
        # 示例: "2026年08月07日 10:15" 或 "2026-08-07 10:15:00"
        match = re.search(
            r"(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?\s*(\d{2}:\d{2}(?::\d{2})?)?",
            text,
        )
        if not match:
            return ""

        year, month, day, time_part = match.groups()

        # 补齐月份和日期的双位数（如 8 -> 08）
        month = month.zfill(2)
        day = day.zfill(2)

        # 如果没有匹配到具体时间，补充 00:00:00，否则补全秒数
        if not time_part:
            time_part = "00:00:00"
        elif len(time_part.split(":")) == 2:
            time_part = f"{time_part}:00"

        # 返回 Pydantic 能够正常解析的标准 ISO 时间字符串：YYYY-MM-DD HH:MM:SS
        return f"{year}-{month}-{day} {time_part}"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []
        content_area = page.locator(".content, .list, .con_left, #page_body, .text_box")
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

            # 如果标题中包含垃圾关键词，直接跳过，不去打开详情页（节省资源）
            if any(kw in title for kw in junk_keywords):
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

            detail_page = await page.context.new_page()
            content = ""
            publish_at = ""

            try:
                # 1. 打开详情页（只等待 DOM 加载完即可，速度快）
                await detail_page.goto(
                    full_url, wait_until="domcontentloaded", timeout=12000
                )

                # 方案 A：从页面节点提取（针对央视网常见的 .info / .info_1 / .source 元素）
                try:
                    info_text = await detail_page.locator(
                        ".info_1, .info, .source"
                    ).first.inner_text(timeout=2000)
                    publish_at = self.extract_date(info_text)
                except Exception:
                    pass

                # 方案 B：如果节点没有抓到，尝试读全局变量 window.publishTime
                if not publish_at:
                    try:
                        raw_js_time = await detail_page.evaluate(
                            "window.publishTime || ''"
                        )
                        publish_at = self.extract_date(str(raw_js_time))
                    except Exception:
                        pass

                # 方案 C：如果依然没抓到，直接用 URL 中的日期（如 /2026/08/06/...）
                if not publish_at:
                    publish_at = self.extract_date(full_url)

                # 2. 直接拿正文区域的文本
                # 央视网正文唯一核心节点：#content_area
                content = await detail_page.locator("#content_area").inner_text(
                    timeout=3000
                )
                content = content.strip()
            except Exception:
                # 兜底方案：如果 DOM 还没加载完，直接读央视网全局变量 cntText
                try:
                    content = await detail_page.evaluate("window.cntText || ''")
                    content = content.strip()
                except Exception:
                    content = ""
            finally:
                await detail_page.close()

            # 智能提取摘要（过滤署名 + 限制最低 40 字符）
            summary = ""
            if content:
                paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
                valid_parts = []

                for p in paragraphs:
                    # 规则 A：跳过短于 25 字且包含署名词汇的行
                    is_reporter_tag = len(p) < 25 and any(
                        k in p for k in ["记者", "讯", "电", "消息", "编辑", "来源"]
                    )
                    if is_reporter_tag:
                        continue

                    # 规则 B：累加有效段落，直到满足最低 40 字符要求
                    valid_parts.append(p)
                    combined_text = " ".join(valid_parts)

                    if len(combined_text) >= 40:
                        summary = combined_text
                        break

                # 兜底：如果整篇文章实在太短无法凑满 40 字，直接用全文
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
