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
    # 报告信息
    # ==========================================================

    symbol: str

    report_date: Optional[str] = None
    """报告期。"""

    report_type: Optional[str] = None
    """报告期类型代码。"""

    statement_type: Optional[str] = None
    """报表类型代码。"""

    announcement_date: Optional[str] = None
    """公告日期。"""

    currency: Optional[str] = None
    """币种。"""

    # ==========================================================
    # 收入
    # ==========================================================

    revenue: Optional[float] = None
    """营业收入。"""

    total_operating_income: Optional[float] = None
    """营业总收入。"""

    # ==========================================================
    # 成本费用
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

    business_tax_and_surcharge: Optional[float] = None
    """营业税金及附加。"""

    asset_impairment_loss: Optional[float] = None
    """资产减值损失。"""

    credit_impairment_loss: Optional[float] = None
    """信用减值损失。"""

    # ==========================================================
    # 收益项目
    # ==========================================================

    investment_income: Optional[float] = None
    """投资收益。"""

    fair_value_change_income: Optional[float] = None
    """公允价值变动收益。"""

    exchange_income: Optional[float] = None
    """汇兑收益。"""

    other_income: Optional[float] = None
    """其他收益。"""

    # ==========================================================
    # 利润
    # ==========================================================

    gross_profit: Optional[float] = None
    """毛利润。"""

    operating_profit: Optional[float] = None
    """营业利润。"""

    total_profit: Optional[float] = None
    """利润总额。"""

    income_tax: Optional[float] = None
    """所得税费用。"""

    net_profit: Optional[float] = None
    """净利润。"""

    net_profit_attributable: Optional[float] = None
    """归属于母公司股东的净利润。"""

    non_recurring_net_profit: Optional[float] = None
    """扣除非经常性损益后的净利润。"""

    # ==========================================================
    # 营业外收支
    # ==========================================================

    non_operating_income: Optional[float] = None
    """营业外收入。"""

    non_operating_expense: Optional[float] = None
    """营业外支出。"""

    # ==========================================================
    # 其他综合收益
    # ==========================================================

    other_comprehensive_income: Optional[float] = None
    """其他综合收益。"""

    # ==========================================================
    # EBIT / EBITDA
    # ==========================================================

    ebit: Optional[float] = None
    """息税前利润。"""

    ebitda: Optional[float] = None
    """息税折旧摊销前利润。"""

    # ==========================================================
    # 每股收益
    # ==========================================================

    eps: Optional[float] = None
    """基本每股收益。"""

    diluted_eps: Optional[float] = None
    """稀释每股收益。"""

    # ==========================================================
    # Display
    # ==========================================================

    def display(self) -> None:
        """
        显示利润表。
        """

        print("📋 利润表")

        print("\n报告信息")
        print(f"  股票代码       : {self.symbol}")
        print(f"  报告期         : {self.report_date or '-'}")
        print(f"  报告类型       : {self.report_type or '-'}")
        print(f"  报表类型       : {self.statement_type or '-'}")
        print(f"  公告日期       : {self.announcement_date or '-'}")
        print(f"  币种           : {self.currency or '-'}")

        print("\n营业收入")
        print(f"  营业收入       : {self._format_amount(self.revenue)}")
        print(
            f"  营业总收入     : " f"{self._format_amount(self.total_operating_income)}"
        )

        print("\n成本费用")
        print(f"  营业成本       : {self._format_amount(self.operating_cost)}")
        print(
            f"  营业总成本     : " f"{self._format_amount(self.total_operating_cost)}"
        )
        print(f"  销售费用       : " f"{self._format_amount(self.selling_expense)}")
        print(
            f"  管理费用       : " f"{self._format_amount(self.administrative_expense)}"
        )
        print(f"  财务费用       : " f"{self._format_amount(self.financial_expense)}")
        print(f"  研发费用       : " f"{self._format_amount(self.rd_expense)}")
        print(
            f"  营业税金及附加 : "
            f"{self._format_amount(self.business_tax_and_surcharge)}"
        )
        print(
            f"  资产减值损失   : " f"{self._format_amount(self.asset_impairment_loss)}"
        )
        print(
            f"  信用减值损失   : " f"{self._format_amount(self.credit_impairment_loss)}"
        )

        print("\n其他收益")
        print(f"  投资收益       : " f"{self._format_amount(self.investment_income)}")
        print(
            f"  公允价值变动收益: "
            f"{self._format_amount(self.fair_value_change_income)}"
        )
        print(f"  汇兑收益       : " f"{self._format_amount(self.exchange_income)}")
        print(f"  其他收益       : " f"{self._format_amount(self.other_income)}")

        print("\n利润")
        print(f"  毛利润         : " f"{self._format_amount(self.gross_profit)}")
        print(f"  营业利润       : " f"{self._format_amount(self.operating_profit)}")
        print(f"  利润总额       : " f"{self._format_amount(self.total_profit)}")
        print(f"  所得税         : " f"{self._format_amount(self.income_tax)}")
        print(f"  净利润         : " f"{self._format_amount(self.net_profit)}")
        print(
            f"  归母净利润     : "
            f"{self._format_amount(self.net_profit_attributable)}"
        )
        print(
            f"  扣非净利润     : "
            f"{self._format_amount(self.non_recurring_net_profit)}"
        )

        print("\n营业外收支")
        print(
            f"  营业外收入     : " f"{self._format_amount(self.non_operating_income)}"
        )
        print(
            f"  营业外支出     : " f"{self._format_amount(self.non_operating_expense)}"
        )

        print("\n其他综合收益")
        print(
            f"  其他综合收益   : "
            f"{self._format_amount(self.other_comprehensive_income)}"
        )

        print("\n每股指标")
        print(f"  基本 EPS       : " f"{self._format_number(self.eps)}")
        print(f"  稀释 EPS       : " f"{self._format_number(self.diluted_eps)}")

        print("\n盈利能力")
        print(f"  EBIT           : " f"{self._format_amount(self.ebit)}")
        print(f"  EBITDA         : " f"{self._format_amount(self.ebitda)}")

    @staticmethod
    def _format_amount(
        value: Optional[float],
    ) -> str:
        if value is None:
            return "-"

        return f"{value:,.2f}"

    @staticmethod
    def _format_number(
        value: Optional[float],
    ) -> str:
        if value is None:
            return "-"

        return f"{value:.4f}"
