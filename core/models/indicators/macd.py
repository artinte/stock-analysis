from __future__ import annotations

from dataclasses import dataclass

from core.models.indicators.base import IndicatorPoint


@dataclass(slots=True)
class MACDPoint(IndicatorPoint):
    """
    MACD 指标在某个时间点的计算结果。

    DIF:
        快速 EMA - 慢速 EMA

    DEA:
        DIF 的 EMA

    HIST:
        DIF - DEA
    """

    dif: float | None = None
    dea: float | None = None
    hist: float | None = None

    def display(self) -> str:
        """
        返回适合终端显示的 MACD 信息。
        """
        return (
            f"MACD "
            f"{self.symbol} "
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} | "
            f"DIF={self.format_value(self.dif)} "
            f"DEA={self.format_value(self.dea)} "
            f"HIST={self.format_value(self.hist)}"
        )
