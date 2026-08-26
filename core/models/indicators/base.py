from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class IndicatorPoint:
    """
    技术指标时间点数据基类。

    所有技术指标都对应某一个证券、
    某一个时间点，因此统一包含：

        symbol
        timestamp

    具体指标由子类实现。
    """

    symbol: str
    timestamp: datetime

    @staticmethod
    def format_value(
        value: float | None,
        digits: int = 4,
    ) -> str:
        """
        格式化指标数值。

        Args:
            value: 指标值。
            digits: 小数位数。

        Returns:
            格式化后的字符串。
        """
        if value is None:
            return "-"

        return f"{value:.{digits}f}"

    def display(self) -> str:
        """
        返回指标的显示字符串。

        子类应该覆盖该方法。
        """
        return (
            f"{self.__class__.__name__}("
            f"symbol={self.symbol}, "
            f"timestamp={self.timestamp}"
            f")"
        )
