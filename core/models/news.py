from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class NewsType(str, Enum):
    """新闻类型。"""

    COMPANY = "company"
    INDUSTRY = "industry"
    MARKET = "market"
    MACRO = "macro"
    POLICY = "policy"
    FINANCE = "finance"
    RESEARCH = "research"
    INTERNATIONAL = "international"
    OTHER = "other"


class NewsImportance(str, Enum):
    """新闻重要程度。"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class News:
    """
    新闻数据模型。

    News 只描述新闻本身，不保存 AI 分析结果。

    News
        ↓
    NewsAnalyzer
        ↓
    NewsAnalysis
        ↓
    EventAnalyzer
        ↓
    Event
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    news_id: Optional[str] = None

    title: str = ""

    content: Optional[str] = None

    summary: Optional[str] = None

    # ==========================================================
    # 新闻类型
    # ==========================================================

    news_type: NewsType = NewsType.OTHER

    importance: NewsImportance = NewsImportance.NORMAL

    category: Optional[str] = None

    # ==========================================================
    # 时间
    # ==========================================================

    publish_time: Optional[datetime] = None

    crawl_time: Optional[datetime] = None

    update_time: Optional[datetime] = None

    # ==========================================================
    # 来源
    # ==========================================================

    source: Optional[str] = None

    source_name: Optional[str] = None

    source_url: Optional[str] = None

    source_id: Optional[str] = None

    author: Optional[str] = None

    crawler: Optional[str] = None

    crawler_version: Optional[str] = None

    # ==========================================================
    # 关联证券
    # ==========================================================

    symbols: list[str] = field(default_factory=list)

    company_names: list[str] = field(default_factory=list)

    # ==========================================================
    # 分类标签
    # ==========================================================

    tags: list[str] = field(default_factory=list)

    keywords: list[str] = field(default_factory=list)

    # ==========================================================
    # 媒体信息
    # ==========================================================

    image_url: Optional[str] = None

    video_url: Optional[str] = None

    # ==========================================================
    # 内容质量
    # ==========================================================

    is_original: Optional[bool] = None

    is_reposted: Optional[bool] = None

    duplicate_of: Optional[str] = None

    # ==========================================================
    # 扩展数据
    # ==========================================================

    extra: dict = field(default_factory=dict)

    def display(self) -> None:
        """
        格式化打印新闻信息。
        """

        def format_time(value: Optional[datetime]) -> str:
            if value is None:
                return "-"
            return value.strftime("%Y-%m-%d %H:%M:%S")

        def format_list(values: list[str]) -> str:
            return ", ".join(values) if values else "-"

        def format_bool(value: Optional[bool]) -> str:
            if value is None:
                return "-"
            return "是" if value else "否"

        print(f"📰 {self.title or '-'}")

        print(f"ID:          {self.news_id or '-'}")
        print(f"类型:        {self.news_type.value}")
        print(f"重要程度:    {self.importance.value}")
        print(f"分类:        {self.category or '-'}")

        print()

        print(f"发布时间:    {format_time(self.publish_time)}")
        print(f"抓取时间:    {format_time(self.crawl_time)}")
        print(f"更新时间:    {format_time(self.update_time)}")

        print()

        print(f"来源:        {self.source or '-'}")
        print(f"来源名称:    {self.source_name or '-'}")
        print(f"作者:        {self.author or '-'}")
        print(f"链接:        {self.source_url or '-'}")

        print()

        print(f"关联股票:    {format_list(self.symbols)}")
        print(f"关联公司:    {format_list(self.company_names)}")

        print(f"标签:        {format_list(self.tags)}")
        print(f"关键词:      {format_list(self.keywords)}")

        print()

        print(f"原创:        {format_bool(self.is_original)}")
        print(f"转载:        {format_bool(self.is_reposted)}")
        print(f"重复新闻:    {self.duplicate_of or '-'}")

        print()

        if self.summary:
            print("摘要:")
            print(self.summary)

        if self.content:
            print()
            print("正文:")
            print(self.content)

        if self.image_url:
            print()
            print(f"图片:        {self.image_url}")

        if self.video_url:
            print(f"视频:        {self.video_url}")

        if self.crawler:
            print()
            print(f"爬虫:        {self.crawler}")

        if self.crawler_version:
            print(f"爬虫版本:    {self.crawler_version}")

        if self.extra:
            print()
            print("扩展数据:")
            for key, value in self.extra.items():
                print(f"  {key}: {value}")
