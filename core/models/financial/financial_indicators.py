from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class FinancialIndicators:
    """
    财务分析指标。

    注意：

    这里主要保存由财务报表数据计算得到的指标，
    不直接代表某一张财务报表。
    """

    # ==========================================================
    # 盈利能力
    # ==========================================================

    gross_margin: Optional[float] = None
    """毛利率。"""

    operating_margin: Optional[float] = None
    """营业利润率。"""

    net_margin: Optional[float] = None
    """净利率。"""

    roe: Optional[float] = None
    """
    净资产收益率。
    """

    roa: Optional[float] = None
    """
    总资产收益率。
    """

    roic: Optional[float] = None
    """
    投入资本回报率。
    """

    # ==========================================================
    # 成长能力
    # ==========================================================

    revenue_growth: Optional[float] = None
    """营业收入同比增长率。"""

    revenue_yoy: Optional[float] = None
    """营业收入同比增长率。"""

    revenue_qoq: Optional[float] = None
    """营业收入环比增长率。"""

    profit_growth: Optional[float] = None
    """净利润增长率。"""

    net_profit_yoy: Optional[float] = None
    """净利润同比增长率。"""

    net_profit_qoq: Optional[float] = None
    """净利润环比增长率。"""

    eps_growth: Optional[float] = None
    """EPS 增长率。"""

    # ==========================================================
    # 财务健康
    # ==========================================================

    debt_to_asset_ratio: Optional[float] = None
    """
    资产负债率。
    """

    current_ratio: Optional[float] = None
    """
    流动比率。
    """

    quick_ratio: Optional[float] = None
    """
    速动比率。
    """

    interest_coverage: Optional[float] = None
    """
    利息保障倍数。
    """

    # ==========================================================
    # 营运能力
    # ==========================================================

    receivable_turnover: Optional[float] = None
    """
    应收账款周转率。
    """

    inventory_turnover: Optional[float] = None
    """
    存货周转率。
    """

    # ==========================================================
    # 现金流质量
    # ==========================================================

    cash_flow_quality: Optional[float] = None
    """
    现金流质量。

    通常：

        经营现金流 / 净利润
    """

    # ==========================================================
    # 每股指标
    # ==========================================================

    book_value_per_share: Optional[float] = None
    """每股净资产。"""

    operating_cash_flow_per_share: Optional[float] = None
    """每股经营现金流。"""

    # ==========================================================
    # 股东回报
    # ==========================================================

    dividend: Optional[float] = None
    """每股股利。"""

    dividend_yield: Optional[float] = None
    """股息率。"""

    payout_ratio: Optional[float] = None
    """股利支付率。"""

    def display(self) -> None:
        """
        显示财务指标。
        """

        print("财务指标")

        print("\n盈利能力")
        print(f"  毛利率         : {self._format_percent(self.gross_margin)}")
        print(
            f"  营业利润率     : "
            f"{self._format_percent(self.operating_margin)}"
        )
        print(f"  净利率         : {self._format_percent(self.net_margin)}")
        print(f"  ROE            : {self._format_percent(self.roe)}")
        print(f"  ROA            : {self._format_percent(self.roa)}")
        print(f"  ROIC           : {self._format_percent(self.roic)}")

        print("\n成长能力")
        print(f"  营收增长       : {self._format_percent(self.revenue_growth)}")
        print(f"  营收同比       : {self._format_percent(self.revenue_yoy)}")
        print(f"  营收环比       : {self._format_percent(self.revenue_qoq)}")
        print(f"  利润增长       : {self._format_percent(self.profit_growth)}")
        print(f"  净利润同比     : {self._format_percent(self.net_profit_yoy)}")
        print(f"  净利润环比     : {self._format_percent(self.net_profit_qoq)}")
        print(f"  EPS 增长       : {self._format_percent(self.eps_growth)}")

        print("\n财务健康")
        print(
            f"  资产负债率     : "
            f"{self._format_percent(self.debt_to_asset_ratio)}"
        )
        print(f"  流动比率       : {self._format_ratio(self.current_ratio)}")
        print(f"  速动比率       : {self._format_ratio(self.quick_ratio)}")
        print(
            f"  利息保障倍数   : "
            f"{self._format_ratio(self.interest_coverage)}"
        )

        print("\n营运能力")
        print(
            f"  应收账款周转率 : "
            f"{self._format_ratio(self.receivable_turnover)}"
        )
        print(
            f"  存货周转率     : "
            f"{self._format_ratio(self.inventory_turnover)}"
        )

        print("\n现金流质量")
        print(
            f"  现金流质量     : "
            f"{self._format_ratio(self.cash_flow_quality)}"
        )

        print("\n每股指标")
        print(
            f"  每股净资产     : "
            f"{self._format_number(self.book_value_per_share)}"
        )
        print(
            f"  每股经营现金流 : "
            f"{self._format_number(self.operating_cash_flow_per_share)}"
        )

        print("\n股东回报")
        print(f"  每股股利       : {self._format_number(self.dividend)}")
        print(f"  股息率         : {self._format_percent(self.dividend_yield)}")
        print(f"  股利支付率     : {self._format_percent(self.payout_ratio)}")

    @staticmethod
    def _format_percent(value: Optional[float]) -> str:
        if value is None:
            return "-"

        return f"{value:.2f}%"

    @staticmethod
    def _format_ratio(value: Optional[float]) -> str:
        if value is None:
            return "-"

        return f"{value:.2f}x"

    @staticmethod
    def _format_number(value: Optional[float]) -> str:
        if value is None:
            return "-"

        return f"{value:.4f}"