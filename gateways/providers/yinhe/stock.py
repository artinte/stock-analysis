from __future__ import annotations

from datetime import date
from typing import Optional

from core.cache.file import FileCache
from core.cache.paths import get_cache_path

from core.models.stock import Stock
from utils.stock_mapping import normalize_symbol, get_exchange


class YinheStock:
    """
    银河股票基础信息适配器。
    """

    def __init__(self, gateway):
        self.gateway = gateway

        # 本地文件缓存
        self._stock_cache = FileCache[Stock](
            path=get_cache_path(
                provider="yinhe",
                name="stock_basic",
            ),
            ttl_days=90,
            serializer=Stock.to_dict,
            deserializer=Stock.from_dict,
        )

    @staticmethod
    def _parse_date(value) -> date | None:
        """
        将数据源日期转换为 date。
        """
        if value is None:
            return None

        if isinstance(value, date):
            return value

        value = str(value).strip()

        if not value or value == "-":
            return None

        # 兼容 20210827
        if len(value) == 8 and value.isdigit():
            return date(
                int(value[:4]),
                int(value[4:6]),
                int(value[6:8]),
            )

        # 兼容 2021-08-27
        return date.fromisoformat(value)

    @staticmethod
    def _clean_value(value):
        """
        清理数据源中的空值。
        """
        if value is None:
            return None

        # 兼容 pandas NaN
        try:
            if value != value:
                return None
        except Exception:
            pass

        value = str(value).strip()

        if not value or value == "-":
            return None

        return value

    def fetch_stock(
        self,
        symbol: str,
    ) -> Optional[Stock]:
        """
        获取单只股票基础信息。
        """
        stocks = self.fetch_stocks([symbol])
        return stocks[0] if stocks else None

    def fetch_stocks(
        self,
        symbols: list[str],
    ) -> list[Stock]:
        """
        批量获取股票基础信息。

        优先读取本地缓存。
        只有缓存未命中的股票才请求数据源。
        """

        self.gateway._ensure_started()

        if not symbols:
            return []

        # 1. 标准化 symbol，并去重，保持原有顺序
        normalized_symbols = list(
            dict.fromkeys(normalize_symbol(symbol) for symbol in symbols)
        )

        stocks: list[Stock] = []
        missing_symbols: list[str] = []

        # 2. 先读取本地缓存
        for symbol in normalized_symbols:
            cached_stock = self._stock_cache.get(symbol)

            if cached_stock is not None:
                stocks.append(cached_stock)
            else:
                missing_symbols.append(symbol)

        # 3. 如果全部命中缓存，直接返回
        if not missing_symbols:
            return stocks

        try:
            # 4. 只请求缓存中没有的股票
            stock_basic = self.gateway.info_data.get_stock_basic(
                missing_symbols,
            )

            if stock_basic is None or stock_basic.empty:
                return stocks

            # 5. 解析数据源返回结果
            for _, row in stock_basic.iterrows():

                symbol = self._clean_value(row.get("MARKET_CODE"))

                if symbol is None:
                    continue

                stock_name = self._clean_value(row.get("SECURITY_NAME"))

                exchange = get_exchange(symbol)

                stock = Stock(
                    symbol=symbol,
                    name=stock_name,
                    company_name=self._clean_value(row.get("COMP_NAME")),
                    exchange=exchange,
                    market=self._clean_value(row.get("LISTPLATE_NAME")),
                    listing_date=self._parse_date(row.get("LISTDATE")),
                    delisting_date=self._parse_date(row.get("DELISTDATE")),
                    listed_status=(
                        bool(row.get("IS_LISTED"))
                        if self._clean_value(row.get("IS_LISTED")) is not None
                        else None
                    ),
                    source=self.gateway.display_name,
                )

                # 6. 写入本地缓存
                self._stock_cache.set(
                    key=stock.symbol,
                    value=stock,
                )

                stocks.append(stock)

            return stocks

        except Exception as e:
            print(f"[银河网关] 获取股票信息失败 " f"{missing_symbols}: {e}")
            return stocks
