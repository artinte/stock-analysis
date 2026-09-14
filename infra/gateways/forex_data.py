from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ForexDataGateway(ABC):
    """
    外汇数据 Gateway 抽象接口。

    Gateway 负责定义外汇数据源能够提供的基础能力。
    具体的数据源实现由 providers/<provider>/gateway.py 完成。
    """

    name: str = "unknown"

    # ======================================================
    # 实时行情
    # ======================================================

    @abstractmethod
    def fetch_quote(
        self,
        symbol: str,
    ) -> Any:
        """
        获取单个外汇品种的实时行情。

        Parameters
        ----------
        symbol:
            外汇品种，例如 EURUSD、USDJPY。

        Returns
        -------
        Any
            外汇行情数据。
        """
        raise NotImplementedError

    # ======================================================
    # 批量行情
    # ======================================================

    def fetch_quotes(
        self,
        symbols: list[str],
    ) -> list[Any]:
        """
        批量获取外汇行情。

        默认逐个调用 fetch_quote。
        数据源可以根据自身能力覆盖此方法。
        """
        return [self.fetch_quote(symbol) for symbol in symbols]

    # ======================================================
    # K 线
    # ======================================================

    @abstractmethod
    def fetch_kline(
        self,
        symbol: str,
        period: str = "1d",
        limit: int = 500,
    ) -> list[Any]:
        """
        获取外汇 K 线数据。

        Parameters
        ----------
        symbol:
            外汇品种。

        period:
            K 线周期，例如 1m、5m、1h、1d。

        limit:
            返回的数据数量。
        """
        raise NotImplementedError

    # ======================================================
    # 生命周期
    # ======================================================

    def login(self, config: dict | None = None) -> bool:
        """
        登录或初始化数据源。

        不需要登录的数据源可以直接使用默认实现。
        """
        return True

    def logout(self) -> None:
        """关闭数据源连接。"""
        return None

    def health_check(self) -> bool:
        """检查数据源是否可用。"""
        return True
