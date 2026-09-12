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

        # 内存中的股票名称缓存，主要用于快速读取名称
        self._stock_name_cache: dict[str, str] = {}

        # 本地文件缓存
        self._stock_cache = FileCache[Stock](
            path=get_cache_path(
                provider="yinhe",
                name="stock_basic",
            ),
            ttl_days=90,
            serializer=self._stock_to_dict,
            deserializer=self._stock_from_dict,
        )

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

                # 同步名称缓存
                if cached_stock.name and cached_stock.name != "-":
                    self._stock_name_cache[cached_stock.symbol] = cached_stock.name

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

                symbol = row.get("MARKET_CODE") or "-"
                stock_name = row.get("SECURITY_NAME") or "-"

                exchange = get_exchange(symbol) if symbol != "-" else "-"

                stock = Stock(
                    symbol=symbol,
                    name=stock_name,
                    company_name=row.get("COMP_NAME") or "-",
                    exchange=exchange,
                    market=row.get("LISTPLATE_NAME") or "-",
                    listing_date=row.get("LISTDATE") or "-",
                    delisting_date=row.get("DELISTDATE") or "-",
                    listed_status=row.get("IS_LISTED") or "-",
                    source=self.gateway.display_name,
                )

                # 6. 写入本地缓存
                self._stock_cache.set(
                    key=stock.symbol,
                    value=stock,
                )

                # 7. 同步内存名称缓存
                if stock.name and stock.name != "-":
                    self._stock_name_cache[stock.symbol] = stock.name

                stocks.append(stock)

            return stocks

        except Exception as e:
            print(f"[银河网关] 获取股票信息失败 " f"{missing_symbols}: {e}")
            return stocks

    def fetch_stock_by_name(
        self,
        name: str,
    ) -> Optional[Stock]:
        """
        根据股票名称获取股票基础信息。

        当前实现需要数据源支持按名称查询。
        """
        self.gateway._ensure_started()

        if not name:
            return None

        try:
            stock_basic = self.gateway.info_data.get_stock_basic_by_name(
                name,
            )

            if stock_basic is None or stock_basic.empty:
                return None

            row = stock_basic.iloc[0]

            symbol = row.get("MARKET_CODE") or "-"
            stock_name = row.get("SECURITY_NAME") or "-"

            stock = Stock(
                symbol=symbol,
                name=stock_name,
                company_name=row.get("COMP_NAME") or "-",
                exchange=(get_exchange(symbol) if symbol != "-" else "-"),
                market=row.get("LISTPLATE_NAME") or "-",
                listing_date=row.get("LISTDATE") or "-",
                delisting_date=row.get("DELISTDATE") or "-",
                listed_status=row.get("IS_LISTED") or "-",
                source=self.gateway.display_name,
            )

            if stock.symbol != "-":
                self._stock_cache.set(
                    key=stock.symbol,
                    value=stock,
                )

            if stock.name and stock.name != "-":
                self._stock_name_cache[stock.symbol] = stock.name

            return stock

        except Exception as e:
            print(f"[银河网关] 根据名称获取股票信息失败 " f"{name}: {e}")
            return None

    def fetch_stock_name(
        self,
        symbol: str,
    ) -> str:
        """
        获取股票名称。
        """

        formatted_symbol = normalize_symbol(symbol)

        # 1. 先查内存名称缓存
        cached_name = self._stock_name_cache.get(
            formatted_symbol,
        )

        if cached_name:
            return cached_name

        # 2. 再查 Stock 文件缓存
        cached_stock = self._stock_cache.get(
            formatted_symbol,
        )

        if cached_stock is not None:
            if cached_stock.name and cached_stock.name != "-":
                self._stock_name_cache[formatted_symbol] = cached_stock.name

                return cached_stock.name

        # 3. 最后请求数据源
        try:
            self.gateway._ensure_started()

            stock_basic = self.gateway.info_data.get_stock_basic(
                [formatted_symbol],
            )

            if stock_basic is None or stock_basic.empty:
                return "未知名称"

            row = stock_basic.iloc[0]
            stock_name = row.get("SECURITY_NAME") or "-"

            if stock_name == "-":
                return "未知名称"

            self._stock_name_cache[formatted_symbol] = stock_name

            return stock_name

        except Exception as e:
            print(f"[银河网关] 获取股票名称失败 " f"{formatted_symbol}: {e}")
            return "获取失败"

    @staticmethod
    def _stock_to_dict(stock: Stock) -> dict:
        """
        将 Stock 对象序列化为 JSON 字典。
        """

        return {
            "symbol": stock.symbol,
            "name": stock.name,
            "company_name": stock.company_name,
            "exchange": stock.exchange,
            "market": stock.market,
            "listing_date": stock.listing_date,
            "delisting_date": stock.delisting_date,
            "listed_status": stock.listed_status,
            "source": stock.source,
        }

    @staticmethod
    def _stock_from_dict(data: dict) -> Stock:
        """
        将 JSON 字典反序列化为 Stock 对象。
        """

        return Stock(
            symbol=data.get("symbol", "-"),
            name=data.get("name", "-"),
            company_name=data.get("company_name", "-"),
            exchange=data.get("exchange", "-"),
            market=data.get("market", "-"),
            listing_date=data.get("listing_date", "-"),
            delisting_date=data.get("delisting_date", "-"),
            listed_status=data.get("listed_status", "-"),
            source=data.get("source", "-"),
        )
