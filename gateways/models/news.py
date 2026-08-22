from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class NewsType(str, Enum):
    """
    新闻类型。
    """

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
    """
    新闻重要程度。
    """

    LOW = "low"

    NORMAL = "normal"

    HIGH = "high"

    CRITICAL = "critical"


@dataclass(slots=True)
class News:
    """
    股票 / 公司相关新闻。

    News 用于描述新闻媒体、财经网站、资讯平台等
    发布的新闻内容。

    与 Announcement 的区别：

        News
            新闻媒体发布的资讯。

        Announcement
            上市公司、交易所、监管机构等正式披露的信息。

        Event
            从 News / Announcement 中进一步提取出的
            结构化事件。

    例如：

        News
            ↓
        “贵州茅台宣布新产品上市……”

            ↓ EventAnalyzer

        Event
            event_type = MAJOR_PROJECT
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    news_id: Optional[str] = None

    symbol: Optional[str] = None

    title: str = ""

    content: Optional[str] = None

    summary: Optional[str] = None

    # ==========================================================
    # 新闻类型
    # ==========================================================

    news_type: NewsType = NewsType.OTHER

    importance: NewsImportance = NewsImportance.NORMAL

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
    # 新闻媒体信息
    # ==========================================================

    image_url: Optional[str] = None

    video_url: Optional[str] = None

    category: Optional[str] = None

    # ==========================================================
    # 内容质量
    # ==========================================================

    is_original: Optional[bool] = None

    is_reposted: Optional[bool] = None

    duplicate_of: Optional[str] = None

    # ==========================================================
    # 情绪分析
    # ==========================================================

    sentiment: Optional[str] = None

    sentiment_score: Optional[float] = None

    # ==========================================================
    # AI 分析
    # ==========================================================

    ai_summary: Optional[str] = None

    ai_keywords: list[str] = field(default_factory=list)

    ai_topics: list[str] = field(default_factory=list)

    ai_impact: Optional[str] = None

    ai_impact_score: Optional[float] = None

    # ==========================================================
    # 数据来源
    # ==========================================================

    crawler: Optional[str] = None

    crawler_version: Optional[str] = None

    # ==========================================================
    # 扩展数据
    # ==========================================================

    extra: dict = field(default_factory=dict)
