from __future__ import annotations

from datetime import date
from typing import Optional

from common.enums.quote_level import QuoteLevel

from core.models.financial.income_statement import IncomeStatement
from core.models.financial.financial import Financial
from core.models.valuation import Valuation
from core.models.stock import Stock
from core.models.quote import Quote
from core.models.industry import Industry
from core.models.financial.balance_sheet import BalanceSheet
from core.models.financial.cash_flow import CashFlow
from core.models.industry_profile import IndustryProfile

from core.models.crypto.quote import CryptoQuote
from core.models.crypto.kline import CryptoKline

from gateways.registry import GatewayRegistry
from gateways.stock_data_gateway import StockDataGateway
from gateways.services.industry_service import IndustryService


class DataManager:
    """
    统一数据管理器。

    DataManager 对上层业务提供统一的数据访问入口，
    屏蔽不同数据源和不同资产类型的实现细节。

    支持的资产类型：

    - 股票：stock
    - 加密货币：crypto

    支持的数据源示例：

    - yinhe
    - akshare
    - binance

    设计原则：

    - 股票 Gateway 只负责股票数据
    - Crypto Gateway 只负责加密货币数据
    - DataManager 负责统一调度
    - FastAPI 不直接实例化具体 Gateway
    """

    DEFAULT_STOCK_PROVIDER = "yinhe"
    DEFAULT_CRYPTO_PROVIDER = "binance"

    def __init__(
        self,
        provider_name: str = DEFAULT_STOCK_PROVIDER,
        config: Optional[dict] = None,
        crypto_provider_name: str = DEFAULT_CRYPTO_PROVIDER,
    ):
        self.config = config or {}

        # --------------------------------------------------
        # 股票 Gateway
        # --------------------------------------------------
        self.stock_provider = provider_name.strip().lower()

        self.stock_gateway: StockDataGateway = GatewayRegistry.create(
            self.stock_provider,
            self.config,
        )

        # --------------------------------------------------
        # 加密货币 Gateway
        # --------------------------------------------------
        self.crypto_provider = crypto_provider_name.strip().lower()

        self.crypto_gateway = GatewayRegistry.create(
            self.crypto_provider,
            self.config,
        )

        # --------------------------------------------------
        # 行业服务
        # --------------------------------------------------
        self.industry = IndustryService()

    # ======================================================
    # 生命周期管理
    # ======================================================

    def start(self) -> bool:
        """
        启动数据源。

        股票数据源和加密货币数据源分别启动。
        某些数据源可能不需要登录，例如 Binance 公共行情接口。
        """

        stock_started = self.stock_gateway.login(self.config)

        crypto_started = True

        # 某些 Crypto Gateway 可能不需要登录。
        # 如果 Gateway 实现了 login，则调用它。
        login_method = getattr(self.crypto_gateway, "login", None)

        if callable(login_method):
            crypto_started = login_method(self.config)

        return bool(stock_started and crypto_started)

    def stop(self) -> None:
        """
        停止所有数据源。
        """

        logout_method = getattr(self.stock_gateway, "logout", None)

        if callable(logout_method):
            logout_method()

        crypto_logout_method = getattr(
            self.crypto_gateway,
            "logout",
            None,
        )

        if callable(crypto_logout_method):
            crypto_logout_method()

    def health_check(self) -> bool:
        """
        检查所有数据源是否正常。

        只有股票和加密货币数据源都正常时才返回 True。
        """

        stock_health = True
        crypto_health = True

        stock_health_method = getattr(
            self.stock_gateway,
            "health_check",
            None,
        )

        if callable(stock_health_method):
            stock_health = bool(stock_health_method())

        crypto_health_method = getattr(
            self.crypto_gateway,
            "health_check",
            None,
        )

        if callable(crypto_health_method):
            crypto_health = bool(crypto_health_method())

        return stock_health and crypto_health

    # ======================================================
    # 股票数据
    # ======================================================

    def get_stock(
        self,
        symbol: str,
    ) -> Stock:
        """
        获取股票基础信息。
        """

        return self.stock_gateway.fetch_stock(symbol)

    def get_stocks(
        self,
        symbols: list[str],
    ) -> list[Stock]:
        """
        批量获取股票基础信息。
        """

        return self.stock_gateway.fetch_stocks(symbols)

    def get_quote(
        self,
        symbol: str,
        level: QuoteLevel = QuoteLevel.LEVEL_1,
    ) -> Quote:
        """
        获取股票实时行情。
        """

        return self.stock_gateway.fetch_quote(
            symbol,
            level,
        )

    def get_quotes(
        self,
        symbols: list[str],
        level: QuoteLevel = QuoteLevel.LEVEL_1,
    ):
        """
        批量获取股票实时行情。
        """

        return self.stock_gateway.fetch_quotes(
            symbols,
            level,
        )

    def get_kline(
        self,
        symbol: str,
        interval,
        start_time=None,
        end_time=None,
        limit: int = 1000,
    ):
        """
        获取股票 K 线。
        """

        return self.stock_gateway.fetch_kline(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    def get_klines(
        self,
        symbols: list[str],
        interval,
        start_time=None,
        end_time=None,
        limit: int = 1000,
    ):
        """
        批量获取股票 K 线。
        """

        return self.stock_gateway.fetch_klines(
            symbols=symbols,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    def get_income_statement(
        self,
        symbol: str,
        start_year: Optional[int] = None,
        start_quarter: Optional[int] = None,
        end_year: Optional[int] = None,
        end_quarter: Optional[int] = None,
    ) -> list[IncomeStatement]:
        """
        获取利润表。
        """

        return self.stock_gateway.fetch_income_statement(
            symbol,
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        )

    def get_balance_sheet(
        self,
        symbol: str,
        start_year: Optional[int] = None,
        start_quarter: Optional[int] = None,
        end_year: Optional[int] = None,
        end_quarter: Optional[int] = None,
    ) -> list[BalanceSheet]:
        """
        获取资产负债表。
        """

        return self.stock_gateway.fetch_balance_sheet(
            symbol,
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        )

    def get_cash_flow(
        self,
        symbol: str,
        start_year: Optional[int] = None,
        start_quarter: Optional[int] = None,
        end_year: Optional[int] = None,
        end_quarter: Optional[int] = None,
    ) -> list[CashFlow]:
        """
        获取现金流量表。
        """

        return self.stock_gateway.fetch_cash_flow(
            symbol,
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        )

    def get_financial(
        self,
        symbol: str,
        start_year: Optional[int] = None,
        start_quarter: Optional[int] = None,
        end_year: Optional[int] = None,
        end_quarter: Optional[int] = None,
    ) -> list[Financial]:
        """
        获取综合财务数据。
        """

        return self.stock_gateway.fetch_financial(
            symbol,
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        )

    def get_valuation(
        self,
        symbol: str,
    ) -> Valuation:
        """
        获取股票估值数据。
        """

        return self.stock_gateway.fetch_valuation(symbol)

    def get_etf_composition(
        self,
        symbol: str,
        trade_date: date | None = None,
    ):
        """
        获取 ETF 成分及申赎信息。
        """

        return self.stock_gateway.fetch_etf_composition(
            symbol,
            trade_date,
        )

    # ======================================================
    # 加密货币数据
    # ======================================================

    def get_crypto_quote(
        self,
        symbol: str,
    ) -> CryptoQuote:
        """
        获取加密货币实时行情。

        示例：

            manager.get_crypto_quote("BTCUSDT")
            manager.get_crypto_quote("ETHUSDT")
        """

        return self.crypto_gateway.fetch_quote(symbol)

    def get_crypto_quotes(
        self,
        symbols: list[str],
    ) -> list[CryptoQuote]:
        """
        批量获取加密货币实时行情。
        """

        fetch_quotes = getattr(
            self.crypto_gateway,
            "fetch_quotes",
            None,
        )

        if callable(fetch_quotes):
            return fetch_quotes(symbols)

        return [
            self.crypto_gateway.fetch_quote(symbol)
            for symbol in symbols
        ]

    def get_crypto_kline(
        self,
        symbol: str,
        interval: str = "1h",
        start_time=None,
        end_time=None,
        limit: int = 500,
    ) -> list[CryptoKline]:
        """
        获取加密货币 K 线。

        示例：

            manager.get_crypto_kline(
                symbol="BTCUSDT",
                interval="1h",
                limit=200,
            )
        """

        return self.crypto_gateway.fetch_kline(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    def get_crypto_klines(
        self,
        symbols: list[str],
        interval: str = "1h",
        start_time=None,
        end_time=None,
        limit: int = 500,
    ):
        """
        批量获取加密货币 K 线。
        """

        fetch_klines = getattr(
            self.crypto_gateway,
            "fetch_klines",
            None,
        )

        if callable(fetch_klines):
            return fetch_klines(
                symbols=symbols,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            )

        return [
            self.get_crypto_kline(
                symbol=symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            )
            for symbol in symbols
        ]

    # ======================================================
    # 行业服务
    # ======================================================

    def get_industry(
        self,
        symbol: str,
    ) -> Industry:
        return self.industry.get_industry(symbol)

    def get_industries(
        self,
        symbols: list[str],
    ) -> list[Industry]:
        return self.industry.get_industries(symbols)

    def get_industry_profile(
        self,
        industry: Industry,
    ) -> IndustryProfile:
        return self.industry.get_industry_profile(industry)

    # ======================================================
    # Provider 信息
    # ======================================================

    @classmethod
    def available_providers(cls) -> list[str]:
        return GatewayRegistry.names()