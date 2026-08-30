from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .balance_sheet import BalanceSheet
from .cash_flow import CashFlowStatement
from .financial_indicators import FinancialIndicators
from .income_statement import IncomeStatement


@dataclass(slots=True)
class Financial:
    """
    公司财务数据。

    Financial 是一个财务报告的统一容器，
    本身不直接保存大量财务字段。

    具体数据分别由：

        BalanceSheet
        IncomeStatement
        CashFlowStatement
        FinancialIndicators

    表示。
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    symbol: str

    report_date: Optional[str] = None
    """
    财务报告期。

    例如：

        2025-12-31
        2026-03-31
    """

    report_type: Optional[str] = None
    """
    报告类型。

    例如：

        annual
        quarterly
        interim
    """

    period: Optional[str] = None
    """
    财务周期。

    例如：

        Q1
        Q2
        Q3
        FY
    """

    currency: Optional[str] = None
    """
    币种。

    例如：

        CNY
        USD
    """

    announcement_date: Optional[str] = None
    """
    公告日期。
    """

    source: Optional[str] = None
    """
    数据来源。

    例如：

        yinhe
        akshare
        tushare
    """

    # ==========================================================
    # 财务报表
    # ==========================================================

    income: Optional[IncomeStatement] = None
    """
    利润表。
    """

    balance: Optional[BalanceSheet] = None
    """
    资产负债表。
    """

    cash_flow: Optional[CashFlowStatement] = None
    """
    现金流量表。
    """

    # ==========================================================
    # 财务指标
    # ==========================================================

    indicators: Optional[FinancialIndicators] = None
    """
    财务分析指标。
    """

    def display(self) -> None:
        print("财务数据")

        print(f"股票代码       : {self.symbol}")
        print(f"报告日期       : {self.report_date or '-'}")
        print(f"报告类型       : {self.report_type or '-'}")
        print(f"报告周期       : {self.period or '-'}")
        print(f"币种           : {self.currency or '-'}")
        print(f"公告日期       : {self.announcement_date or '-'}")
        print(f"数据来源       : {self.source or '-'}")

        if self.income:
            print()
            self.income.display()

        if self.balance:
            print()
            self.balance.display()

        if self.cash_flow:
            print()
            self.cash_flow.display()

        if self.indicators:
            print()
            self.indicators.display()
