from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Valuation:
    """
    股票估值数据。

    用于描述股票当前估值水平：

        市值
        PE
        PB
        PS
        PEG
        EV/EBITDA
        股息率

    数据来源可能包括：

        银河证券
        腾讯行情
        Tushare
        AkShare
        第三方估值服务

    上层业务不应该依赖具体数据源。
    """

    # ==========================================================
    # 基础
    # ==========================================================

    symbol: str

    timestamp: Optional[datetime] = None

    report_date: Optional[str] = None

    # ==========================================================
    # 当前价格
    #
    # 与 Quote.price 保持兼容
    # ==========================================================

    price: Optional[float] = None

    # ==========================================================
    # 市值
    # 单位：亿元
    # ==========================================================

    market_cap: Optional[float] = None

    circulating_market_cap: Optional[float] = None

    # 股本
    # 单位：股
    #

    total_shares: Optional[float] = None

    circulating_shares: Optional[float] = None

    # ==========================================================
    # 市盈率 PE
    # ==========================================================

    # 静态PE
    pe_static: Optional[float] = None

    # 动态PE
    pe_dynamic: Optional[float] = None

    # TTM PE
    pe_ttm: Optional[float] = None

    # ==========================================================
    # PB
    # ==========================================================

    pb: Optional[float] = None

    # ==========================================================
    # PS
    # ==========================================================

    ps_static: Optional[float] = None

    ps_ttm: Optional[float] = None

    # ==========================================================
    # PEG
    # ==========================================================

    peg: Optional[float] = None

    # ==========================================================
    # 股息
    # ==========================================================

    dividend_yield: Optional[float] = None

    # ==========================================================
    # 企业价值
    # ==========================================================

    enterprise_value: Optional[float] = None

    ev_ebitda: Optional[float] = None

    # ==========================================================
    # 盈利收益率
    #
    # 商业化分析常用
    # ==========================================================

    earnings_yield: Optional[float] = None

    # ==========================================================
    # 数据来源
    #
    # 方便以后多源融合
    # ==========================================================

    source: Optional[str] = None

    # 数据质量
    #
    # realtime:
    #     实时
    #
    # delayed:
    #     延迟
    #
    # report:
    #     财报计算
    #
    data_type: Optional[str] = None
