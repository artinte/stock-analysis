from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Quote:
    """
    股票行情快照。

    当前银河数据源使用最近交易日 K 线构造行情，
    因此 price 表示最近交易日收盘价，而非实时成交价。
    """

    symbol: str

    name: Optional[str] = None

    timestamp: Optional[datetime] = None

    # ----------------------------------------------------------
    # 价格
    # ----------------------------------------------------------

    price: Optional[float] = None

    prev_close: Optional[float] = None

    open: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    # ----------------------------------------------------------
    # 涨跌
    # ----------------------------------------------------------

    change: Optional[float] = None

    change_percent: Optional[float] = None

    # ----------------------------------------------------------
    # 成交
    # ----------------------------------------------------------

    volume: Optional[float] = None

    amount: Optional[float] = None

    turnover_rate: Optional[float] = None

    volume_ratio: Optional[float] = None

    # ----------------------------------------------------------
    # 股本 / 市值
    # ----------------------------------------------------------

    total_shares: Optional[float] = None

    float_shares: Optional[float] = None

    market_cap: Optional[float] = None

    circulating_market_cap: Optional[float] = None

    # ----------------------------------------------------------
    # 估值
    # ----------------------------------------------------------

    pe_dynamic: Optional[float] = None

    pe_ttm: Optional[float] = None

    pb: Optional[float] = None

    # ----------------------------------------------------------
    # 涨跌停
    # ----------------------------------------------------------

    high_limit: Optional[float] = None

    low_limit: Optional[float] = None

    # ----------------------------------------------------------
    # 其他行情指标
    # ----------------------------------------------------------

    average_price: Optional[float] = None

    amplitude: Optional[float] = None
