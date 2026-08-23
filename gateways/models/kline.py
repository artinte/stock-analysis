from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from common.constants import Interval


@dataclass(slots=True)
class Kline:
    """
    标准 K 线数据模型。

    所有行情数据源最终统一转换为该结构。

    支持：

        A股:
            腾讯
            银河证券
            AkShare
            TDX
            Tushare

        美股:
            Yahoo Finance
            Alpha Vantage
            Polygon

    数据流：

        DataSource
            ↓
        Gateway
            ↓
        Kline
            ↓
        技术分析
            ↓
        策略计算
            ↓
        绘图


    注意：

    Kline 只描述价格行为，
    不包含：

        股票基本信息
        行业
        公司信息
        财务
        新闻

    这些属于 StockCenter 其它模块。
    """

    # ======================================================
    # 基础
    # ======================================================

    symbol: str

    timestamp: datetime

    interval: Interval

    # ======================================================
    # OHLC
    # ======================================================

    open: float

    high: float

    low: float

    close: float

    # ======================================================
    # 成交
    # ======================================================

    volume: Optional[float] = None
    """
    成交量。

    A股:
        股

    美股:
        share
    """

    amount: Optional[float] = None
    """
    成交额。

    A股:
        元

    美股:
        dollar
    """

    turnover: Optional[float] = None
    """
    换手率。

    单位:

        %
    """

    # ======================================================
    # 涨跌
    # ======================================================

    change: Optional[float] = None

    change_percent: Optional[float] = None

    pre_close: Optional[float] = None
    """
    昨收价格。
    """

    # ======================================================
    # 复权
    # ======================================================

    adjusted: bool = False
    """
    是否复权。

    False:
        原始价格

    True:
        前复权 / 后复权
    """

    # ======================================================
    # 扩展字段
    # ======================================================

    turnover_rate: Optional[float] = None
    """
    换手率。

    保留兼容旧代码。

    新代码推荐使用 turnover。
    """

    amplitude: Optional[float] = None
    """
    振幅。

    计算：

        (high-low)/pre_close * 100
    """

    average_price: Optional[float] = None
    """
    均价。

    通常:

        amount / volume
    """

    def is_up(self) -> bool:
        """
        判断上涨。
        """

        if self.change_percent is None:
            return self.close > self.open

        return self.change_percent > 0

    def is_down(self) -> bool:
        """
        判断下跌。
        """

        if self.change_percent is None:
            return self.close < self.open

        return self.change_percent < 0
