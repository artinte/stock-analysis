from __future__ import annotations

from dataclasses import dataclass

from core.models.indicators.base import IndicatorPoint


@dataclass(slots=True)
class RSIPoint(IndicatorPoint):
    """
    RSI 指标在某个时间点的计算结果。

    RSI:
        Relative Strength Index
        相对强弱指标
    """

    rsi: float | None = None

    def display(self) -> str:
        """
        返回适合终端显示的 RSI 信息。
        """
        return (
            f"RSI "
            f"{self.symbol} "
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} | "
            f"RSI={self.format_value(self.rsi, 2)}"
        )
