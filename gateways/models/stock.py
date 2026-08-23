from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from common.constants import Exchange
from utils.stock_mapping import exchange_name


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

    def display(self) -> None:
        """
        打印股票基础信息。
        """
        print("✅ 股票基础信息")
        print(f"  股票代码：{self.symbol}")
        print(f"  股票名称：{self.name or '-'}")
        print(f"  上市板块：{self.market or '-'}")
        print(f"  交易所：{exchange_name(self.exchange) or '-'}")
        print(f"  上市日期：{self.listing_date or '-'}")
        print(f"  上市价格：{self.ipo_price if self.ipo_price is not None else '-'}")
        print(f"  退市日期：{self.delisting_date or '-'}")
        print(
            f"  上市状态：{self.listed_status if self.listed_status is not None else '-'}"
        )
        print(f"  公司全称：{self.company_name or '-'}")
        print(f"  数据来源：{self.source or '-'}")
