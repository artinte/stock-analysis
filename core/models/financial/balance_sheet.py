from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class BalanceSheet:
    """
    资产负债表。

    描述公司在某一个财务报告期末的资产、
    负债和所有者权益状况。
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    symbol: str

    report_date: Optional[str] = None
    """报告期。"""

    report_type: Optional[str] = None
    """报告期类型。"""

    statement_type: Optional[str] = None
    """报表类型。"""

    announcement_date: Optional[str] = None
    """公告日期。"""

    currency: Optional[str] = None
    """币种。"""

    # ==========================================================
    # 资产
    # ==========================================================

    total_assets: Optional[float] = None
    """资产总额。"""

    current_assets: Optional[float] = None
    """流动资产合计。"""

    non_current_assets: Optional[float] = None
    """非流动资产合计。"""

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

    construction_in_progress: Optional[float] = None
    """在建工程。"""

    intangible_assets: Optional[float] = None
    """无形资产。"""

    goodwill: Optional[float] = None
    """商誉。"""

    long_term_equity_investment: Optional[float] = None
    """长期股权投资。"""

    investment_real_estate: Optional[float] = None
    """投资性房地产。"""

    right_of_use_assets: Optional[float] = None
    """使用权资产。"""

    # ==========================================================
    # 负债
    # ==========================================================

    total_liabilities: Optional[float] = None
    """负债总额。"""

    current_liabilities: Optional[float] = None
    """流动负债合计。"""

    non_current_liabilities: Optional[float] = None
    """非流动负债合计。"""

    short_term_debt: Optional[float] = None
    """短期借款。"""

    long_term_debt: Optional[float] = None
    """长期借款。"""

    accounts_payable: Optional[float] = None
    """应付账款。"""

    notes_payable: Optional[float] = None
    """应付票据。"""

    bonds_payable: Optional[float] = None
    """应付债券。"""

    lease_liability: Optional[float] = None
    """租赁负债。"""

    tax_payable: Optional[float] = None
    """应交税费。"""

    dividends_payable: Optional[float] = None
    """应付股利。"""

    # ==========================================================
    # 所有者权益
    # ==========================================================

    total_equity: Optional[float] = None
    """所有者权益合计。"""

    shareholders_equity: Optional[float] = None
    """归属于股东的权益，不含少数股东。"""

    minority_interest: Optional[float] = None
    """少数股东权益。"""

    share_capital: Optional[float] = None
    """股本。"""

    capital_reserve: Optional[float] = None
    """资本公积。"""

    surplus_reserve: Optional[float] = None
    """盈余公积。"""

    undistributed_profit: Optional[float] = None
    """未分配利润。"""

    treasury_stock: Optional[float] = None
    """库存股。"""

    # ==========================================================
    # Display
    # ==========================================================

    def display(self) -> None:
        """
        显示资产负债表。
        """

        print("📋 资产负债表")

        print("\n报告信息")
        print(f"  股票代码       : {self.symbol}")
        print(f"  报告期         : {self.report_date or '-'}")
        print(f"  报告类型       : {self.report_type or '-'}")
        print(f"  报表类型       : {self.statement_type or '-'}")
        print(f"  公告日期       : {self.announcement_date or '-'}")
        print(f"  币种           : {self.currency or '-'}")

        print("\n资产")
        print(f"  资产总额       : {self._format_amount(self.total_assets)}")
        print(f"  流动资产       : {self._format_amount(self.current_assets)}")
        print(f"  非流动资产     : {self._format_amount(self.non_current_assets)}")
        print(f"  货币资金       : {self._format_amount(self.cash)}")
        print(f"  应收账款       : {self._format_amount(self.accounts_receivable)}")
        print(f"  存货           : {self._format_amount(self.inventory)}")
        print(f"  固定资产       : {self._format_amount(self.fixed_assets)}")
        print(
            f"  在建工程       : "
            f"{self._format_amount(self.construction_in_progress)}"
        )
        print(f"  无形资产       : " f"{self._format_amount(self.intangible_assets)}")
        print(f"  商誉           : {self._format_amount(self.goodwill)}")
        print(
            f"  长期股权投资   : "
            f"{self._format_amount(self.long_term_equity_investment)}"
        )
        print(
            f"  投资性房地产   : " f"{self._format_amount(self.investment_real_estate)}"
        )
        print(f"  使用权资产     : " f"{self._format_amount(self.right_of_use_assets)}")

        print("\n负债")
        print(f"  负债总额       : " f"{self._format_amount(self.total_liabilities)}")
        print(f"  流动负债       : " f"{self._format_amount(self.current_liabilities)}")
        print(
            f"  非流动负债     : "
            f"{self._format_amount(self.non_current_liabilities)}"
        )
        print(f"  短期借款       : " f"{self._format_amount(self.short_term_debt)}")
        print(f"  长期借款       : " f"{self._format_amount(self.long_term_debt)}")
        print(f"  应付账款       : " f"{self._format_amount(self.accounts_payable)}")
        print(f"  应付票据       : " f"{self._format_amount(self.notes_payable)}")
        print(f"  应付债券       : " f"{self._format_amount(self.bonds_payable)}")
        print(f"  租赁负债       : " f"{self._format_amount(self.lease_liability)}")
        print(f"  应交税费       : " f"{self._format_amount(self.tax_payable)}")
        print(f"  应付股利       : " f"{self._format_amount(self.dividends_payable)}")

        print("\n所有者权益")
        print(f"  所有者权益     : " f"{self._format_amount(self.total_equity)}")
        print(f"  股东权益       : " f"{self._format_amount(self.shareholders_equity)}")
        print(f"  少数股东权益   : " f"{self._format_amount(self.minority_interest)}")
        print(f"  股本           : " f"{self._format_amount(self.share_capital)}")
        print(f"  资本公积       : " f"{self._format_amount(self.capital_reserve)}")
        print(f"  盈余公积       : " f"{self._format_amount(self.surplus_reserve)}")
        print(
            f"  未分配利润     : " f"{self._format_amount(self.undistributed_profit)}"
        )
        print(f"  库存股         : " f"{self._format_amount(self.treasury_stock)}")

    @staticmethod
    def _format_amount(
        value: Optional[float],
    ) -> str:
        if value is None:
            return "-"

        return f"{value:,.2f}"
