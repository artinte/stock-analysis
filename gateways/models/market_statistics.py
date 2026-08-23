from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class MarketStatistics:
    """
    市场统计信息。

    表示某一个市场范围的统计数据。

    例如：

        全市场
        主板
        创业板
        科创板
        北交所
    """

    # ==========================================================
    # 市场
    # ==========================================================

    market: str

    trading_date: Optional[str] = None

    # ==========================================================
    # 股票数量
    # ==========================================================

    total_count: Optional[int] = None

    advancing_count: Optional[int] = None

    declining_count: Optional[int] = None

    unchanged_count: Optional[int] = None

    # ==========================================================
    # 涨跌停
    # ==========================================================

    limit_up_count: Optional[int] = None

    limit_down_count: Optional[int] = None

    # ==========================================================
    # 成交
    # ==========================================================

    volume: Optional[float] = None

    amount: Optional[float] = None

    # ==========================================================
    # 市场强弱
    # ==========================================================

    advance_decline_ratio: Optional[float] = None

    limit_up_down_ratio: Optional[float] = None

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    def display(self) -> None:
        """打印市场统计信息。"""

        print(f"市场：{self.market}")
        print(f"交易日期：{self.trading_date or '-'}")

        print(f"股票总数：{self.total_count if self.total_count is not None else '-'}")
        print(
            f"上涨："
            f"{self.advancing_count if self.advancing_count is not None else '-'}"
        )
        print(
            f"下跌："
            f"{self.declining_count if self.declining_count is not None else '-'}"
        )
        print(
            f"平盘："
            f"{self.unchanged_count if self.unchanged_count is not None else '-'}"
        )

        print(
            f"涨停："
            f"{self.limit_up_count if self.limit_up_count is not None else '-'}"
        )
        print(
            f"跌停："
            f"{self.limit_down_count if self.limit_down_count is not None else '-'}"
        )

        print(f"成交量：" f"{self.volume if self.volume is not None else '-'}")
        print(f"成交额：" f"{self.amount if self.amount is not None else '-'}")

        print(
            f"涨跌比："
            f"{self.advance_decline_ratio if self.advance_decline_ratio is not None else '-'}"
        )
        print(
            f"涨跌停比："
            f"{self.limit_up_down_ratio if self.limit_up_down_ratio is not None else '-'}"
        )

        print(f"数据来源：{self.source or '-'}")
