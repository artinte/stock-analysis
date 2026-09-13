from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CryptoKline:
    """加密货币 OHLCV K 线。"""

    symbol: str
    timestamp: datetime

    open: float
    high: float
    low: float
    close: float
    volume: float

    interval: str = "1d"
    amount: float | None = None

    close_time: datetime | None = None
    trade_count: int | None = None

    source: str = ""

    def display(self) -> None:
        print()
        print(f"{self.symbol} K线")
        print(f"    时间:       {self.timestamp}")
        print(f"    周期:       {self.interval}")
        print(f"    开盘:       {self.open}")
        print(f"    最高:       {self.high}")
        print(f"    最低:       {self.low}")
        print(f"    收盘:       {self.close}")
        print(f"    成交量:     {self.volume}")
        print(f"    成交额:     {self.amount}")
        print(f"    成交笔数:   {self.trade_count}")
        print(f"    数据源:     {self.source}")
