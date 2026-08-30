from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CashFlowStatement:
    """
    现金流量表。

    描述公司在某一个财务报告期内现金及现金等价物
    的流入和流出情况。
    """

    # ==========================================================
    # 经营活动
    # ==========================================================

    operating_cash_flow: Optional[float] = None
    """
    经营活动产生的现金流量净额。
    """

    cash_flow_from_operations: Optional[float] = None
    """
    经营活动现金流。
    """

    # ==========================================================
    # 投资活动
    # ==========================================================

    investing_cash_flow: Optional[float] = None
    """
    投资活动产生的现金流量净额。
    """

    # ==========================================================
    # 筹资活动
    # ==========================================================

    financing_cash_flow: Optional[float] = None
    """
    筹资活动产生的现金流量净额。
    """

    # ==========================================================
    # 自由现金流
    # ==========================================================

    free_cash_flow: Optional[float] = None
    """
    自由现金流。

    通常：

        FCF = Operating Cash Flow - Capital Expenditure
    """

    fcff: Optional[float] = None
    """
    企业自由现金流。
    """

    fcfe: Optional[float] = None
    """
    股权自由现金流。
    """

    def display(self) -> None:
        """
        显示现金流量表。
        """

        print("现金流量表")

        print("\n现金流")
        print(f"  经营活动现金流 : " f"{self._format_amount(self.operating_cash_flow)}")
        print(
            f"  经营现金流     : "
            f"{self._format_amount(self.cash_flow_from_operations)}"
        )
        print(f"  投资活动现金流 : " f"{self._format_amount(self.investing_cash_flow)}")
        print(f"  筹资活动现金流 : " f"{self._format_amount(self.financing_cash_flow)}")

        print("\n自由现金流")
        print(f"  自由现金流     : {self._format_amount(self.free_cash_flow)}")
        print(f"  FCFF           : {self._format_amount(self.fcff)}")
        print(f"  FCFE           : {self._format_amount(self.fcfe)}")

    @staticmethod
    def _format_amount(value: Optional[float]) -> str:
        if value is None:
            return "-"

        return f"{value:,.2f}"
