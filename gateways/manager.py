import os
import pandas
from typing import Optional
from dotenv import load_dotenv

from core.models.financial.income_statement import IncomeStatement
from gateways.gateway import StockDataGateway
from core.models.stock import Stock
from core.models.industry import Industry
from core.models.industry_profile import IndustryProfile
from gateways.registry import GatewayRegistry
from gateways.services.industry_service import IndustryService

"""

股票数据统一管理层。

DataManager 是整个股票数据模块对上层业务提供的统一入口，
负责屏蔽不同数据源之间的实现差异。上层业务不需要直接依赖
AkShare、银河证券或其他具体数据源，只需要通过 DataManager
获取股票基础信息、行情、K 线、估值等标准化数据。

整体架构：

    上层业务
        │
        ▼
    DataManager
        │
        ▼
    StockDataGateway
        │
        ├── AkShareGateway
        ├── YinheGateway
        └── 其他数据源
                │
                ▼
            第三方数据接口

核心职责：

1. 统一数据源入口

    DataManager 对外提供统一的数据访问接口，例如：

        manager.get_stock()
        manager.get_quote()
        manager.get_quotes()
        manager.get_kline()
        manager.get_valuation()

    上层业务无需关心当前使用的是哪个数据源。

2. 管理数据源生命周期

    DataManager 负责数据源的启动、停止以及运行状态检查：

        manager.start()
        manager.stop()
        manager.health_check()

    具体的登录、连接、初始化和注销逻辑由对应的
    StockDataGateway 实现负责。

3. 支持多数据源切换

    DataManager 通过 provider_name 选择具体数据源：

        DataManager(provider_name="akshare")
        DataManager(provider_name="yinhe")

    数据源实例由 GatewayRegistry 统一创建。

    因此新增数据源时，不需要修改 DataManager，
    只需要实现新的 StockDataGateway 并注册到 GatewayRegistry。

4. 隔离第三方数据源依赖

    DataManager 不应该包含具体数据源的实现细节。

    例如：

        AkShare 的接口调用
        银河证券的登录逻辑
        AmazingData 的字段处理

    都应该放在对应的 Gateway 中。

    DataManager 只负责调用统一接口并向上层返回结果。

5. 与数据模型和分析模块解耦

    DataManager 的职责是“获取数据”，而不是“分析数据”。

    因此以下功能不应该放在 DataManager 中：

        - 技术指标计算
        - MACD / RSI / BOLL 等指标分析
        - PE / PB / PS 深度分析
        - 股票评分
        - 投资逻辑分析
        - AI 分析

    这些功能应该由独立的 indicators、analysis 等模块负责。

推荐的数据处理流程：

    DataManager
        │
        │ 获取原始/标准化数据
        ▼
    models
        │
        ├── Kline
        ├── Valuation
        └── 其他统一数据模型
        │
        ▼
    indicators
        │
        ├── MA
        ├── MACD
        ├── RSI
        ├── BOLL
        └── Williams
        │
        ▼
    analysis
        │
        ├── ValuationAnalyzer
        ├── TechnicalAnalyzer
        └── 其他分析模块

设计原则：

    DataManager 负责：“从哪里获取数据”
    Gateway 负责：“如何从具体数据源获取数据”
    Model 负责：“数据应该以什么形式表达”

    Indicators 负责：“如何计算技术指标”
    Analysis 负责：“如何分析这些数据”

这种分层可以避免业务代码与具体数据源产生强耦合，同时方便后续增加新的数据源、替换数据接口以及进行单元测试。

数据源注册机制：

    DataManager
        ↓
    GatewayRegistry.create(provider_name)
        ↓
    创建对应 Gateway
        ↓
    gateway.login()
        ↓
    gateway.fetch_xxx()

具体 Gateway 通常通过装饰器自动注册：

    @GatewayRegistry.register("akshare")
    class AkShareGateway(...):
        ...

    @GatewayRegistry.register("yinhe")
    class YinheGateway(...):
        ...

DataManager 本身不需要知道具体 Gateway 的实现细节。

扩展新的数据源时，推荐遵循以下方式：

    1. 创建新的 Gateway
    2. 继承 StockDataGateway
    3. 实现统一接口
    4. 使用 GatewayRegistry 注册
    5. 在数据源模块中完成第三方接口适配

例如：

    @GatewayRegistry.register("xxx")
    class XxxGateway(StockDataGateway):
        ...

之后即可通过：

    manager = DataManager(
        provider_name="xxx",
        config=config,
    )

使用新的数据源，而无需修改 DataManager 的核心代码。

注意：

    DataManager 不应该直接 import 并调用具体的数据源 SDK。
    所有第三方数据源依赖都应该封装在 providers 目录下的
    Gateway 实现中。

这样可以保证 DataManager 长期保持稳定，
使整个数据访问层具备较好的可扩展性、可维护性和可测试性。
"""


