from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Valuation:
    """
    股票估值结果。

    Valuation 只保存计算后的估值结果，
    不负责从原始财务数据计算指标。

    原始数据来自：

        Quote
        IncomeStatement
        BalanceSheet
        CashFlow

    计算逻辑由 ValuationAnalyzer 负责。
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    symbol: str

    timestamp: Optional[datetime] = None
    """估值计算对应的行情时间。"""

    report_date: Optional[str] = None
    """估值所使用的最新财务报告期。"""

    source: Optional[str] = None
    """数据来源。"""

    data_type: Optional[str] = None
    """
    数据类型。

    例如：

        calculated
        realtime
        historical
    """

    # ==========================================================
    # 市值
    # ==========================================================

    market_cap: Optional[float] = None
    """总市值。"""

    float_market_cap: Optional[float] = None
    """流通市值。"""

    # ==========================================================
    # PE
    # ==========================================================

    pe_static: Optional[float] = None
    """
    静态市盈率。

    Market Cap / 最近年度归母净利润
    """

    pe_dynamic: Optional[float] = None
    """
    动态市盈率。

    Market Cap / 预测净利润。

    如果没有预测数据，则为 None。
    """

    pe_ttm: Optional[float] = None
    """
    TTM 市盈率。

    Market Cap / 最近四个季度归母净利润之和
    """

    # ==========================================================
    # PB / PS
    # ==========================================================

    pb: Optional[float] = None
    """
    市净率。

    Market Cap / 归属于母公司股东的权益
    """

    ps_static: Optional[float] = None
    """
    静态市销率。

    Market Cap / 最近年度营业收入
    """

    ps_ttm: Optional[float] = None
    """
    TTM 市销率。

    Market Cap / 最近四个季度营业收入之和
    """

    # ==========================================================
    # PEG
    # ==========================================================

    peg: Optional[float] = None
    """
    PEG。

    PE TTM / 净利润增长率
    """

    # ==========================================================
    # 企业价值
    # ==========================================================

    enterprise_value: Optional[float] = None
    """
    企业价值。

    EV = Market Cap + Debt - Cash
    """

    ev_ebitda: Optional[float] = None
    """EV / EBITDA。"""

    # ==========================================================
    # 收益率
    # ==========================================================

    earnings_yield: Optional[float] = None
    """
    盈利收益率。

    1 / PE × 100%
    """

    dividend_yield: Optional[float] = None
    """
    股息率。

    当前版本如果没有可靠的股息数据，则为 None。
    """

    # ==========================================================
    # Display
    # ==========================================================

    def display(self) -> None:
        """显示估值结果。"""

        def fmt(value: Optional[float]) -> str:
            if value is None:
                return "-"

            return f"{value:.2f}"

        def fmt_percent(value: Optional[float]) -> str:
            if value is None:
                return "-"

            return f"{value:.2f}%"

        def fmt_market_cap(
            value: Optional[float],
        ) -> str:
            if value is None:
                return "-"

            if value >= 100_000_000_000:
                return f"{value / 100_000_000_000:.2f} 千亿"

            if value >= 100_000_000:
                return f"{value / 100_000_000:.2f} 亿"

            if value >= 10_000:
                return f"{value / 10_000:.2f} 万"

            return f"{value:,.2f}"

        print("📊 股票估值")

        print("\n基础信息")
        print(f"  股票代码       : {self.symbol}")
        print(f"  报告期         : {self.report_date or '-'}")
        print(f"  数据来源       : {self.source or '-'}")
        print(f"  数据类型       : {self.data_type or '-'}")

        print("\n市值")
        print(f"  总市值         : {fmt_market_cap(self.market_cap)}")
        print(f"  流通市值       : {fmt_market_cap(self.float_market_cap)}")

        print("\nPE")
        print(f"  静态 PE        : {fmt(self.pe_static)}")
        print(f"  动态 PE        : {fmt(self.pe_dynamic)}")
        print(f"  TTM PE         : {fmt(self.pe_ttm)}")

        print("\nPB / PS")
        print(f"  PB             : {fmt(self.pb)}")
        print(f"  静态 PS        : {fmt(self.ps_static)}")
        print(f"  TTM PS         : {fmt(self.ps_ttm)}")

        print("\nPEG")
        print(f"  PEG            : {fmt(self.peg)}")

        print("\n企业价值")
        print(f"  EV             : {fmt_market_cap(self.enterprise_value)}")
        print(f"  EV / EBITDA    : {fmt(self.ev_ebitda)}")

        print("\n收益率")
        print(f"  盈利收益率     : {fmt_percent(self.earnings_yield)}")
        print(f"  股息率         : {fmt_percent(self.dividend_yield)}")
