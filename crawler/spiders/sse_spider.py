# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional
from playwright.async_api import Page
from core.base_spider import BaseSpider
from core.models import ArticleItem


class SSESpider(BaseSpider):
    name = "上海证券交易所-热点与动态"
    start_url = "http://www.sse.com.cn/aboutus/mediacenter/hotandd/"
    max_items = 5  # 限制最多抓取 5 条数据

    async def parse(self, page: Page) -> List[ArticleItem]:
        items = []

        # 1. 消除无头浏览器特征，规避防爬检测
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        try:
            # 2. 加载页面并等待指定列表容器 `#sse_list_1 dl` 及其内部的 dd 生成
            await page.goto(
                self.start_url, wait_until="domcontentloaded", timeout=20000
            )
            await page.wait_for_selector("#sse_list_1 dl dd a", timeout=12000)

            # 轻微滚动，触发页面潜在的懒加载
            await page.evaluate("window.scrollBy(0, 400)")
            await page.wait_for_timeout(800)

        except Exception as e:
            print(f"⚠️ 页面列表加载或定位超时: {e}")

        # 3. 精准定位目标容器 `#sse_list_1 dl` 下的 <dd>
        dd_locator = page.locator("#sse_list_1 dl dd")
        count = await dd_locator.count()

        blacklist = ["javascript", "download", "pdf", "zip"]
        visited_urls = set()

        for i in range(count):
            # 达到 5 条限制时直接终止循环
            if len(items) >= self.max_items:
                break

            dd = dd_locator.nth(i)
            a_tag = dd.locator("a")
            span_tag = dd.locator("span")

            # 校验是否存在 a 标签
            if await a_tag.count() == 0:
                continue

            # 提取标题与 href
            title = (await a_tag.inner_text()).strip().replace("\n", " ")
            href = await a_tag.get_attribute("href")

            if not href or not title:
                continue

            full_url = self.build_url(href)

            # 过滤黑名单、重复链接及无效标题
            if any(k in full_url.lower() for k in blacklist):
                continue
            if full_url in visited_urls:
                continue
            if len(title) < 5 or title in ["更多", "详细", "点击查看"]:
                continue

            visited_urls.add(full_url)

            # 4. 提取 <span> 中的日期文本，转换为 datetime
            published_at: Optional[datetime] = None
            if await span_tag.count() > 0:
                date_text = (await span_tag.inner_text()).strip()
                if date_text:
                    try:
                        published_at = datetime.strptime(date_text, "%Y-%m-%d")
                    except Exception:
                        published_at = None

            # 5. 打开详情页抓取正文（使用全量/精准选择器）
            detail_page = await page.context.new_page()
            content = ""
            try:
                await detail_page.goto(
                    full_url, wait_until="domcontentloaded", timeout=15000
                )

                # 精准对齐你的 HTML 结构，按优先级排布：.allZoom 放在最前面
                target_selectors = [
                    ".allZoom",  # 对应你贴出的正文容器 <div class="allZoom">
                    ".article_sub",
                    ".allDetail",
                    ".article_content",
                    "#zoom",
                    ".sse_detail_txt",
                    "div.content_box",
                ]

                # 显式等待 .allZoom 等节点加载出来
                for sel in target_selectors:
                    try:
                        await detail_page.wait_for_selector(sel, timeout=2000)
                        loc = detail_page.locator(sel)
                        if await loc.count() > 0:
                            text_candidate = (await loc.first.inner_text()).strip()
                            if len(text_candidate) > 20:
                                content = text_candidate
                                break
                    except Exception:
                        continue

                # 兜底逻辑：如果上面的类名均失效，自动寻找包裹绝大多数 p 标签的父容器文本
                if not content:
                    p_texts = await detail_page.locator("body p").all_inner_texts()
                    valid_ps = [p.strip() for p in p_texts if len(p.strip()) > 10]
                    if valid_ps:
                        content = "\n".join(valid_ps)

            except Exception as e:
                print(f"⚠️ 详情页抓取失败 [{full_url}]: {e}")
                content = ""
            finally:
                await detail_page.close()

            # 6. 智能提取摘要（段落过滤 + 凑满 40 字）
            summary = ""
            if content:
                paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
                valid_parts = []

                for p in paragraphs:
                    # 过滤短于 25 字且包含落款/编辑信息的噪声行
                    is_tag = len(p) < 25 and any(
                        k in p for k in ["来源", "时间", "编辑", "发布", "记者", "字号"]
                    )
                    if is_tag:
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

            # 7. 生成 ArticleItem 实例并加入列表
            items.append(
                ArticleItem(
                    source_name=self.name,
                    title=title,
                    url=full_url,
                    summary=summary if summary != title else "",
                    content=content,
                    category="热点与动态",
                    published_at=published_at,
                )
            )

        return items
