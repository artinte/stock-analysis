from __future__ import annotations

from dataclasses import dataclass

from core.models.indicators.base import IndicatorPoint


@dataclass(slots=True)
class BollingerPoint(IndicatorPoint):
    """
    Bollinger Bands（布林带）在某个时间点的计算结果。

    upper:
        上轨

    middle:
        中轨

    lower:
        下轨

    bandwidth:
        带宽
    """

    upper: float | None = None
    middle: float | None = None
    lower: float | None = None
    bandwidth: float | None = None

    def display(self) -> str:
        """
        返回适合终端显示的布林带信息。
        """
        return (
            f"BOLL "
            f"{self.symbol} "
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} | "
            f"UPPER={self.format_value(self.upper)} "
            f"MIDDLE={self.format_value(self.middle)} "
            f"LOWER={self.format_value(self.lower)} "
            f"BANDWIDTH={self.format_value(self.bandwidth)}"
        )
