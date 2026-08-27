from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class NewsAnalysis:
    """
    新闻 AI / NLP 分析结果。

    News 是事实数据。
    NewsAnalysis 是对 News 的分析结果。

    两者生命周期可以完全独立。
    """

    # ==========================================================
    # 关联新闻
    # ==========================================================

    news_id: str

    # ==========================================================
    # 分析时间
    # ==========================================================

    analyzed_at: Optional[datetime] = None

    # ==========================================================
    # 情绪分析
    # ==========================================================

    sentiment: Optional[str] = None

    sentiment_score: Optional[float] = None

    # ==========================================================
    # AI 摘要
    # ==========================================================

    summary: Optional[str] = None

    # ==========================================================
    # AI 关键词 / 主题
    # ==========================================================

    keywords: list[str] = field(default_factory=list)

    topics: list[str] = field(default_factory=list)

    # ==========================================================
    # 市场影响
    # ==========================================================

    impact: Optional[str] = None

    impact_score: Optional[float] = None

    # ==========================================================
    # 分析模型
    # ==========================================================

    model: Optional[str] = None

    model_version: Optional[str] = None

    # ==========================================================
    # 扩展
    # ==========================================================

    extra: dict = field(default_factory=dict)