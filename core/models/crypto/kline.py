from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Kline:
    """通用 OHLCV K 线。"""

    symbol: str
    timestamp: datetime

    open: float
    high: float
    low: float
    close: float
    volume: float

    interval: str = "1d"
    amount: float | None = None
    source: str = ""
