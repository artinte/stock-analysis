from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Quote:
    """
    股票实时行情快照。

    描述某一个证券在某个时间点的市场状态。


    数据来源：

        Tencent
        银河证券
        AkShare
        TDX
        Tushare
        Yahoo Finance


    数据流：

        DataSource
            ↓
        Gateway
            ↓
        Quote
            ↓
        StockCenter
            ↓
        行情展示 / 策略 / AI分析


    注意：

    Quote 不是历史数据。

    历史价格:
        Kline


    股票静态信息:
        Stock


    财务:
        Financial


    估值:
        Valuation
    """

    # ==========================================================
    # 基础
    # ==========================================================

    symbol: str

    name: Optional[str] = None

    timestamp: Optional[datetime] = None

    source: Optional[str] = None
    """
    数据来源。

    例如:

        tencent
        yinhe
        akshare
    """

    # ==========================================================
    # 当前价格
    # ==========================================================

    price: Optional[float] = None
    """
    当前价格。

    注意：

    部分数据源没有实时行情时，
    可能是最近交易日收盘价。
    """

    prev_close: Optional[float] = None
    """
    昨收。
    """

    open: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    # ==========================================================
    # 涨跌
    # ==========================================================

    change: Optional[float] = None

    change_percent: Optional[float] = None

    amplitude: Optional[float] = None
    """
    振幅。

    %

    计算:

        (high-low)/prev_close
    """

    # ==========================================================
    # 成交
    # ==========================================================

    volume: Optional[float] = None
    """
    成交量。

    A股:
        股

    美股:
        shares
    """

    amount: Optional[float] = None
    """
    成交额。

    A股:
        元

    美股:
        USD
    """

    turnover: Optional[float] = None
    """
    换手率。

    推荐新代码使用。


    兼容旧字段:

        turnover_rate
    """

    turnover_rate: Optional[float] = None
    """
    旧版本字段。

    保留兼容。
    """

    volume_ratio: Optional[float] = None
    """
    量比。
    """

    average_price: Optional[float] = None
    """
    成交均价。

    amount / volume
    """

    # ==========================================================
    # 股本
    # ==========================================================

    total_shares: Optional[float] = None
    """
    总股本。
    """

    float_shares: Optional[float] = None
    """
    流通股本。
    """

    # ==========================================================
    # 市值
    # ==========================================================

    market_cap: Optional[float] = None
    """
    总市值。

    单位:

        亿元
    """

    circulating_market_cap: Optional[float] = None
    """
    流通市值。

    单位:

        亿元
    """

    # ==========================================================
    # 估值
    # ==========================================================

    pe_dynamic: Optional[float] = None
    """
    动态 PE。
    """

    pe_static: Optional[float] = None
    """
    静态 PE。

    增加这个。

    原 Quote 缺少。
    """

    pe_ttm: Optional[float] = None
    """
    TTM PE。
    """

    pb: Optional[float] = None

    ps: Optional[float] = None
    """
    市销率。
    """

    # ==========================================================
    # 涨跌停
    # ==========================================================

    high_limit: Optional[float] = None

    low_limit: Optional[float] = None

    # ==========================================================
    # 交易状态
    # ==========================================================

    status: Optional[str] = None
    """
    股票状态。


    示例:

        trading
        suspended
        delisted
    """

    currency: Optional[str] = None
    """
    交易货币。

    A股:

        CNY


    美股:

        USD
    """
