from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from gateways.models.constants import Interval


class StockDataGateway(ABC):
    """
    股票数据源统一抽象接口。

    所有数据源必须实现这一接口。
    """

    name: str = ""

    display_name: str = ""

    def __init__(
        self,
        config: Optional[dict] = None,
    ) -> None:
        self.config = config or {}
        self._started = False

    @abstractmethod
    def login(
        self,
        config: Optional[dict] = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def logout(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch_stock(
        self,
        symbol: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def fetch_quote(
        self,
        symbol: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def fetch_quotes(
        self,
        symbols: list[str],
    ):
        raise NotImplementedError

    @abstractmethod
    def fetch_kline(
        self,
        symbol: str,
        interval: Interval = Interval.DAY_1,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ):
        raise NotImplementedError

    @abstractmethod
    def fetch_valuation(
        self,
        symbol: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def fetch_financial(
        self,
        symbol: str,
    ):
        raise NotImplementedError

    def is_started(self) -> bool:
        return self._started

    def __enter__(self):
        self.login()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.logout()