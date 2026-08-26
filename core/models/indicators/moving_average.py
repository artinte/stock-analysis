from __future__ import annotations

from dataclasses import dataclass

from core.models.indicators.base import IndicatorPoint


@dataclass(slots=True)
class MovingAveragePoint(IndicatorPoint):
    """
    移动平均线在某个时间点的计算结果。

    period:
        移动平均周期，例如：

            MA5
            MA10
            MA20
            MA60
            MA120
            MA250

    value:
        移动平均值。
    """

    period: int = 20
    value: float | None = None

    def display(self) -> str:
        """
        返回适合终端显示的移动平均线信息。
        """
        return (
            f"MA{self.period} "
            f"{self.symbol} "
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} | "
            f"VALUE={self.format_value(self.value)}"
        )
