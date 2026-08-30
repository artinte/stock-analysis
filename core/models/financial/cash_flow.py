from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CashFlowStatement:
    """
    现金流量表。

    描述公司在某一个财务报告期内现金、
    现金等价物及其流入流出情况。
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
    # 经营活动
    # ==========================================================

    operating_cash_flow: Optional[float] = None
    """
    经营活动产生的现金流量净额。
    """

    cash_flow_from_operations: Optional[float] = None
    """
    间接法经营活动产生的现金流量净额。
    """

    operating_cash_inflow: Optional[float] = None
    """
    经营活动现金流入小计。
    """

    operating_cash_outflow: Optional[float] = None
    """
    经营活动现金流出小计。
    """

    cash_received_from_sales: Optional[float] = None
    """
    销售商品、提供劳务收到的现金。
    """

    cash_paid_for_goods: Optional[float] = None
    """
    购买商品、接受劳务支付的现金。
    """

    cash_paid_to_employees: Optional[float] = None
    """
    支付给职工以及为职工支付的现金。
    """

    taxes_paid: Optional[float] = None
    """
    支付的各项税费。
    """

    tax_refund_received: Optional[float] = None
    """
    收到的税费返还。
    """

    # ==========================================================
    # 投资活动
    # ==========================================================

    investing_cash_flow: Optional[float] = None
    """
    投资活动产生的现金流量净额。
    """

    investing_cash_inflow: Optional[float] = None
    """
    投资活动现金流入小计。
    """

    investing_cash_outflow: Optional[float] = None
    """
    投资活动现金流出小计。
    """

    capital_expenditure: Optional[float] = None
    """
    购建固定资产、无形资产和其他长期资产支付的现金。
    """

    cash_received_from_investments: Optional[float] = None
    """
    收回投资收到的现金。
    """

    investment_income_received: Optional[float] = None
    """
    取得投资收益收到的现金。
    """

    # ==========================================================
    # 筹资活动
    # ==========================================================

    financing_cash_flow: Optional[float] = None
    """
    筹资活动产生的现金流量净额。
    """

    financing_cash_inflow: Optional[float] = None
    """
    筹资活动现金流入小计。
    """

    financing_cash_outflow: Optional[float] = None
    """
    筹资活动现金流出小计。
    """

    cash_received_from_borrowings: Optional[float] = None
    """
    取得借款收到的现金。
    """

    cash_paid_for_debt: Optional[float] = None
    """
    偿还债务支付的现金。
    """

    dividends_interest_paid: Optional[float] = None
    """
    分配股利、利润或偿付利息支付的现金。
    """

    cash_from_equity_investment: Optional[float] = None
    """
    吸收投资收到的现金。
    """

    # ==========================================================
    # 现金及现金等价物
    # ==========================================================

    beginning_cash_balance: Optional[float] = None
    """
    期初现金及现金等价物余额。
    """

    ending_cash_balance: Optional[float] = None
    """
    期末现金及现金等价物余额。
    """

    net_change_in_cash: Optional[float] = None
    """
    现金及现金等价物净增加额。
    """

    exchange_rate_effect: Optional[float] = None
    """
    汇率变动对现金的影响。
    """

    # ==========================================================
    # 自由现金流
    # ==========================================================

    free_cash_flow: Optional[float] = None
    """
    企业自由现金流量。
    """

    fcff: Optional[float] = None
    """
    企业自由现金流。

    后续可根据完整数据进一步计算。
    """

    fcfe: Optional[float] = None
    """
    股权自由现金流。

    后续可根据完整数据进一步计算。
    """

    # ==========================================================
    # Display
    # ==========================================================

    def display(self) -> None:
        """
        显示现金流量表。
        """

        print("📋 现金流量表")

        print("\n报告信息")
        print(f"  股票代码       : {self.symbol}")
        print(f"  报告期         : {self.report_date or '-'}")
        print(f"  报告类型       : {self.report_type or '-'}")
        print(f"  报表类型       : {self.statement_type or '-'}")
        print(f"  公告日期       : {self.announcement_date or '-'}")
        print(f"  币种           : {self.currency or '-'}")

        print("\n经营活动")
        print(f"  经营活动现金流 : " f"{self._format_amount(self.operating_cash_flow)}")
        print(
            f"  间接法经营现金流: "
            f"{self._format_amount(self.cash_flow_from_operations)}"
        )
        print(
            f"  经营活动现金流入: " f"{self._format_amount(self.operating_cash_inflow)}"
        )
        print(
            f"  经营活动现金流出: "
            f"{self._format_amount(self.operating_cash_outflow)}"
        )
        print(
            f"  销售商品收现   : "
            f"{self._format_amount(self.cash_received_from_sales)}"
        )
        print(f"  购买商品付现   : " f"{self._format_amount(self.cash_paid_for_goods)}")
        print(
            f"  支付职工现金   : " f"{self._format_amount(self.cash_paid_to_employees)}"
        )
        print(f"  支付税费       : " f"{self._format_amount(self.taxes_paid)}")
        print(f"  收到税费返还   : " f"{self._format_amount(self.tax_refund_received)}")

        print("\n投资活动")
        print(f"  投资活动现金流 : " f"{self._format_amount(self.investing_cash_flow)}")
        print(
            f"  投资活动现金流入: " f"{self._format_amount(self.investing_cash_inflow)}"
        )
        print(
            f"  投资活动现金流出: "
            f"{self._format_amount(self.investing_cash_outflow)}"
        )
        print(f"  资本开支       : " f"{self._format_amount(self.capital_expenditure)}")
        print(
            f"  收回投资       : "
            f"{self._format_amount(self.cash_received_from_investments)}"
        )
        print(
            f"  投资收益收现   : "
            f"{self._format_amount(self.investment_income_received)}"
        )

        print("\n筹资活动")
        print(f"  筹资活动现金流 : " f"{self._format_amount(self.financing_cash_flow)}")
        print(
            f"  筹资活动现金流入: " f"{self._format_amount(self.financing_cash_inflow)}"
        )
        print(
            f"  筹资活动现金流出: "
            f"{self._format_amount(self.financing_cash_outflow)}"
        )
        print(
            f"  取得借款       : "
            f"{self._format_amount(self.cash_received_from_borrowings)}"
        )
        print(f"  偿还债务       : " f"{self._format_amount(self.cash_paid_for_debt)}")
        print(
            f"  分红及利息     : "
            f"{self._format_amount(self.dividends_interest_paid)}"
        )
        print(
            f"  吸收投资       : "
            f"{self._format_amount(self.cash_from_equity_investment)}"
        )

        print("\n现金及现金等价物")
        print(
            f"  期初余额       : " f"{self._format_amount(self.beginning_cash_balance)}"
        )
        print(f"  期末余额       : " f"{self._format_amount(self.ending_cash_balance)}")
        print(f"  净增加额       : " f"{self._format_amount(self.net_change_in_cash)}")
        print(
            f"  汇率变动影响   : " f"{self._format_amount(self.exchange_rate_effect)}"
        )

        print("\n自由现金流")
        print(f"  自由现金流     : " f"{self._format_amount(self.free_cash_flow)}")
        print(f"  FCFF           : " f"{self._format_amount(self.fcff)}")
        print(f"  FCFE           : " f"{self._format_amount(self.fcfe)}")

    @staticmethod
    def _format_amount(
        value: Optional[float],
    ) -> str:

        if value is None:
            return "-"

        return f"{value:,.2f}"
