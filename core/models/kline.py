from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from common.constants import Interval


@dataclass(slots=True)
class Kline:
    """
    标准 K 线数据模型。

    描述证券在一个指定时间周期内的 OHLCV 行情数据。
    不同数据源由 Gateway 统一转换为该结构。

    时间约定：

        timestamp 表示该 K 线周期的时间。

    例如：

        5 分钟 K：
            timestamp = 09:30:00
            表示 09:30 ~ 09:35 这一根 K 线

        日 K：
            timestamp = 当日交易日期
            表示当天交易周期


    OHLC 含义均针对“当前 K 线周期”：

        open:
            周期内第一笔成交价

        high:
            周期内最高成交价

        low:
            周期内最低成交价

        close:
            周期内最后一笔成交价

        volume:
            周期内成交量

        amount:
            周期内成交额
    """

    # 标准证券代码，例如 600519.SH
    symbol: str

    # K 线周期
    interval: Interval

    # K 线时间（周期开始时间）
    timestamp: datetime

    # 当前周期 OHLC
    open: float
    high: float
    low: float
    close: float

    # 当前周期成交量
    volume: float | None = None

    # 当前周期成交额
    amount: float | None = None

    def display(self) -> None:
        """
        打印 K 线数据。
        """
        print("✅ K线数据")
        print(f"  证券代码：{self.symbol}")
        print(f"  K线周期：{self.interval.value}")
        print(f"  交易时间：{self.timestamp}")
        print(f"  开盘价：{self.open:.2f}")
        print(f"  最高价：{self.high:.2f}")
        print(f"  最低价：{self.low:.2f}")
        print(f"  收盘价：{self.close:.2f}")
        print(f"  成交量：" f"{self.volume if self.volume is not None else '-'}")
        print(f"  成交额：" f"{self.amount if self.amount is not None else '-'}")
