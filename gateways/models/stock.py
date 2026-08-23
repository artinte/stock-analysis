from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Stock:
    """
    股票基础信息。

    描述证券本身的静态属性。

    不包含：

        行业
        新闻
        公告
        财务
        行情
        估值


    数据来源：

        Gateway
        证券基础接口


    数据流：

        DataSource
            ↓
        StockGateway
            ↓
        Stock
            ↓
        StockCenter


    """

    # ==========================================================
    # 基础
    # ==========================================================

    symbol: str
    """
    股票代码。

    例如:

        600519.SH
        000001.SZ
    """

    name: Optional[str] = None
    """
    股票简称。
    """

    market: Optional[str] = None

    exchange: Optional[str] = None

    # ==========================================================
    # 上市信息
    # ==========================================================

    # 上市日期
    listing_date: Optional[str] = None

    # 上市价格
    ipo_price: Optional[float] = None
    
    # 退市日期
    delisting_date: Optional[str] = None
    
    # 上市状态
    listed_status: Optional[bool] = None

    # ==========================================================
    # 股本
    # ==========================================================

    total_shares: Optional[float] = None

    circulating_shares: Optional[float] = None

    # ==========================================================
    # 公司关联
    # ==========================================================

    # 公司全称
    company_name: Optional[str] = None

    # 数据来源
    source: Optional[str] = None
