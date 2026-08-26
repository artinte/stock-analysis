from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from common.constants import Interval


@dataclass(slots=True)
class Kline:
    """
    标准 K 线 / OHLCV 行情数据模型。

    Kline 是整个行情系统最基础的标准数据实体。

    数据流：

        DataSource
            ↓
        Gateway
            ↓
        Kline
            ↓
        ┌───────────────┐
        │ 技术指标       │
        │ 策略           │
        │ 回测           │
        │ 图表           │
        │ 行情数据库     │
        └───────────────┘

    设计原则：

    1. 不绑定任何数据源
    2. 不包含股票基本信息
    3. 不包含财务信息
    4. 不包含行业信息
    5. 不包含技术指标
    6. 保留原始行情核心字段
    7. 支持不同市场和不同周期
    """

    # ==========================================================
    # 标识
    # ==========================================================

    symbol: str
    """
    标准证券代码。

    例如：

        600519.SH
        000001.SZ
        300750.SZ
        AAPL
        TSLA
    """

    timestamp: datetime
    """
    K 线时间。

    日线：
        交易日

    分钟线：
        K 线开始时间。
    """

    interval: Interval
    """
    K 线周期。
    """

    # ==========================================================
    # OHLC
    # ==========================================================

    open: float
    high: float
    low: float
    close: float

    # ==========================================================
    # 成交
    # ==========================================================

    volume: Optional[float] = None
    """
    成交量。

    A 股通常为：
        股

    美股通常为：
        share

    期货通常为：
        手
    """

    amount: Optional[float] = None
    """
    成交额。

    A 股：
        元

    美股：
        美元
    """

    trades: Optional[int] = None
    """
    成交笔数。

    部分数据源不提供。
    """

    # ==========================================================
    # VWAP / 成交价格
    # ==========================================================

    average_price: Optional[float] = None
    """
    成交均价。

    常见计算：

        amount / volume
    """

    vwap: Optional[float] = None
    """
    VWAP（Volume Weighted Average Price）。

    如果数据源直接提供，则优先使用数据源值。

    注意：

        average_price 和 vwap 在不同数据源中的定义
        可能存在差异，因此保留两个字段。
    """

    # ==========================================================
    # 涨跌
    # ==========================================================

    pre_close: Optional[float] = None
    """
    前收盘价。
    """

    change: Optional[float] = None
    """
    涨跌额。

        close - pre_close
    """

    change_percent: Optional[float] = None
    """
    涨跌幅。

    单位：

        %
    """

    amplitude: Optional[float] = None
    """
    振幅。

    常见计算：

        (high - low) / pre_close * 100
    """

    # 换手率
    # 
    # 单位：%
    turnover: Optional[float] = None

    # ==========================================================
    # 复权
    # ==========================================================

    adjusted: bool = False
    """
    是否经过复权处理。

    False:
        原始行情

    True:
        已复权行情
    """

    adjustment: Optional[str] = None
    """
    复权类型。

    例如：

        None
        "forward"
        "backward"

    即：

        不复权
        前复权
        后复权
    """

    # ==========================================================
    # 交易状态
    # ==========================================================

    is_trading: Optional[bool] = None
    """
    当前 K 线对应时间是否处于交易状态。

    对分钟行情尤其有意义。
    """

    # ==========================================================
    # 数据质量
    # ==========================================================

    is_complete: bool = True
    """
    K 线是否完整。

    对实时行情特别重要。

    False 通常表示：

        当前正在形成的 K 线
    """

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None
    """
    数据来源。

    例如：

        yinhe
        akshare
        tdx
        tushare
        yahoo
    """

    # ==========================================================
    # 方法
    # ==========================================================

    def is_up(self) -> bool:
        """判断 K 线是否上涨。"""

        if self.change_percent is not None:
            return self.change_percent > 0

        return self.close > self.open

    def is_down(self) -> bool:
        """判断 K 线是否下跌。"""

        if self.change_percent is not None:
            return self.change_percent < 0

        return self.close < self.open

    def is_flat(self) -> bool:
        """判断 K 线是否平盘。"""

        if self.change_percent is not None:
            return self.change_percent == 0

        return self.close == self.open

    def display(self) -> None:
        """
        以适合行情终端/调试的形式显示 K 线。

        display() 只负责展示，
        不改变数据。
        """

        print(
            f"{self.symbol} "
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} "
            f"[{self.interval}]"
        )

        print(
            f"  OHLC       "
            f"O={self.open:.2f} "
            f"H={self.high:.2f} "
            f"L={self.low:.2f} "
            f"C={self.close:.2f}"
        )

        if self.pre_close is not None:
            print(f"  Pre Close  {self.pre_close:.2f}")

        if self.change is not None or self.change_percent is not None:
            change = f"{self.change:+.2f}" if self.change is not None else "-"

            change_percent = (
                f"{self.change_percent:+.2f}%"
                if self.change_percent is not None
                else "-"
            )

            print(f"  Change     " f"{change} ({change_percent})")

        if self.amplitude is not None:
            print(f"  Amplitude  {self.amplitude:.2f}%")

        if self.volume is not None:
            print(f"  Volume     {self.volume:,.2f}")

        if self.amount is not None:
            print(f"  Amount     {self.amount:,.2f}")

        if self.turnover is not None:
            print(f"  Turnover   {self.turnover:.2f}%")

        if self.average_price is not None:
            print(f"  Avg Price  {self.average_price:.2f}")

        if self.vwap is not None:
            print(f"  VWAP       {self.vwap:.2f}")

        if self.trades is not None:
            print(f"  Trades     {self.trades:,}")

        print(f"  Adjusted   " f"{self.adjustment or 'none'}")

        if self.source is not None:
            print(f"  Source     {self.source}")

        print(f"  Complete   " f"{self.is_complete}")
