from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Quote:
    """
    股票实时行情。

    用于描述某一时刻的市场行情。
    """

    symbol: str

    name: Optional[str] = None

    timestamp: Optional[datetime] = None

    price: Optional[float] = None

    prev_close: Optional[float] = None

    open: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    change: Optional[float] = None

    change_percent: Optional[float] = None

    volume: Optional[float] = None

    amount: Optional[float] = None

    turnover_rate: Optional[float] = None

    volume_ratio: Optional[float] = None

    market_cap: Optional[float] = None

    circulating_market_cap: Optional[float] = None

    pe_dynamic: Optional[float] = None

    pe_ttm: Optional[float] = None

    pb: Optional[float] = None

    high_limit: Optional[float] = None

    low_limit: Optional[float] = None