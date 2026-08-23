from enum import Enum

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
