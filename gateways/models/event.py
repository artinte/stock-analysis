from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EventType(str, Enum):
    """
    股票事件类型。
    """

    # ----------------------------------------------------------
    # 公司治理
    # ----------------------------------------------------------

    EXECUTIVE_CHANGE = "executive_change"
    DIRECTOR_CHANGE = "director_change"
    SUPERVISOR_CHANGE = "supervisor_change"

    # ----------------------------------------------------------
    # 股东 / 股权
    # ----------------------------------------------------------

    SHAREHOLDER_CHANGE = "shareholder_change"
    SHARE_REPURCHASE = "share_repurchase"
    SHAREHOLDER_REDUCTION = "shareholder_reduction"
    SHAREHOLDER_INCREASE = "shareholder_increase"

    # ----------------------------------------------------------
    # 融资
    # ----------------------------------------------------------

    IPO = "ipo"
    REFINANCING = "refinancing"
    PRIVATE_PLACEMENT = "private_placement"
    CONVERTIBLE_BOND = "convertible_bond"
    BOND_ISSUANCE = "bond_issuance"

    # ----------------------------------------------------------
    # 资本运作
    # ----------------------------------------------------------

    MERGER = "merger"
    ACQUISITION = "acquisition"
    RESTRUCTURING = "restructuring"
    ASSET_INJECTION = "asset_injection"
    ASSET_SALE = "asset_sale"

    # ----------------------------------------------------------
    # 分红
    # ----------------------------------------------------------

    DIVIDEND = "dividend"
    BONUS_SHARE = "bonus_share"
    STOCK_SPLIT = "stock_split"

    # ----------------------------------------------------------
    # 经营
    # ----------------------------------------------------------

    CONTRACT = "contract"
    MAJOR_PROJECT = "major_project"
    INVESTMENT = "investment"
    INVESTMENT_PROJECT = "investment_project"

    # ----------------------------------------------------------
    # 风险
    # ----------------------------------------------------------

    RISK = "risk"
    REGULATORY_PENALTY = "regulatory_penalty"
    LITIGATION = "litigation"
    PLEDGE = "pledge"
    FREEZE = "freeze"

    # ----------------------------------------------------------
    # 其他
    # ----------------------------------------------------------

    OTHER = "other"


@dataclass(slots=True)
class Event:
    """
    股票 / 上市公司重大事件。

    Event 用于描述一个具有明确时间和事件性质的
    公司级或股票级事件。

    例如：

        董事长变更
        高管辞职
        大股东增持
        大股东减持
        股份回购
        重大合同
        并购重组
        定增
        分红
        诉讼
        监管处罚
        股权质押
        资产出售

    新闻和公告本身不属于 Event。

    新闻：
        描述一篇新闻报道。

    公告：
        描述上市公司发布的一份公告。

    Event：
        从新闻、公告、交易所披露等数据中抽取出来的
        一个结构化事件。
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    symbol: str

    event_type: EventType

    event_time: Optional[datetime] = None

    title: Optional[str] = None

    description: Optional[str] = None

    # ==========================================================
    # 事件主体
    # ==========================================================

    subject: Optional[str] = None

    """
    事件主体。

    例如：

        贵州茅台
        某股东
        董事长
        中国证监会
    """

    counterparty: Optional[str] = None

    """
    事件相关方。

    例如：

        某收购对象
        某投资方
        某交易对手
    """

    # ==========================================================
    # 金额
    # ==========================================================

    amount: Optional[float] = None

    currency: Optional[str] = "CNY"

    # ==========================================================
    # 股份
    # ==========================================================

    shares: Optional[float] = None

    share_ratio: Optional[float] = None

    # ==========================================================
    # 事件状态
    # ==========================================================

    status: Optional[str] = None

    """
    事件状态。

    例如：

        proposed
        pending
        approved
        completed
        cancelled

    中文数据源也可以直接保存：

        拟实施
        进行中
        已完成
        已终止
    """

    # ==========================================================
    # 来源
    # ==========================================================

    source: Optional[str] = None

    source_url: Optional[str] = None

    source_id: Optional[str] = None

    # ==========================================================
    # 相关公告 / 新闻
    # ==========================================================

    announcement_id: Optional[str] = None

    news_id: Optional[str] = None

    # ==========================================================
    # 元数据
    # ==========================================================

    tags: Optional[list[str]] = None

    extra: Optional[dict] = None