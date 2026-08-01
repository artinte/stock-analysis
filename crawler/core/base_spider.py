from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urljoin
from playwright.async_api import Page
from core.browser import browser_manager
from core.models import ArticleItem


class BaseSpider(ABC):
    name: str = "base_spider"
    start_url: str = ""

    @abstractmethod
    async def parse(self, page: Page) -> List[ArticleItem]:
        """子类需实现的具体解析逻辑"""
        pass

    def build_url(self, href: str) -> str:
        """统一将相对路径转换为绝对路径"""
        return urljoin(self.start_url, href)

    async def run(self) -> List[ArticleItem]:
        """统一的爬虫执行流与异常处理"""
        print(f"🕵️ [{self.name}] 正在准备抓取: {self.start_url}")
        page = await browser_manager.get_page()
        try:
            await page.goto(
                self.start_url, wait_until="domcontentloaded", timeout=30000
            )
            items = await self.parse(page)
            print(f"✅ [{self.name}] 抓取完成，获取到 {len(items)} 条数据")
            return items
        except Exception as e:
            print(f"❌ [{self.name}] 抓取失败: {e}")
            return []
        finally:
            # 仅关闭当前 Context/Page，保持全局 Browser 存活
            await page.context.close()