from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)  # frozen=True 使对象不可变，提高安全性和哈希效率
class Kline:
    """
    K线数据结构
    """

    code: str  # 证券代码+市场 (如: "000001.SH")
    trade_time: datetime  # 交易所行情数据时间
    open: float  # 今开盘价
    high: float  # 最高价
    low: float  # 最低价
    close: float  # 收盘价
    volume: int  # 成交总量
    amount: float  # 成交总金额

    def __post_init__(self):
        """数据合法性简单校验"""
        if self.low > self.high:
            raise ValueError(f"最低价 {self.low} 不能高于最高价 {self.high}")
