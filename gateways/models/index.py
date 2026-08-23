from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Index:
    """
    市场指数。

    描述股票市场指数的基础信息和实时行情。

    例如：

        上证指数
        深证成指
        创业板指
        科创50
        沪深300
        中证500
        中证A500
    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    symbol: str

    name: Optional[str] = None

    exchange: Optional[str] = None

    timestamp: Optional[datetime] = None

    source: Optional[str] = None

    # ==========================================================
    # 行情
    # ==========================================================

    price: Optional[float] = None

    prev_close: Optional[float] = None

    open: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    # ==========================================================
    # 涨跌
    # ==========================================================

    change: Optional[float] = None

    change_percent: Optional[float] = None

    amplitude: Optional[float] = None

    # ==========================================================
    # 成交
    # ==========================================================

    volume: Optional[float] = None

    amount: Optional[float] = None

    # ==========================================================
    # 成分股
    # ==========================================================

    component_count: Optional[int] = None

    def display(self) -> None:
        """打印指数信息。"""

        print(f"指数代码：{self.symbol}")
        print(f"指数名称：{self.name or '-'}")
        print(f"交易所：{self.exchange or '-'}")
        print(f"时间：{self.timestamp or '-'}")
        print(f"数据来源：{self.source or '-'}")

        print(f"当前点位：{self.price if self.price is not None else '-'}")
        print(f"昨收：{self.prev_close if self.prev_close is not None else '-'}")
        print(f"开盘：{self.open if self.open is not None else '-'}")
        print(f"最高：{self.high if self.high is not None else '-'}")
        print(f"最低：{self.low if self.low is not None else '-'}")

        print(f"涨跌：{self.change if self.change is not None else '-'}")
        print(
            f"涨跌幅："
            f"{self.change_percent if self.change_percent is not None else '-'}%"
        )
        print(f"振幅：" f"{self.amplitude if self.amplitude is not None else '-'}%")

        print(f"成交量：{self.volume if self.volume is not None else '-'}")
        print(f"成交额：{self.amount if self.amount is not None else '-'}")
        print(f"成分股数量：{self.component_count or '-'}")
