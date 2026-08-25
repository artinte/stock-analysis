from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class InstitutionType(str, Enum):
    """
    机构类型。

    用于区分不同类型的投资机构。
    """

    FUND = "fund"
    BROKER = "broker"
    INSURANCE = "insurance"
    SOCIAL_SECURITY = "social_security"
    QFII = "qfii"
    BANK = "bank"
    TRUST = "trust"
    PRIVATE_FUND = "private_fund"
    INVESTMENT_COMPANY = "investment_company"
    ASSET_MANAGEMENT = "asset_management"
    FOREIGN_INSTITUTION = "foreign_institution"
    OTHER = "other"


class InstitutionAction(str, Enum):
    """
    机构对股票的行为。
    """

    BUY = "buy"
    SELL = "sell"
    INCREASE = "increase"
    REDUCE = "reduce"
    HOLD = "hold"
    NEW_POSITION = "new_position"
    EXIT = "exit"
    UNKNOWN = "unknown"


class RatingType(str, Enum):
    """
    机构研究评级。
    """

    STRONG_BUY = "strong_buy"
    BUY = "buy"
    OVERWEIGHT = "overweight"
    HOLD = "hold"
    UNDERWEIGHT = "underweight"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class Institution:
    """
    投资机构基本信息。

    例如：

        华夏基金
        易方达基金
        中金公司
        高盛
        摩根士丹利
        全国社保基金
        香港中央结算有限公司
    """

    institution_id: Optional[str] = None

    name: str = ""

    institution_type: Optional[InstitutionType] = None

    country: Optional[str] = None

    region: Optional[str] = None

    description: Optional[str] = None

    website: Optional[str] = None

    source: Optional[str] = None

    source_url: Optional[str] = None

    extra: dict = field(default_factory=dict)


@dataclass(slots=True)
class InstitutionHolding:
    """
    机构持股信息。

    描述：

        某个机构在某个报告期持有某只股票多少股份。
    """

    symbol: str

    institution_id: Optional[str] = None

    institution_name: Optional[str] = None

    institution_type: Optional[InstitutionType] = None

    # ==========================================================
    # 报告期
    # ==========================================================

    report_date: Optional[datetime] = None

    # ==========================================================
    # 持股
    # ==========================================================

    shares: Optional[float] = None

    holding_ratio: Optional[float] = None

    market_value: Optional[float] = None

    # ==========================================================
    # 持股变化
    # ==========================================================

    previous_shares: Optional[float] = None

    change_shares: Optional[float] = None

    change_ratio: Optional[float] = None

    action: InstitutionAction = InstitutionAction.UNKNOWN

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    source_url: Optional[str] = None

    extra: dict = field(default_factory=dict)


@dataclass(slots=True)
class InstitutionRating:
    """
    机构对股票的研究评级。

    例如：

        中信证券 → 买入
        中金公司 → 跑赢行业
        某机构 → 增持
    """

    symbol: str

    institution_id: Optional[str] = None

    institution_name: Optional[str] = None

    rating: Optional[RatingType] = None

    rating_text: Optional[str] = None

    # ==========================================================
    # 目标价格
    # ==========================================================

    target_price: Optional[float] = None

    target_price_low: Optional[float] = None

    target_price_high: Optional[float] = None

    # ==========================================================
    # 当前价格
    # ==========================================================

    price_at_rating: Optional[float] = None

    # ==========================================================
    # 时间
    # ==========================================================

    rating_date: Optional[datetime] = None

    # ==========================================================
    # 研究报告
    # ==========================================================

    report_title: Optional[str] = None

    report_id: Optional[str] = None

    report_url: Optional[str] = None

    # ==========================================================
    # 来源
    # ==========================================================

    source: Optional[str] = None

    source_url: Optional[str] = None

    extra: dict = field(default_factory=dict)


@dataclass(slots=True)
class InstitutionResearch:
    """
    机构调研信息。

    描述机构对上市公司的调研活动。
    """

    symbol: str

    institution_id: Optional[str] = None

    institution_name: Optional[str] = None

    institution_type: Optional[InstitutionType] = None

    research_date: Optional[datetime] = None

    research_type: Optional[str] = None

    """
    例如：

        现场调研
        电话会议
        视频会议
        其他
    """

    participants: list[str] = field(default_factory=list)

    topic: Optional[str] = None

    summary: Optional[str] = None

    source: Optional[str] = None

    source_url: Optional[str] = None

    extra: dict = field(default_factory=dict)


@dataclass(slots=True)
class InstitutionData:
    """
    股票相关的机构数据。

    一个股票可以对应大量机构：

        股票
          │
          ├── 机构持股
          │
          ├── 机构评级
          │
          └── 机构调研

    因此这里不直接把机构字段塞进 Stock。
    """

    symbol: str

    # ==========================================================
    # 机构持股
    # ==========================================================

    holdings: list[InstitutionHolding] = field(default_factory=list)

    # ==========================================================
    # 机构评级
    # ==========================================================

    ratings: list[InstitutionRating] = field(default_factory=list)

    # ==========================================================
    # 机构调研
    # ==========================================================

    research: list[InstitutionResearch] = field(default_factory=list)

    # ==========================================================
    # 更新时间
    # ==========================================================

    updated_at: Optional[datetime] = None

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    extra: dict = field(default_factory=dict)
