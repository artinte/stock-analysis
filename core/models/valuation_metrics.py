from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class ValuationMetrics:
    """
    估值分析指标。

    所有字段均为根据原始数据计算得到的指标。
    """

    # ==========================================================
    # 市值
    # ==========================================================

    market_cap: Optional[float] = None

    circulating_market_cap: Optional[float] = None

    # ==========================================================
    # PE
    # ==========================================================

    pe_static: Optional[float] = None

    pe_dynamic: Optional[float] = None

    pe_ttm: Optional[float] = None

    # ==========================================================
    # PB
    # ==========================================================

    pb: Optional[float] = None

    # ==========================================================
    # PS
    # ==========================================================

    ps_static: Optional[float] = None

    ps_ttm: Optional[float] = None

    # ==========================================================
    # PEG
    # ==========================================================

    peg: Optional[float] = None

    # ==========================================================
    # 企业价值
    # ==========================================================

    enterprise_value: Optional[float] = None

    ev_ebitda: Optional[float] = None

    # ==========================================================
    # 收益率
    # ==========================================================

    earnings_yield: Optional[float] = None

    dividend_yield: Optional[float] = None