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

    Financial 是公司财务数据的统一容器。

    包含：

        - 利润表
        - 资产负债表
        - 现金流量表
        - 财务分析指标

    Financial 本身不保存具体财务科目，
    具体数据由对应的 Model 表示。
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
        2026-06-30
    """

    report_type: Optional[str] = None
    """
    报告类型。

    例如：

        annual
        interim
        quarterly

    具体值由数据源决定。
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

    由 FinancialAnalyzer 根据财务报表计算得到。
    """

    # ==========================================================
    # Display
    # ==========================================================

    def display(self) -> None:
        """
        显示完整财务数据。

        显示内容：

            - 基础报告信息
            - 利润表
            - 资产负债表
            - 现金流量表
            - 财务分析指标

        当某一部分数据不存在时，
        显示 "-"，而不是直接跳过。
        """

        print("📊 公司财务数据")
        print("=" * 80)

        # ======================================================
        # 报告信息
        # ======================================================

        print("【报告信息】")

        print(f"  股票代码       : " f"{self.symbol}")

        print(f"  报告期         : " f"{self.report_date or '-'}")

        print(f"  报告类型       : " f"{self.report_type or '-'}")

        print(f"  财务周期       : " f"{self.period or '-'}")

        print(f"  币种           : " f"{self.currency or '-'}")

        print(f"  公告日期       : " f"{self.announcement_date or '-'}")

        print(f"  数据来源       : " f"{self.source or '-'}")

        # ======================================================
        # 利润表
        # ======================================================

        print()
        print("【利润表】")

        if self.income is not None:
            self.income.display()
        else:
            print("  -")

        # ======================================================
        # 资产负债表
        # ======================================================

        print()
        print("【资产负债表】")

        if self.balance is not None:
            self.balance.display()
        else:
            print("  -")

        # ======================================================
        # 现金流量表
        # ======================================================

        print()
        print("【现金流量表】")

        if self.cash_flow is not None:
            self.cash_flow.display()
        else:
            print("  -")

        # ======================================================
        # 财务分析指标
        # ======================================================

        print()
        print("【财务指标】")

        if self.indicators is not None:
            self.indicators.display()
        else:
            print("  -")

        print()
        print("=" * 80)
