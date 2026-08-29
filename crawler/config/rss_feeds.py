from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class RSSFeed:
    """
    RSS 数据源配置。

    一个 RSSFeed 就代表一个新闻源。
    """

    name: str
    url: str

    category: str = "财经新闻"

    enabled: bool = True

    # 请求超时时间
    timeout: int = 30000

    # 最大抓取数量
    max_items: Optional[int] = None

    # 描述
    description: str = ""


RSS_FEEDS = [

    # ============================================================
    # Google News
    # ============================================================

    RSSFeed(
        name="Google新闻",
        url=(
            "https://news.google.com/rss"
            "?hl=zh-CN"
            "&gl=CN"
            "&ceid=CN:zh-Hans"
        ),
        category="综合新闻",
        description="Google 新闻简体中文",
    ),

    # ============================================================
    # Yahoo Finance
    # ============================================================

    RSSFeed(
        name="Yahoo股市",
        url=(
            "https://tw.stock.yahoo.com/rss"
            "?category=news"
        ),
        category="财经新闻",
        description="Yahoo 股市最新新闻",
    ),

    RSSFeed(
        name="Yahoo台股",
        url=(
            "https://tw.stock.yahoo.com/rss"
            "?category=tw-market"
        ),
        category="台股新闻",
        description="Yahoo 台股市场动态",
    ),

    RSSFeed(
        name="Yahoo国际财经",
        url=(
            "https://tw.stock.yahoo.com/rss"
            "?category=intl-markets"
        ),
        category="国际财经",
        description="Yahoo 国际财经",
    ),

    RSSFeed(
        name="Yahoo研究报告",
        url=(
            "https://tw.stock.yahoo.com/rss"
            "?category=research"
        ),
        category="研究报告",
        description="Yahoo 研究报告",
    ),

    # ============================================================
    # CNBC
    # ============================================================

    RSSFeed(
        name="CNBC",
        url=(
            "https://www.cnbc.com/"
            "id/10000664/device/rss/rss.html"
        ),
        category="国际财经",
        description="CNBC 财经新闻",
    ),

    # ============================================================
    # MarketWatch
    # ============================================================

    RSSFeed(
        name="MarketWatch",
        url=(
            "https://feeds.marketwatch.com/"
            "marketwatch/topstories/"
        ),
        category="国际财经",
        description="MarketWatch 市场新闻",
    ),

    RSSFeed(
        name="MarketWatch股票",
        url=(
            "https://feeds.marketwatch.com/"
            "marketwatch/marketpulse/"
        ),
        category="股票新闻",
        description="MarketWatch 股票市场",
    ),

    # ============================================================
    # Seeking Alpha
    # ============================================================

    RSSFeed(
        name="SeekingAlpha",
        url="https://seekingalpha.com/feed.xml",
        category="投资研究",
        description="Seeking Alpha 投资研究",
    ),

    # ============================================================
    # Bloomberg
    # ============================================================

    RSSFeed(
        name="Bloomberg市场",
        url=(
            "https://feeds.bloomberg.com/"
            "markets/news.rss"
        ),
        category="国际市场",
        description="Bloomberg 市场新闻",
    ),

    RSSFeed(
        name="Bloomberg科技",
        url=(
            "https://feeds.bloomberg.com/"
            "technology/news.rss"
        ),
        category="科技新闻",
        description="Bloomberg 科技新闻",
    ),

    # ============================================================
    # Financial Times
    # ============================================================

    RSSFeed(
        name="FinancialTimes",
        url=(
            "https://www.ft.com/markets"
            "?format=rss"
        ),
        category="国际财经",
        description="Financial Times 市场",
    ),

    # ============================================================
    # Economist
    # ============================================================

    RSSFeed(
        name="TheEconomist",
        url=(
            "https://www.economist.com/"
            "finance-and-economics/rss.xml"
        ),
        category="宏观财经",
        description="The Economist 财经",
    ),
]


def get_enabled_feeds() -> list[RSSFeed]:
    """
    获取启用的 RSS 数据源。
    """

    return [
        feed
        for feed in RSS_FEEDS
        if feed.enabled
    ]


def get_feed(name: str) -> Optional[RSSFeed]:
    """
    根据名称获取 RSS 数据源。
    """

    for feed in RSS_FEEDS:
        if feed.name == name:
            return feed

    return None

