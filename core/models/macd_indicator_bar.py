from dataclasses import dataclass
from datetime import datetime

@dataclass
class MACDIndicatorBar:
    """
    纯原生 Python 数据类，没有任何第三方依赖。
    专门用来封装单根 K 线的行情与指标。
    """
    code: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    dif: float | None = None
    dea: float | None = None
    hist: float | None = None
