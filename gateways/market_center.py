from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from models.index import Index


@dataclass(slots=True)
class MarketCenter:
    """
    股票市场数据中心。

    用于保存整个股票市场的整体数据。

    数据流：

        DataSource
            ↓
        Gateway
            ↓
        Index / MarketCenter
            ↓
        MarketCenter
            ↓
        市场分析 / 策略 / AI分析

    主要包含：

        - 主要市场指数
        - 市场涨跌统计
        - 市场成交情况
        - 市场状态
    """

    # ==========================================================
    # 主要指数
    # ==========================================================

    indices: list[Index] = field(default_factory=list)
    """
    市场主要指数。

    例如：

        上证指数
        深证成指
        创业板指
        科创50
        沪深300
        中证500
        中证A500
    """

    # ==========================================================
    # 市场涨跌
    # ==========================================================

    advancing_count: Optional[int] = None
    """
    上涨股票数量。
    """

    declining_count: Optional[int] = None
    """
    下跌股票数量。
    """

    unchanged_count: Optional[int] = None
    """
    平盘股票数量。
    """

    limit_up_count: Optional[int] = None
    """
    涨停股票数量。
    """

    limit_down_count: Optional[int] = None
    """
    跌停股票数量。
    """

    # ==========================================================
    # 市场成交
    # ==========================================================

    total_amount: Optional[float] = None
    """
    全市场成交额。

    单位：

        元
    """

    # ==========================================================
    # 市场状态
    # ==========================================================

    trading_date: Optional[str] = None
    """
    交易日期。
    """

    status: Optional[str] = None
    """
    市场状态。

    例如：

        trading
        closed
        holiday
    """

    source: Optional[str] = None
    """
    数据来源。
    """

    # ==========================================================
    # 指数操作
    # ==========================================================

    def add_index(self, index: Index) -> None:
        """添加市场指数。"""
        self.indices.append(index)

    def get_index(self, symbol: str) -> Optional[Index]:
        """根据指数代码获取指数。"""
        for index in self.indices:
            if index.symbol == symbol:
                return index

        return None

    # ==========================================================
    # 展示
    # ==========================================================

    def display(self) -> None:
        """打印市场数据。"""

        print(f"交易日期：{self.trading_date or '-'}")
        print(f"市场状态：{self.status or '-'}")
        print(f"数据来源：{self.source or '-'}")

        print()
        print("主要指数：")

        for index in self.indices:
            change_percent = (
                f"{index.change_percent:.2f}%"
                if index.change_percent is not None
                else "-"
            )

            price = f"{index.price:.2f}" if index.price is not None else "-"

            print(
                f"  {index.symbol}  "
                f"{index.name or '-'}  "
                f"{price}  "
                f"{change_percent}"
            )

        print()
        print(
            f"上涨：{self.advancing_count if self.advancing_count is not None else '-'}"
        )
        print(
            f"下跌：{self.declining_count if self.declining_count is not None else '-'}"
        )
        print(
            f"平盘：{self.unchanged_count if self.unchanged_count is not None else '-'}"
        )
        print(
            f"涨停：{self.limit_up_count if self.limit_up_count is not None else '-'}"
        )
        print(
            f"跌停：{self.limit_down_count if self.limit_down_count is not None else '-'}"
        )

        print(
            f"市场成交额："
            f"{self.total_amount if self.total_amount is not None else '-'}"
        )
