from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class IncomeStatement:
    """
    利润表。

    描述公司在某一个财务报告期内的经营成果。
    """

    # ==========================================================
    # 收入
    # ==========================================================

    revenue: Optional[float] = None
    """营业收入。"""

    operating_income: Optional[float] = None
    """营业收入。"""

    total_operating_income: Optional[float] = None
    """营业总收入。"""

    # ==========================================================
    # 成本
    # ==========================================================

    operating_cost: Optional[float] = None
    """营业成本。"""

    total_operating_cost: Optional[float] = None
    """营业总成本。"""

    selling_expense: Optional[float] = None
    """销售费用。"""

    administrative_expense: Optional[float] = None
    """管理费用。"""

    financial_expense: Optional[float] = None
    """财务费用。"""

    rd_expense: Optional[float] = None
    """研发费用。"""

    # ==========================================================
    # 利润
    # ==========================================================

    gross_profit: Optional[float] = None
    """毛利润。"""

    operating_profit: Optional[float] = None
    """营业利润。"""

    total_profit: Optional[float] = None
    """利润总额。"""

    ebit: Optional[float] = None
    """息税前利润。"""

    ebitda: Optional[float] = None
    """息税折旧摊销前利润。"""

    income_tax: Optional[float] = None
    """所得税费用。"""

    net_profit: Optional[float] = None
    """净利润。"""

    net_profit_attributable: Optional[float] = None
    """归属于母公司股东的净利润。"""

    non_recurring_net_profit: Optional[float] = None
    """扣除非经常性损益后的净利润。"""

    # ==========================================================
    # 每股收益
    # ==========================================================

    eps: Optional[float] = None
    """基本每股收益。"""

    diluted_eps: Optional[float] = None
    """稀释每股收益。"""
    
    def display(self) -> None:
        """
        显示利润表。
        """

        print("利润表")

        print("\n营业收入")
        print(f"  营业收入       : {self._format_amount(self.revenue)}")
        print(f"  营业收入       : {self._format_amount(self.operating_income)}")
        print(f"  营业总收入     : {self._format_amount(self.total_operating_income)}")

        print("\n成本费用")
        print(f"  营业成本       : {self._format_amount(self.operating_cost)}")
        print(f"  营业总成本     : {self._format_amount(self.total_operating_cost)}")
        print(f"  销售费用       : {self._format_amount(self.selling_expense)}")
        print(f"  管理费用       : {self._format_amount(self.administrative_expense)}")
        print(f"  财务费用       : {self._format_amount(self.financial_expense)}")
        print(f"  研发费用       : {self._format_amount(self.rd_expense)}")

        print("\n利润")
        print(f"  毛利润         : {self._format_amount(self.gross_profit)}")
        print(f"  营业利润       : {self._format_amount(self.operating_profit)}")
        print(f"  利润总额       : {self._format_amount(self.total_profit)}")
        print(f"  EBIT           : {self._format_amount(self.ebit)}")
        print(f"  EBITDA         : {self._format_amount(self.ebitda)}")
        print(f"  所得税         : {self._format_amount(self.income_tax)}")
        print(f"  净利润         : {self._format_amount(self.net_profit)}")
        print(
            f"  归母净利润     : "
            f"{self._format_amount(self.net_profit_attributable)}"
        )
        print(
            f"  扣非净利润     : "
            f"{self._format_amount(self.non_recurring_net_profit)}"
        )

        print("\n每股指标")
        print(f"  EPS            : {self._format_number(self.eps)}")
        print(f"  稀释 EPS       : {self._format_number(self.diluted_eps)}")

    @staticmethod
    def _format_amount(value: Optional[float]) -> str:
        if value is None:
            return "-"

        return f"{value:,.2f}"

    @staticmethod
    def _format_number(value: Optional[float]) -> str:
        if value is None:
            return "-"

        return f"{value:.4f}"