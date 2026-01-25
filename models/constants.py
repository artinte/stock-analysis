from enum import Enum


class Interval(Enum):
    """K线周期枚举"""

    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "60m"
    DAY_1 = "1d"
    WEEK_1 = "1w"

    def __str__(self):
        return self.value
