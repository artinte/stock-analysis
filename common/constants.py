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


TEN_THOUSAND = 10_000
HUNDRED_MILLION = 100_000_000


class IndexSymbol(str, Enum):
    """
    A 股主要市场指数。

    用法：
        # 获取完整 Symbol
        IndexSymbol.SSE.value
        # "000001.SH"

        # 获取指数名称
        IndexSymbol.SSE.display_name
        # "上证指数"

        # 获取不带市场后缀的代码
        IndexSymbol.SSE.code
        # "000001"

        # 获取交易所
        IndexSymbol.SSE.exchange
        # "SH"

        # 传递给 Gateway
        gateway.fetch_index(IndexSymbol.SSE)

        # 遍历所有指数
        for index in IndexSymbol:
            print(index.symbol, index.display_name)

    注意：
        value / symbol 使用标准的 "代码.交易所" 格式，
        例如 "000001.SH"。

        如果底层数据源只接受纯代码，例如 "000001"，
        使用 .code 获取。
    """

    SSE = ("000001.SH", "上证指数")
    SZSE = ("399001.SZ", "深证成指")
    GEM = ("399006.SZ", "创业板指")
    STAR = ("000680.SH", "科创综指")
    STAR_50 = ("000688.SH", "科创50")

    SSE_50 = ("000016.SH", "上证50")
    CSI_300 = ("000300.SH", "沪深300")
    CSI_500 = ("000905.SH", "中证500")
    CSI_1000 = ("000852.SH", "中证1000")
    CSI_A500 = ("000510.SH", "中证A500")

    def __new__(cls, symbol: str, display_name: str):
        obj = str.__new__(cls, symbol)
        obj._value_ = symbol
        obj.symbol = symbol
        obj.display_name = display_name
        return obj

    @property
    def code(self) -> str:
        """不带市场后缀的指数代码。"""
        return self.symbol.split(".", 1)[0]

    @property
    def exchange(self) -> str:
        """交易所代码。"""
        return self.symbol.split(".", 1)[1]


class IndustryLevel(int, Enum):
    """行业分类层级。"""

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4


class IndustryStandard(str, Enum):
    """
    行业分类标准。

    不同数据源、研究机构使用的行业分类体系可能不同，
    因此不能简单地使用一个 industry 字段表示。
    """

    # 中证行业分类
    CSI = "csi"

    # 国民经济行业分类
    NATIONAL = "national"

    # 证监会行业分类
    CSRC = "csrc"

    # 申万行业分类
    SW = "sw"

    # Wind 行业分类
    WIND = "wind"

    # 自定义分类
    CUSTOM = "custom"
