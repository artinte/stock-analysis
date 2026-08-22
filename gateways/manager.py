import os

from dotenv import load_dotenv
import pandas
from typing import Optional

from base import StockDataGateway

from registry import GatewayRegistry

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

    DataManager 负责：
        “从哪里获取数据”

    Gateway 负责：
        “如何从具体数据源获取数据”

    Model 负责：
        “数据应该以什么形式表达”

    Indicators 负责：
        “如何计算技术指标”

    Analysis 负责：
        “如何分析这些数据”

这种分层可以避免业务代码与具体数据源产生强耦合，
同时方便后续增加新的数据源、替换数据接口以及进行
单元测试。

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

    DEFAULT_PROVIDER = "akshare"

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

    def start(self) -> bool:

        return self.gateway.login(self.config)

    def stop(self) -> None:

        self.gateway.logout()

    def health_check(self) -> bool:

        return self.gateway.health_check()

    def get_stock(
        self,
        symbol: str,
    ):
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

    @classmethod
    def available_providers(
        cls,
    ) -> list[str]:

        return GatewayRegistry.names()


if __name__ == "__main__":
    import datetime
    import pandas
    from analysis.valuation import ValuationAnalyzer
    from providers.yinhe.gateway import YinheGateway
    from models.constants import Interval
    from indicators.volatility import calculate_bollinger_bands
    from indicators.macd import calculate_macd
    from indicators.moving_average import calculate_moving_averages
    from indicators.momentum import calculate_rsi, calculate_williams

    load_dotenv()

    config = {
        "username": os.getenv(
            "amazing_username",
            "",
        ),
        "password": os.getenv(
            "amazing_password",
            "",
        ),
        "host": os.getenv(
            "amazing_host",
            "",
        ),
        "port": int(
            os.getenv(
                "amazing_port",
                "0",
            )
        ),
        "local_path": os.getenv(
            "local_path",
            os.path.curdir,
        ),
    }

    manager = DataManager(provider_name="yinhe", config=config)

    print("\n股票数据与技术指标测试")

    if not manager.start():
        raise RuntimeError("数据源启动失败")

    symbol = "600519"

    try:
        # 1. 基础数据
        print(f"\n[1] 股票基础数据：{symbol}")

        stock = manager.get_stock(symbol)
        print(stock)

        # 2. K 线
        print("\n[2] 日 K 线")

        end_time = datetime.datetime.now()

        start_time = end_time - datetime.timedelta(days=720)

        klines = manager.get_kline(
            symbol=symbol,
            interval=Interval.DAY_1,
            start_time=start_time,
            end_time=end_time,
            limit=720,
        )

        print(f"共获取 {len(klines)} 条 K 线")

        # 3. 构建 DataFrame
        df = pandas.DataFrame(
            [
                {
                    "timestamp": item.timestamp,
                    "open": item.open,
                    "high": item.high,
                    "low": item.low,
                    "close": item.close,
                    "volume": item.volume,
                    "amount": item.amount,
                }
                for item in klines
            ]
        )

        # 按时间排序，并将 timestamp 作为索引
        df["timestamp"] = pandas.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        df = df.set_index("timestamp")

        # 4. 技术指标
        print("\n[3] 计算技术指标")

        ma = calculate_moving_averages(df)
        macd = calculate_macd(df)
        rsi = calculate_rsi(df)
        williams = calculate_williams(df)
        boll = calculate_bollinger_bands(df)

        def fmt(value) -> str:
            """格式化指标数值。"""
            if value is None:
                return "--"

            return f"{float(value):.2f}"

        print("✓ MA")
        print(
            f"  MA3  = {fmt(ma.get('MA3'))}    "
            f"MA5  = {fmt(ma.get('MA5'))}    "
            f"MA10 = {fmt(ma.get('MA10'))}"
        )
        print(
            f"  MA20 = {fmt(ma.get('MA20'))}    "
            f"MA30 = {fmt(ma.get('MA30'))}    "
            f"MA60 = {fmt(ma.get('MA60'))}"
        )

        print("✓ MACD")
        print(
            f"  DIF  = {fmt(macd.get('DIF'))}    "
            f"DEA  = {fmt(macd.get('DEA'))}    "
            f"MACD = {fmt(macd.get('MACD'))}"
        )

        print("✓ RSI")
        print(
            f"  RSI6  = {fmt(rsi.get('RSI6'))}    "
            f"RSI12 = {fmt(rsi.get('RSI12'))}    "
            f"RSI24 = {fmt(rsi.get('RSI24'))}"
        )

        print("✓ Williams %R")
        print(f"  Williams %R = {fmt(williams.get('Williams %R'))}")

        print("✓ Bollinger Bands")
        print(
            f"  Upper  = {fmt(boll.get('upper'))}    "
            f"Middle = {fmt(boll.get('middle'))}    "
            f"Lower  = {fmt(boll.get('lower'))}"
        )

        # 5. 合并所有技术指标
        print("\n[4] 技术指标结果")

        indicators = pandas.concat(
            [
                ma,
                macd,
                rsi,
                williams,
                boll,
            ],
            axis=1,
        )

        print(indicators.to_string(index=False))

        # 6. 财务数据
        print("\n[5] 财务数据")

        financial = manager.get_financial(symbol)
        print(financial)

        # 7. 估值
        print("\n[6] 估值分析")

        valuation = ValuationAnalyzer()
        print(valuation)

        print("\n测试完成")

    finally:
        manager.stop()
        print("数据源已停止")
