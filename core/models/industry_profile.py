from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from common.constants import IndustryLevel
from core.models.industry import Industry


@dataclass(slots=True)
class IndustryProfile:
    """
    行业画像。

    描述某一个行业层级的整体情况。

    例如：

        Industry：

            一级：食品饮料
            二级：饮料
            三级：白酒

        IndustryProfile：

            level = IndustryLevel.LEVEL_3

        表示当前 Profile 统计的是“白酒”行业。

    主要用于分析：

        - 行业有多少只股票
        - 行业整体涨跌
        - 行业成交情况
        - 行业估值是否昂贵
        - 行业盈利能力
        - 行业基本面情况
    """

    # ==========================================================
    # 行业
    # ==========================================================

    industry: Industry

    # 当前 Profile 对应的行业层级
    level: IndustryLevel

    # ==========================================================
    # 行业成分股
    # ==========================================================

    stock_count: Optional[int] = None

    # ==========================================================
    # 行业行情
    # ==========================================================

    change_percent: Optional[float] = None

    volume: Optional[float] = None

    amount: Optional[float] = None

    # ==========================================================
    # 行业涨跌
    # ==========================================================

    advancing_count: Optional[int] = None

    declining_count: Optional[int] = None

    unchanged_count: Optional[int] = None

    # ==========================================================
    # 行业估值
    # ==========================================================

    pe: Optional[float] = None

    pe_ttm: Optional[float] = None

    pb: Optional[float] = None

    # ==========================================================
    # 行业基本面
    # ==========================================================

    revenue_growth: Optional[float] = None

    profit_growth: Optional[float] = None

    roe: Optional[float] = None

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    def display(self) -> None:
        """打印行业画像。"""

        print("行业画像")

        # ------------------------------------------------------
        # 行业信息
        # ------------------------------------------------------

        print(f"行业：{self.industry.name or '-'}")
        print(f"行业代码：{self.industry.code or '-'}")

        print(
            f"分类标准："
            f"{self.industry.standard.value if self.industry.standard is not None else '-'}"
        )

        print(f"统计层级：第 {self.level.value} 级")

        # ------------------------------------------------------
        # 行情
        # ------------------------------------------------------

        print()
        print("行业行情")

        print(
            f"成分股：" f"{self.stock_count if self.stock_count is not None else '-'}"
        )

        print(
            f"涨跌幅：" f"{self.change_percent:.2f}%"
            if self.change_percent is not None
            else "涨跌幅：-"
        )

        print(f"成交量：" f"{self.volume if self.volume is not None else '-'}")

        print(f"成交额：" f"{self.amount if self.amount is not None else '-'}")

        # ------------------------------------------------------
        # 涨跌
        # ------------------------------------------------------

        print()
        print("行业涨跌")

        print(
            f"上涨：{self.advancing_count if self.advancing_count is not None else '-'}"
        )
        print(
            f"下跌：{self.declining_count if self.declining_count is not None else '-'}"
        )
        print(
            f"平盘：{self.unchanged_count if self.unchanged_count is not None else '-'}"
        )

        # ------------------------------------------------------
        # 估值
        # ------------------------------------------------------

        print()
        print("行业估值")

        print(f"PE：{self.pe if self.pe is not None else '-'}")
        print(f"PE-TTM：{self.pe_ttm if self.pe_ttm is not None else '-'}")
        print(f"PB：{self.pb if self.pb is not None else '-'}")

        # ------------------------------------------------------
        # 基本面
        # ------------------------------------------------------

        print()
        print("行业基本面")

        print(
            f"营收增长：" f"{self.revenue_growth:.2f}%"
            if self.revenue_growth is not None
            else "营收增长：-"
        )

        print(
            f"利润增长：" f"{self.profit_growth:.2f}%"
            if self.profit_growth is not None
            else "利润增长：-"
        )

        print(f"ROE：" f"{self.roe:.2f}%" if self.roe is not None else "ROE：-")

        # ------------------------------------------------------
        # 数据来源
        # ------------------------------------------------------

        print()
        print(f"数据来源：{self.source or '-'}")
