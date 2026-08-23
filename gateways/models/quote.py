from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Quote:
    """
    股票实时行情快照。

    描述某一个证券在某个时间点的市场状态。


    数据来源：

        Tencent
        银河证券
        AkShare
        TDX
        Tushare
        Yahoo Finance


    数据流：

        DataSource
            ↓
        Gateway
            ↓
        Quote
            ↓
        StockCenter
            ↓
        行情展示 / 策略 / AI分析


    注意：

    Quote 不是历史数据。

    历史价格:
        Kline


    股票静态信息:
        Stock


    财务:
        Financial


    估值:
        Valuation
    """

    # ==========================================================
    # 基础
    # ==========================================================

    symbol: str

    name: Optional[str] = None

    timestamp: Optional[datetime] = None

    source: Optional[str] = None
    """
    数据来源。

    例如:

        tencent
        yinhe
        akshare
    """

    # ==========================================================
    # 当前价格
    # ==========================================================

    price: Optional[float] = None
    """
    当前价格。

    注意：

    部分数据源没有实时行情时，
    可能是最近交易日收盘价。
    """

    prev_close: Optional[float] = None
    """
    昨收。
    """

    open: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    # ==========================================================
    # 涨跌
    # ==========================================================

    change: Optional[float] = None

    change_percent: Optional[float] = None

    amplitude: Optional[float] = None
    """
    振幅。

    %

    计算:

        (high-low)/prev_close
    """

    # ==========================================================
    # 成交
    # ==========================================================

    volume: Optional[float] = None
    """
    成交量。

    A股:
        股

    美股:
        shares
    """

    amount: Optional[float] = None
    """
    成交额。

    A股:
        元

    美股:
        USD
    """

    # 换手率
    turnover: Optional[float] = None

    volume_ratio: Optional[float] = None
    """
    量比。
    """

    average_price: Optional[float] = None
    """
    成交均价。

    amount / volume
    """

    # ==========================================================
    # 股本
    # ==========================================================

    total_shares: Optional[float] = None
    """
    总股本。
    """

    circulating_shares: Optional[float] = None
    """
    流通股本。
    """

    # ==========================================================
    # 市值
    # ==========================================================

    market_cap: Optional[float] = None
    """
    总市值。

    单位:

        亿元
    """

    circulating_market_cap: Optional[float] = None
    """
    流通市值。

    单位:

        亿元
    """

    # ==========================================================
    # 估值
    # ==========================================================

    pe_dynamic: Optional[float] = None
    """
    动态 PE。
    """

    pe_static: Optional[float] = None
    """
    静态 PE。

    增加这个。

    原 Quote 缺少。
    """

    pe_ttm: Optional[float] = None
    """
    TTM PE。
    """

    pb: Optional[float] = None

    ps: Optional[float] = None
    """
    市销率。
    """

    # ==========================================================
    # 涨跌停
    # ==========================================================

    high_limit: Optional[float] = None

    low_limit: Optional[float] = None

    # ==========================================================
    # 交易状态
    # ==========================================================

    status: Optional[str] = None
    """
    股票状态。


    示例:

        trading
        suspended
        delisted
    """

    """
    交易货币。

    A股:

        CNY


    美股:

        USD
    """
    currency: Optional[str] = None

    def display(self) -> None:
        """打印实时行情信息。"""
        print("✅ 最新行情")
        print(f"  股票代码：{self.symbol}")
        print(f"  股票名称：{self.name or '-'}")
        print(f"  时间：{self.timestamp or '-'}")
        print(f"  数据来源：{self.source or '-'}")

        print(f"  当前价格：{self.price if self.price is not None else '-'}")
        print(f"  昨收：{self.prev_close if self.prev_close is not None else '-'}")
        print(f"  开盘：{self.open if self.open is not None else '-'}")
        print(f"  最高：{self.high if self.high is not None else '-'}")
        print(f"  最低：{self.low if self.low is not None else '-'}")

        print(f"  涨跌：{self.change if self.change is not None else '-'}")
        print(
            f"  涨跌幅："
            f"{self.change_percent if self.change_percent is not None else '-'}%"
        )
        print(f"  振幅：" f"{self.amplitude if self.amplitude is not None else '-'}%")

        print(f"  成交量：{self.volume if self.volume is not None else '-'}")
        print(f"  成交额：{self.amount if self.amount is not None else '-'}")
        print(f"  换手率：" f"{self.turnover if self.turnover is not None else '-'}%")
        print(
            f"  量比：" f"{self.volume_ratio if self.volume_ratio is not None else '-'}"
        )
        print(
            f"  成交均价："
            f"{self.average_price if self.average_price is not None else '-'}"
        )

        print(
            f"  总股本："
            f"{self.total_shares if self.total_shares is not None else '-'}"
        )
        print(
            f"  流通股本："
            f"{self.circulating_shares if self.circulating_shares is not None else '-'}"
        )

        print(
            f"  总市值："
            f"{self.market_cap if self.market_cap is not None else '-'} 亿元"
        )
        print(
            f"  流通市值："
            f"{self.circulating_market_cap if self.circulating_market_cap is not None else '-'} 亿元"
        )

        print(
            f"  动态 PE：" f"{self.pe_dynamic if self.pe_dynamic is not None else '-'}"
        )
        print(f"  静态 PE：" f"{self.pe_static if self.pe_static is not None else '-'}")
        print(f"  PE(TTM)：" f"{self.pe_ttm if self.pe_ttm is not None else '-'}")
        print(f"  PB：{self.pb if self.pb is not None else '-'}")
        print(f"  PS：{self.ps if self.ps is not None else '-'}")

        print(f"  涨停：" f"{self.high_limit if self.high_limit is not None else '-'}")
        print(f"  跌停：" f"{self.low_limit if self.low_limit is not None else '-'}")

        print(f"  状态：{self.status or '-'}")
        print(f"  货币：{self.currency or '-'}")
