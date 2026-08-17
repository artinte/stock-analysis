from typing import Optional

from base import StockDataGateway
from registry import GatewayRegistry

# ============================================================
# 加载内置数据源
#
# 这些 import 的主要作用：
#
#     import gateway.py
#           ↓
#     执行 @GatewayRegistry.register(...)
#           ↓
#     自动注册
# ============================================================

from providers.akshare.gateway import AkShareGateway
from providers.yinhe.gateway import YinheGateway


class DataManager:
    """
    股票数据统一管理器。
    """

    DEFAULT_PROVIDER = "akshare"

    def __init__(
        self,
        provider_name: str = DEFAULT_PROVIDER,
        config: Optional[dict] = None,
    ):

        self.provider = (
            provider_name.strip().lower()
        )

        self.config = config or {}

        self.gateway: StockDataGateway = (
            GatewayRegistry.create(
                self.provider,
                self.config,
            )
        )

    def start(self) -> bool:

        return self.gateway.login(
            self.config
        )

    def stop(self) -> None:

        self.gateway.logout()

    def health_check(self) -> bool:

        return self.gateway.health_check()

    def get_stock(
        self,
        symbol: str,
    ):
        return self.gateway.fetch_stock(
            symbol
        )

    def get_quote(
        self,
        symbol: str,
    ):
        return self.gateway.fetch_quote(
            symbol
        )

    def get_quotes(
        self,
        symbols: list[str],
    ):
        return self.gateway.fetch_quotes(
            symbols
        )

    def get_kline(
        self,
        symbol: str,
        interval,
        start_time=None,
        end_time=None,
        limit: int = 1000,
    ):
        return self.gateway.fetch_kline(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    def get_valuation(
        self,
        symbol: str,
    ):
        return self.gateway.fetch_valuation(
            symbol
        )

    @classmethod
    def available_providers(
        cls,
    ) -> list[str]:

        return GatewayRegistry.names()