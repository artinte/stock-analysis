from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models.constants import Interval


@dataclass(slots=True)
class Kline:
    """
    标准 K 线数据。

    无论底层使用：

        AkShare
        银河
        TDX
        Tushare
        Baostock

    最终都转换成该统一结构。
    """

    symbol: str

    timestamp: datetime

    interval: Interval

    open: float

    high: float

    low: float

    close: float

    volume: Optional[float] = None

    amount: Optional[float] = None

    turnover: Optional[float] = None

    change: Optional[float] = None

    change_percent: Optional[float] = None

    pre_close: Optional[float] = None

    adjusted: bool = False