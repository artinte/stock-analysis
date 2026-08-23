from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from gateways.models.constants import Exchange


@dataclass(slots=True)
class Stock:
    """
    股票基础信息。

    描述证券本身的静态属性。

    不包含：行业、新闻、公告、财务、行情、估值

    数据流：DataSource -> StockGateway -> Stock -> StockCenter
    """

    # 股票代码，例如 600519.SH
    symbol: str

    # 股票简称：例如 贵州茅台
    name: Optional[str] = None

    # 主板、科创版、创业板
    market: Optional[str] = None

    # 交易所
    exchange: Optional[Exchange] = None

    # 上市日期
    listing_date: Optional[str] = None

    # 上市价格
    ipo_price: Optional[float] = None

    # 退市日期
    delisting_date: Optional[str] = None

    # 上市状态
    listed_status: Optional[bool] = None

    # 公司全称
    company_name: Optional[str] = None

    # 数据来源
    source: Optional[str] = None