class DataManager:
    """
    股票数据统一管理器。
    """

    DEFAULT_PROVIDER = "yinhe"

    def __init__(
        self,
        provider_name: str = DEFAULT_PROVIDER,
        config: Optional[dict] = None,
    ):
        self.provider = provider_name.strip().lower()

        self.config = config or {}

        self.gateway: StockDataGateway = GatewayRegistry.create(
            self.provider,
            self.config,
        )

        # 行业服务
        self.industry = IndustryService()

    def start(self) -> bool:
        return self.gateway.login(self.config)

    def stop(self) -> None:
        self.gateway.logout()

    def health_check(self) -> bool:
        return self.gateway.health_check()

    def get_stock(
        self,
        symbol: str,
    ) -> Stock:
        return self.gateway.fetch_stock(symbol)

    def get_quote(
        self,
        symbol: str,
    ):
        return self.gateway.fetch_quote(symbol)

    def get_quotes(
        self,
        symbols: list[str],
    ):
        return self.gateway.fetch_quotes(symbols)

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
        return self.gateway.fetch_valuation(symbol)

    def fetch_income_statement(
        self,
        symbol: str,
        start_year: Optional[int] = None,
        start_quarter: Optional[int] = None,
        end_year: Optional[int] = None,
        end_quarter: Optional[int] = None,
    ) -> list[IncomeStatement]:
        """
        获取指定股票的利润表数据。

        按财务报告期的“年份 + 季度”进行查询。

        查询范围为闭区间，开始季度和结束季度均包含在结果中。

        参数：
            symbol:
                股票代码，例如：
                    "600519.SH"

            start_year:
                起始财务年度。
                与 start_quarter 配合使用。
                不指定时，表示不限制起始时间。

            start_quarter:
                起始财务季度。
                可选值：
                    1：第一季度
                    2：第二季度
                    3：第三季度
                    4：第四季度

            end_year:
                结束财务年度。
                与 end_quarter 配合使用。
                不指定时，表示不限制结束时间。

            end_quarter:
                结束财务季度。
                可选值：
                    1：第一季度
                    2：第二季度
                    3：第三季度
                    4：第四季度

        查询示例：

            不指定任何时间：
                获取全部历史利润表数据。

            指定开始季度：
                start_year=2025,
                start_quarter=2

                获取 2025Q2 至最新季度的数据。

            指定结束季度：
                end_year=2025,
                end_quarter=3

                获取历史数据至 2025Q3。

            指定完整范围：
                start_year=2024,
                start_quarter=3,
                end_year=2025,
                end_quarter=2

                获取：
                    2024Q3
                    2024Q4
                    2025Q1
                    2025Q2

                其中开始季度和结束季度均包含。

        返回：
            list[IncomeStatement]:
                符合查询条件的利润表数据。
                如果没有匹配数据，则返回空列表。
        """
        return self.gateway.fetch_income_statement(
            symbol,
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        )

    def get_balance_sheet(
        self,
        symbol: str,
    ):
        return self.gateway.fetch_balance_sheet(symbol)

    def get_cash_flow(
        self,
        symbol: str,
    ):
        return self.gateway.fetch_cash_flow(symbol)

    def get_financial(
        self,
        symbol: str,
    ):
        return self.gateway.fetch_financial(symbol)

    @classmethod
    def available_providers(
        cls,
    ) -> list[str]:
        return GatewayRegistry.names()

    def get_industry(
        self,
        symbol: str,
    ) -> Industry:
        return self.industry.get_industry(symbol)

    def get_industry_profile(
        self,
        industry: Industry,
    ) -> IndustryProfile:
        return self.industry.get_industry_profile(industry)
