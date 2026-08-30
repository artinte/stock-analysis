from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.models.valuation.valuation_metrics import ValuationMetrics


@dataclass(slots=True)
class Valuation:
    """
    股票估值数据。

    Valuation 保存：

        1. 估值基础数据
        2. 估值计算结果
        3. 数据来源及时间信息

    其中：

        基础数据
            ↓
        ValuationAnalyzer
            ↓
        ValuationMetrics
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    symbol: str

    timestamp: Optional[datetime] = None

    report_date: Optional[str] = None

    # ==========================================================
    # 估值基础数据
    #
    # 这些数据由 Gateway 获取，
    # 不属于估值计算结果。
    # ==========================================================

    price: Optional[float] = None

    total_shares: Optional[float] = None

    circulating_shares: Optional[float] = None

    # ==========================================================
    # 盈利数据
    # ==========================================================

    net_profit: Optional[float] = None

    net_profit_ttm: Optional[float] = None

    net_profit_forecast: Optional[float] = None

    revenue: Optional[float] = None

    revenue_ttm: Optional[float] = None

    # ==========================================================
    # 净资产
    # ==========================================================

    total_equity: Optional[float] = None

    book_value_per_share: Optional[float] = None

    # ==========================================================
    # 企业价值相关基础数据
    # ==========================================================

    cash: Optional[float] = None

    debt: Optional[float] = None

    ebitda: Optional[float] = None

    # ==========================================================
    # 股东回报
    # ==========================================================

    dividend: Optional[float] = None

    # ==========================================================
    # 计算结果
    # ==========================================================

    metrics: Optional[ValuationMetrics] = None

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    data_type: Optional[str] = None

    # ==========================================================
    # Display
    # ==========================================================

    def display(self) -> None:
        """
        显示股票估值数据。
        """

        def fmt(value: object) -> str:
            if value is None:
                return "-"

            if isinstance(value, str):
                value = value.strip()

                if not value:
                    return "-"

            return str(value)

        def fmt_datetime(
            value: Optional[datetime],
        ) -> str:
            if value is None:
                return "-"

            return value.strftime("%Y-%m-%d %H:%M:%S")

        def fmt_number(
            value: Optional[float],
        ) -> str:
            if value is None:
                return "-"

            return f"{value:,.2f}"

        def fmt_shares(
            value: Optional[float],
        ) -> str:
            if value is None:
                return "-"

            if value >= 100_000_000:
                return f"{value / 100_000_000:.2f} 亿股"

            if value >= 10_000:
                return f"{value / 10_000:.2f} 万股"

            return f"{value:,.0f} 股"

        print("📊 股票估值")
        print("=" * 60)

        # ======================================================
        # 基础信息
        # ======================================================

        print(f"股票代码: {fmt(self.symbol)}")
        print(f"时间: {fmt_datetime(self.timestamp)}")
        print(f"报告期: {fmt(self.report_date)}")
        print(f"数据来源: {fmt(self.source)}")
        print(f"数据类型: {fmt(self.data_type)}")

        # ======================================================
        # 基础数据
        # ======================================================

        print()
        print("【估值基础数据】")

        print(f"当前价格: {fmt_number(self.price)}")

        print(f"总股本: " f"{fmt_shares(self.total_shares)}")

        print(f"流通股本: " f"{fmt_shares(self.circulating_shares)}")

        print(f"净利润: " f"{fmt_number(self.net_profit)}")

        print(f"TTM 净利润: " f"{fmt_number(self.net_profit_ttm)}")

        print(f"预测净利润: " f"{fmt_number(self.net_profit_forecast)}")

        print(f"营业收入: " f"{fmt_number(self.revenue)}")

        print(f"TTM 营业收入: " f"{fmt_number(self.revenue_ttm)}")

        print(f"净资产: " f"{fmt_number(self.total_equity)}")

        print(f"每股净资产: " f"{fmt_number(self.book_value_per_share)}")

        print(f"现金: " f"{fmt_number(self.cash)}")

        print(f"债务: " f"{fmt_number(self.debt)}")

        print(f"EBITDA: " f"{fmt_number(self.ebitda)}")

        print(f"股息: " f"{fmt_number(self.dividend)}")

        # ======================================================
        # 计算指标
        # ======================================================

        print()

        if self.metrics is None:
            print("【估值指标】")
            print("-")
        else:
            self.metrics.display()
