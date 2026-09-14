from __future__ import annotations

from typing import Any

from infra.gateways.forex_data import ForexDataGateway


class ForexManager:
    """
    外汇数据管理器。

    ForexManager 负责外汇领域的数据访问与基础业务封装。

    Manager 不直接依赖具体的数据源，
    所有数据访问都通过 ForexDataGateway 完成。
    """

    def __init__(self, gateway: ForexDataGateway) -> None:
        self.gateway = gateway

    # ======================================================
    # 实时行情
    # ======================================================

    def get_quote(self, symbol: str) -> Any:
        """
        获取单个外汇品种的实时行情。
        """
        symbol = self._normalize_symbol(symbol)

        return self.gateway.fetch_quote(symbol)

    # ======================================================
    # 批量行情
    # ======================================================

    def get_quotes(
        self,
        symbols: list[str],
    ) -> list[Any]:
        """
        批量获取外汇实时行情。
        """
        normalized_symbols = [self._normalize_symbol(symbol) for symbol in symbols]

        return self.gateway.fetch_quotes(normalized_symbols)

    # ======================================================
    # K 线
    # ======================================================

    def get_kline(
        self,
        symbol: str,
        period: str = "1d",
        limit: int = 500,
    ) -> list[Any]:
        """
        获取外汇 K 线数据。
        """
        symbol = self._normalize_symbol(symbol)

        return self.gateway.fetch_kline(
            symbol=symbol,
            period=period,
            limit=limit,
        )

    # ======================================================
    # 生命周期
    # ======================================================

    def login(self, config: dict | None = None) -> bool:
        """登录或初始化外汇数据源。"""
        return bool(self.gateway.login(config))

    def logout(self) -> None:
        """关闭外汇数据源。"""
        self.gateway.logout()

    def health_check(self) -> bool:
        """检查外汇数据源是否可用。"""
        return bool(self.gateway.health_check())

    # ======================================================
    # 内部工具
    # ======================================================

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """
        标准化外汇品种代码。

        例如：
            eurusd -> EURUSD
            EUR/USD -> EURUSD
            usd-jpy -> USDJPY
        """
        if not symbol:
            raise ValueError("symbol 不能为空")

        return symbol.strip().upper().replace("/", "").replace("-", "").replace("_", "")
