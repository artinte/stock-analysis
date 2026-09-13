from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CryptoQuote:
    symbol: str
    exchange: str

    last_price: float
    prev_close: float | None = None

    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None

    change: float | None = None
    change_percent: float | None = None

    volume: float | None = None
    amount: float | None = None
    trade_count: int | None = None

    source: str = ""
    timestamp: int | None = None

    def display(self) -> None:
        print()
        print("=" * 60)
        print(f"{self.symbol} 行情")
        print("=" * 60)

        print(f"    交易对:     {self.symbol}")
        print(f"    交易所:     {self.exchange}")
        print(f"    最新价:     {self.last_price}")
        print(f"    昨收价:     {self.prev_close}")
        print(f"    开盘价:     {self.open_price}")
        print(f"    最高价:     {self.high_price}")
        print(f"    最低价:     {self.low_price}")
        print(f"    涨跌额:     {self.change}")
        print(f"    涨跌幅:     {self.change_percent}%")
        print(f"    成交量:     {self.volume}")
        print(f"    成交额:     {self.amount}")
        print(f"    成交笔数:   {self.trade_count}")
        print(f"    数据源:     {self.source}")
