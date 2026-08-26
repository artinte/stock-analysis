from __future__ import annotations
from dataclasses import dataclass
from core.models.indicators.base import IndicatorPoint


@dataclass(slots=True)
class WilliamsRPoint(IndicatorPoint):
    """
    Williams %R 指标在某个时间点的计算结果。

    Williams %R 通常取值范围：

        [-100, 0]
    """

    value: float | None = None

    def display(self) -> str:
        """
        返回适合终端显示的 Williams %R 信息。
        """
        return (
            f"Williams %R "
            f"{self.symbol} "
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} | "
            f"VALUE={self.format_value(self.value, 2)}"
        )
