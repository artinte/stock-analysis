from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Valuation:
    """
    股票估值数据。

    主要用于：

        PE
        PB
        PS
        PEG
        市值

    等估值指标。
    """

    symbol: str

    timestamp: Optional[datetime] = None

    price: Optional[float] = None

    market_cap: Optional[float] = None

    circulating_market_cap: Optional[float] = None

    # 市盈率
    pe_static: Optional[float] = None

    pe_dynamic: Optional[float] = None

    pe_ttm: Optional[float] = None

    # 市净率
    pb: Optional[float] = None

    # 市销率
    ps_static: Optional[float] = None

    ps_ttm: Optional[float] = None

    # PEG
    peg: Optional[float] = None

    # 股息率
    dividend_yield: Optional[float] = None

    # 企业价值
    enterprise_value: Optional[float] = None

    # EV/EBITDA
    ev_ebitda: Optional[float] = None

    # 数据日期
    report_date: Optional[str] = None