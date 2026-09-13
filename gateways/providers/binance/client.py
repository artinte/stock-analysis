from __future__ import annotations

from typing import Any

import requests


class BinanceClient:
    """Binance 公开市场数据客户端。"""

    BASE_URL = "https://data-api.binance.vision"

    def __init__(
        self,
        timeout: float = 10.0,
    ) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """发送 GET 请求。"""
        response = self.session.get(
            f"{self.BASE_URL}{path}",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def fetch_ticker(self, symbol: str) -> dict[str, Any]:
        return self.get(
            "/api/v3/ticker/24hr",
            {"symbol": symbol.upper()},
        )

    def fetch_price(self, symbol: str) -> dict[str, Any]:
        return self.get(
            "/api/v3/ticker/price",
            {"symbol": symbol.upper()},
        )

    def fetch_klines(
        self,
        symbol: str,
        interval: str,
        limit: int,
    ) -> list[list[Any]]:
        return self.get(
            "/api/v3/klines",
            {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit,
            },
        )

    def fetch_depth(
        self,
        symbol: str,
        limit: int,
    ) -> dict[str, Any]:
        return self.get(
            "/api/v3/depth",
            {
                "symbol": symbol.upper(),
                "limit": limit,
            },
        )

    def fetch_trades(
        self,
        symbol: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        return self.get(
            "/api/v3/trades",
            {
                "symbol": symbol.upper(),
                "limit": limit,
            },
        )
