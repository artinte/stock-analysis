from enum import Enum


class Interval(str, Enum):
    """
    标准 K 线周期。
    """

    MINUTE_1 = "1m"

    MINUTE_5 = "5m"

    MINUTE_15 = "15m"

    MINUTE_30 = "30m"

    MINUTE_60 = "60m"

    DAY_1 = "1d"

    WEEK_1 = "1w"

    MONTH_1 = "1M"


class PEType(str, Enum):
    """
    市盈率类型。
    """

    STATIC = "static"

    DYNAMIC = "dynamic"

    TTM = "ttm"


SHARES_PER_10K = 10_000
SHARES_PER_100M = 100_000_000

