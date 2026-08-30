from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class BalanceSheet:
    """
    资产负债表。

    描述公司在某一个财务报告期末的资产、
    负债和所有者权益状况。

    数据来源可以是：

        银河证券
        AkShare
        Tushare
        Wind
        东方财富
        同花顺
    """

    # ==========================================================
    # 资产
    # ==========================================================

    total_assets: Optional[float] = None
    """资产总额。"""

    cash: Optional[float] = None
    """货币资金。"""

    cash_equivalent: Optional[float] = None
    """现金及现金等价物。"""

    accounts_receivable: Optional[float] = None
    """应收账款。"""

    inventory: Optional[float] = None
    """存货。"""

    fixed_assets: Optional[float] = None
    """固定资产。"""

    goodwill: Optional[float] = None
    """商誉。"""

    # ==========================================================
    # 负债
    # ==========================================================

    total_liabilities: Optional[float] = None
    """负债总额。"""

    current_liabilities: Optional[float] = None
    """流动负债。"""

    non_current_liabilities: Optional[float] = None
    """非流动负债。"""

    short_term_debt: Optional[float] = None
    """短期借款。"""

    long_term_debt: Optional[float] = None
    """长期借款。"""

    accounts_payable: Optional[float] = None
    """应付账款。"""

    # ==========================================================
    # 所有者权益
    # ==========================================================

    total_equity: Optional[float] = None
    """所有者权益合计。"""

    shareholders_equity: Optional[float] = None
    """归属于股东的权益。"""

    minority_interest: Optional[float] = None
    """少数股东权益。"""

    def display(self) -> None:
        """
        显示资产负债表。
        """

        print("资产负债表")

        print("\n资产")
        print(f"  资产总额       : {self._format_amount(self.total_assets)}")
        print(f"  货币资金       : {self._format_amount(self.cash)}")
        print(f"  现金及等价物   : {self._format_amount(self.cash_equivalent)}")
        print(f"  应收账款       : {self._format_amount(self.accounts_receivable)}")
        print(f"  存货           : {self._format_amount(self.inventory)}")
        print(f"  固定资产       : {self._format_amount(self.fixed_assets)}")
        print(f"  商誉           : {self._format_amount(self.goodwill)}")

        print("\n负债")
        print(f"  负债总额       : {self._format_amount(self.total_liabilities)}")
        print(f"  流动负债       : {self._format_amount(self.current_liabilities)}")
        print(f"  非流动负债     : {self._format_amount(self.non_current_liabilities)}")
        print(f"  短期借款       : {self._format_amount(self.short_term_debt)}")
        print(f"  长期借款       : {self._format_amount(self.long_term_debt)}")
        print(f"  应付账款       : {self._format_amount(self.accounts_payable)}")

        print("\n所有者权益")
        print(f"  所有者权益     : {self._format_amount(self.total_equity)}")
        print(f"  股东权益       : {self._format_amount(self.shareholders_equity)}")
        print(f"  少数股东权益   : {self._format_amount(self.minority_interest)}")

    @staticmethod
    def _format_amount(value: Optional[float]) -> str:
        if value is None:
            return "-"

        return f"{value:,.2f}"
