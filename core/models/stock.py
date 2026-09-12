from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from common.enums.exchange import Exchange
from utils.stock_mapping import exchange_name


@dataclass(slots=True)
class Stock:
    """
    股票基础信息，描述证券本身的静态属性。

    不包含：行业、新闻、公告、财务、行情、估值

    数据流：
        DataSource -> StockGateway -> Stock -> StockCenter
    """

    # 股票代码，例如 600519.SH
    symbol: str

    # 股票简称，例如 贵州茅台
    name: str | None = None

    # 上市板块，例如 主板、科创板、创业板
    market: str | None = None

    # 交易所
    exchange: Exchange | None = None

    # 上市日期
    listing_date: date | None = None

    # 上市价格
    ipo_price: float | None = None

    # 退市日期
    delisting_date: date | None = None

    # 上市状态
    listed_status: bool | None = None

    # 公司全称
    company_name: str | None = None

    # 数据来源
    source: str | None = None

    def to_dict(self) -> dict:
        """
        将 Stock 对象转换为可 JSON 序列化的字典。
        """
        return {
            "symbol": self.symbol,
            "name": self.name,
            "market": self.market,
            "exchange": self.exchange.value if self.exchange else None,
            "listing_date": (
                self.listing_date.isoformat() if self.listing_date is not None else None
            ),
            "ipo_price": self.ipo_price,
            "delisting_date": (
                self.delisting_date.isoformat()
                if self.delisting_date is not None
                else None
            ),
            "listed_status": self.listed_status,
            "company_name": self.company_name,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Stock:
        """
        从字典恢复 Stock 对象。
        """

        listing_date = data.get("listing_date")
        if listing_date and listing_date != "-":
            listing_date = date.fromisoformat(listing_date)
        else:
            listing_date = None

        delisting_date = data.get("delisting_date")
        if delisting_date and delisting_date != "-":
            delisting_date = date.fromisoformat(delisting_date)
        else:
            delisting_date = None

        exchange = data.get("exchange")
        if exchange and exchange != "-":
            exchange = Exchange(exchange)
        else:
            exchange = None

        return cls(
            symbol=data.get("symbol", ""),
            name=data.get("name"),
            market=data.get("market"),
            exchange=exchange,
            listing_date=listing_date,
            ipo_price=data.get("ipo_price"),
            delisting_date=delisting_date,
            listed_status=data.get("listed_status"),
            company_name=data.get("company_name"),
            source=data.get("source"),
        )

    def display(self) -> None:
        """
        打印股票基础信息。
        """
        print("✅ 股票基础信息")
        print(f"  股票代码：{self.symbol}")
        print(f"  股票名称：{self.name or '-'}")
        print(f"  上市板块：{self.market or '-'}")
        print(f"  交易所：{exchange_name(self.exchange) or '-'}")
        print(
            f"  上市日期："
            f"{self.listing_date if self.listing_date is not None else '-'}"
        )
        print(
            f"  上市价格：" f"{self.ipo_price if self.ipo_price is not None else '-'}"
        )
        print(
            f"  退市日期："
            f"{self.delisting_date if self.delisting_date is not None else '-'}"
        )
        print(
            f"  上市状态："
            f"{self.listed_status if self.listed_status is not None else '-'}"
        )
        print(f"  公司全称：{self.company_name or '-'}")
        print(f"  数据来源：{self.source or '-'}")
