# -*- coding: utf-8 -*-
from typing import List
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class SSESpider(BaseSpider):
    name = "上海证券交易所核心要闻"
    start_url = "http://www.sse.com.cn/"

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []

        # 1. 打开首页并等待核心新闻区域/列表节点加载
        try:
            await page.wait_for_selector(
                ".sse_list, #tableData_news, .news_list, .dl_list, a[href*='news']",
                timeout=15000,
            )
        except Exception:
            await page.wait_for_selector("a", timeout=10000)

        # 触发向下滚动，确保懒加载元素渲染完毕
        await page.evaluate("window.scrollBy(0, 800)")
        await page.wait_for_timeout(1000)

        # 2. 获取首页新闻、要闻、公告相关的链接节点
        links_locator = page.locator(
            "a[href*='news'], a[href*='aboutus'], .sse_list a, #tableData_news a, .list_box a"
        )
        count = await links_locator.count()

        # 过滤 A: 硬核业务白名单关键词（命中任意一个才被视为有效新闻）
        business_keywords = [
            "规则", "指引", "审议", "发布", "上市", "科创板", "主板",
            "REITs", "ETF", "债券", "程序化", "监管", "交易", "意见",
            "修改", "批复", "通知", "办法", "纪律处分", "听证", "披露"
        ]

        # 过滤 B: 非业务/党建/宣传黑名单关键词（命中任意一个即丢弃）
        blacklist_keywords = [
            "党建", "党委", "党支部", "三会一课", "研讨会", "慰问", "联建",
            "精神", "思想", "表彰", "心得", "学习贯彻", "活动", "团委",
            "javascript", ".pdf", ".doc", ".xlsx", "login", "search"
        ]

        visited_urls = set()

        for i in range(count):
            item = links_locator.nth(i)
            title = (await item.inner_text()).strip().replace("\n", " ")
            href = await item.get_attribute("href")

            if not href or not title:
                continue

            full_url = self.build_url(href)

            # 过滤1：防重
            if full_url in visited_urls:
                continue

            # 过滤2：标题与 URL 基础过滤
            if (
                len(title) < 8
                or title in ["更多", "详细", "点击查看", "更多>>", "首页", "查看详情"]
                or title.startswith("http")
            ):
                continue

            # 过滤3：排除黑名单（党建/非业务/文件下载）
            if any(k in title for k in blacklist_keywords) or any(
                k in full_url.lower() for k in blacklist_keywords
            ):
                continue

            # 过滤4：必须包含核心业务关键词（保证只抓重要业务新闻）
            if not any(k in title for k in business_keywords):
                continue

            visited_urls.add(full_url)

            # 3. 打开详情页提取正文
            detail_page = await page.context.new_page()
            content = ""
            try:
                await detail_page.goto(
                    full_url, wait_until="domcontentloaded", timeout=12000
                )

                # 上交所官网常见的正文区域选择器
                content_locator = detail_page.locator(
                    ".article-content, .detail_main, #zoom, .sse_detail_txt, .content, .con_text"
                )

                await content_locator.first.wait_for(state="attached", timeout=4000)
                content = await content_locator.first.inner_text()
                content = content.strip()

            except Exception:
                # 兜底提取策略：获取页面 p 标签正文文本
                try:
                    paragraphs = await detail_page.locator("p").all_inner_texts()
                    content = "\n".join([p.strip() for p in paragraphs if p.strip()])
                except Exception:
                    content = ""
            finally:
                await detail_page.close()

            # 4. 智能提取摘要（过滤署名与发布机构信息，限制最低 40 字符）
            summary = ""
            if content:
                paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
                valid_parts = []

                for p in paragraphs:
                    # 跳过短于 25 字且包含出处、字号、时间的标签行
                    is_tag_line = len(p) < 25 and any(
                        k in p for k in ["来源：", "发布时间：", "编辑：", "文章来源", "字号：", "【"]
                    )
                    if is_tag_line:
                        continue

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
                    summary=summary if summary != title else "",
                    content=content,
                    category="上交所要闻",
                )
            )

        return items