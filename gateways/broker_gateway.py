from abc import ABC, abstractmethod
from stock_detail import StockDetail


class BrokerGateway(ABC):
    """
    券商网关抽象基类
    实现对银河、通达信、同花顺等不同数据源的标准化接入。
    """

    @abstractmethod
    def login(self, config: dict) -> bool:
        """
        核心登录接口。
        内部需处理：类型转换（如 port 转 uint16_t）、身份认证、连接初始化。
        """
        pass

    @abstractmethod
    def fetch_market_data(self, symbol: str) -> StockDetail:
        """
        统一获取行情接口。
        所有子类必须将券商原始数据转换成 StockDetail 对象后返回。
        """
        pass

    @abstractmethod
    def logout(self):
        """安全登出接口"""
        pass
