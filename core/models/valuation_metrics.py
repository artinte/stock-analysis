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

    def display(self) -> None:
        """
        以可读的估值分析报告形式输出。
        """

        def fmt(value: Optional[float], digits: int = 2) -> str:
            if value is None:
                return "-"

            return f"{value:,.{digits}f}"

        def fmt_ratio(value: Optional[float]) -> str:
            if value is None:
                return "-"

            return f"{value:.2f}"

        def fmt_percent(value: Optional[float]) -> str:
            if value is None:
                return "-"

            return f"{value:.2f}%"

        def fmt_market_cap(value: Optional[float]) -> str:
            if value is None:
                return "-"

            return f"{value:,.2f} 亿元"

        def row(name: str, value: str) -> None:
            print(f"  {name:<18} {value}")

        print("=" * 60)
        print("                    估值分析")
        print("=" * 60)

        # ------------------------------------------------------
        # 市值
        # ------------------------------------------------------

        print("\n【市值】")

        row(
            "总市值",
            fmt_market_cap(self.market_cap),
        )

        row(
            "流通市值",
            fmt_market_cap(self.circulating_market_cap),
        )

        # ------------------------------------------------------
        # PE
        # ------------------------------------------------------

        print("\n【市盈率 PE】")

        row(
            "静态 PE",
            fmt_ratio(self.pe_static),
        )

        row(
            "动态 PE",
            fmt_ratio(self.pe_dynamic),
        )

        row(
            "PE-TTM",
            fmt_ratio(self.pe_ttm),
        )

        # ------------------------------------------------------
        # PB
        # ------------------------------------------------------

        print("\n【市净率 PB】")

        row(
            "PB",
            fmt_ratio(self.pb),
        )

        # ------------------------------------------------------
        # PS
        # ------------------------------------------------------

        print("\n【市销率 PS】")

        row(
            "静态 PS",
            fmt_ratio(self.ps_static),
        )

        row(
            "PS-TTM",
            fmt_ratio(self.ps_ttm),
        )

        # ------------------------------------------------------
        # PEG
        # ------------------------------------------------------

        print("\n【PEG】")

        row(
            "PEG",
            fmt_ratio(self.peg),
        )

        # ------------------------------------------------------
        # 企业价值
        # ------------------------------------------------------

        print("\n【企业价值 EV】")

        row(
            "企业价值",
            fmt_market_cap(self.enterprise_value),
        )

        row(
            "EV / EBITDA",
            fmt_ratio(self.ev_ebitda),
        )

        # ------------------------------------------------------
        # 收益率
        # ------------------------------------------------------

        print("\n【收益率】")

        row(
            "盈利收益率",
            fmt_percent(self.earnings_yield),
        )

        row(
            "股息率",
            fmt_percent(self.dividend_yield),
        )

        print("\n" + "=" * 60)
