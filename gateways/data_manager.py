from datetime import datetime
from typing import List, Optional
from gateways.pe_type import PEType
from models import kline
from gateways.amazing_data_gateway import AmazingDataGateway
from models.constants import Interval

# 这里可以导入其他网关，比如 from gateways.tdx_gateway import TdxGateway


class DataManager:
    def __init__(self, provider_name: str):
        # 1. 建立一个映射表，根据名字选择网关
        self._gateways = {
            "yinhe": AmazingDataGateway,
            # "tdx": TdxGateway,
        }

        target_class = self._gateways.get(provider_name.lower())
        if not target_class:
            raise ValueError(f"不支持的券商类型: {provider_name}")

        # 2. 实例化具体的网关
        self.gateway = target_class()

    def start(self, config: dict) -> bool:
        """统一的启动入口"""
        return self.gateway.login(config)

    def get_kline(
        self,
        symbol: str,
        interval: Interval = Interval.MINUTE_1,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[kline.Kline]:
        """
        统一获取 K 线入口
        :param symbol: 证券代码
        :param interval: K线周期 (1m, 5m, 1d等)
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param limit: 获取条数
        :return: Kline 对象列表
        """
        raw_data = self.gateway.fetch_kline(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        return raw_data

    def get_stock(self, symbol: str):
        """统一的取数入口"""
        return self.gateway.fetch_market_data(symbol)

    def get_stock_name(self, symbol: str) -> str:
        """获取股票名称"""
        return self.gateway.fetch_stock_name(symbol)
    
    def get_pe(self, symbol: str, pe_type: PEType = PEType.TTM) -> float:
        """
        获取指定类型的市盈率
        :param symbol: 股票代码 (如 '000510.SH')
        :param pe_type: PE类型，默认为 TTM
        :return: 市盈率数值
        """
        # 在内部网关调用时传递类型参数
        return self.gateway.fetch_pe(symbol, pe_type=pe_type.value)

    def stop(self):
        """统一的关闭入口"""
        self.gateway.logout()
