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


class Exchange(str, Enum):
    """
    股票交易所。
    """

    # 上海证券交易所
    SSE = "SSE"

    # 深圳证券交易所
    SZSE = "SZSE"

    # 北京证券交易所
    BSE = "BSE"

    NASDAQ = "NASDAQ"

    NYSE = "NYSE"

    UNKNOWN = "UNKNOWN"
