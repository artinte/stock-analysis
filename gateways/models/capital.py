from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class CapitalStructure:
    """
    股票股本结构。

    用于描述上市公司的股本及其流通情况。

    主要包括：

    - 总股本
    - 流通股本
    - 非流通股本
    - 限售股本
    - 股本变更
    - 变更日期
    - 股本来源

    注意：

    CapitalStructure 描述的是股票的股本结构，
    不包含实时价格、成交量、市值等行情数据。

    例如：

        Quote
            ↓
        当前价格、成交量、换手率

        CapitalStructure
            ↓
        总股本、流通股本、限售股本

        Valuation
            ↓
        市值、PE、PB
    """

    # ==========================================================
    # 基础标识
    # ==========================================================

    symbol: str

    """
    股票代码。

    例如：

        600519.SH
        000001.SZ
    """

    # ==========================================================
    # 股本时间
    # ==========================================================

    report_date: Optional[datetime] = None

    """
    股本数据对应日期。

    例如：

        2026-06-30
    """

    change_date: Optional[datetime] = None

    """
    股本发生变更的日期。

    例如：

        配股
        增发
        回购注销
        股权激励
        限售股上市
    """

    # ==========================================================
    # 股本
    # ==========================================================

    total_shares: Optional[float] = None

    """
    总股本。

    单位建议统一为：

        股

    例如：

        1,000,000,000
    """

    circulating_shares: Optional[float] = None

    """
    流通股本。

    单位：

        股
    """

    float_shares: Optional[float] = None

    """
    自由流通股本。

    如果数据源能够区分：

        流通股本
        自由流通股本

    则可以分别保存。

    如果无法区分，可以为 None。
    """

    restricted_shares: Optional[float] = None

    """
    限售股本。

    单位：

        股
    """

    non_circulating_shares: Optional[float] = None

    """
    非流通股本。

    单位：

        股
    """

    # ==========================================================
    # 股本比例
    # ==========================================================

    circulating_ratio: Optional[float] = None

    """
    流通股占总股本比例。

    单位：

        %

    通常：

        circulating_shares / total_shares * 100
    """

    float_ratio: Optional[float] = None

    """
    自由流通股占总股本比例。

    单位：

        %
    """

    restricted_ratio: Optional[float] = None

    """
    限售股占总股本比例。

    单位：

        %
    """

    # ==========================================================
    # 股本变更
    # ==========================================================

    change_type: Optional[str] = None

    """
    股本变更类型。

    例如：

        IPO
        增发
        配股
        可转债转股
        股权激励
        送股
        转增
        回购注销
        限售股上市
        其他
    """

    change_shares: Optional[float] = None

    """
    本次股本变更数量。

    单位：

        股

    增加为正数，
    减少为负数。
    """

    change_reason: Optional[str] = None

    """
    股本变更原因。
    """

    # ==========================================================
    # 市值
    # ==========================================================

    market_cap: Optional[float] = None

    """
    根据总股本计算的总市值。

    注意：

    这里属于股本结构相关的衍生数据。

    单位建议：

        亿元
    """

    circulating_market_cap: Optional[float] = None

    """
    流通市值。

    单位：

        亿元
    """

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    """
    数据来源。

    例如：

        yinhe
        cninfo
        sse
        szse
        eastmoney
        tencent
    """

    source_name: Optional[str] = None

    """
    数据源显示名称。

    例如：

        银河证券
        巨潮资讯
        上海证券交易所
        深圳证券交易所
        东方财富
    """

    # ==========================================================
    # 数据时间
    # ==========================================================

    fetched_at: Optional[datetime] = None

    """
    数据实际获取时间。
    """

    # ==========================================================
    # 原始数据
    # ==========================================================

    raw_data: Optional[dict] = None

    """
    保存数据源原始字段。

    方便：

        数据清洗
        调试
        字段扩展
        数据源切换
    """
