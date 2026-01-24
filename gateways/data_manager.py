from gateways.amazing_data_gateway import AmazingDataGateway

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

    def get_stock(self, symbol: str):
        """统一的取数入口"""
        return self.gateway.fetch_market_data(symbol)

    def stop(self):
        """统一的关闭入口"""
        self.gateway.logout()
