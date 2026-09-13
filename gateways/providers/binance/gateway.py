from __future__ import annotations

from typing import Any

from gateways.providers.binance.client import BinanceClient


class BinanceGateway:
    """Binance 加密货币数据 Gateway。"""

    name = "binance"

    def __init__(
        self,
        client: BinanceClient | None = None,
    ) -> None:
        self.client = client or BinanceClient()

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """将项目内部 symbol 转换为 Binance 交易对。"""
        return symbol.replace("/", "").replace("-", "").upper()

    def fetch_quote(self, symbol: str) -> dict[str, Any]:
        """获取标准化行情。"""
        symbol = self.normalize_symbol(symbol)

        data = self.client.fetch_ticker(symbol)

        return {
            "symbol": symbol,
            "exchange": self.name,
            "last_price": float(data["lastPrice"]),
            "prev_close": float(data["prevClosePrice"]),
            "open_price": float(data["openPrice"]),
            "high_price": float(data["highPrice"]),
            "low_price": float(data["lowPrice"]),
            "change": float(data["priceChange"]),
            "change_percent": float(data["priceChangePercent"]),
            "volume": float(data["volume"]),
            "amount": float(data["quoteVolume"]),
            "trade_count": int(data["count"]),
            "source": self.name,
        }

    def fetch_quotes(
        self,
        symbols: list[str],
    ) -> list[dict[str, Any]]:
        """批量获取行情。"""
        return [self.fetch_quote(symbol) for symbol in symbols]

    def fetch_klines(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """获取标准化 K 线。"""
        symbol = self.normalize_symbol(symbol)

        rows = self.client.fetch_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )

        return [
            {
                "symbol": symbol,
                "exchange": self.name,
                "timestamp": row[0],
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]),
                "close_time": row[6],
                "quote_volume": float(row[7]),
                "trade_count": int(row[8]),
                "source": self.name,
            }
            for row in rows
        ]

    def fetch_order_book(
        self,
        symbol: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        symbol = self.normalize_symbol(symbol)

        data = self.client.fetch_depth(
            symbol=symbol,
            limit=limit,
        )

        return {
            "symbol": symbol,
            "exchange": self.name,
            "last_update_id": data["lastUpdateId"],
            "bids": [
                {
                    "price": float(price),
                    "quantity": float(quantity),
                }
                for price, quantity in data["bids"]
            ],
            "asks": [
                {
                    "price": float(price),
                    "quantity": float(quantity),
                }
                for price, quantity in data["asks"]
            ],
            "source": self.name,
        }
