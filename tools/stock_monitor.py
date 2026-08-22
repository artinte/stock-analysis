from gateways import DataManager, GatewayRegistry

"""
股票实时监控与数据源测试工具。

本模块用于通过项目统一的数据网关接口，
获取指定股票的基础信息、实时行情、估值和财务数据，
并以命令行表格形式输出股票监控报告。

数据访问流程：

    Stock Monitor
         ↓
    DataManager
         ↓
    StockDataGateway
         ↓
    指定数据源 Gateway
         ↓
    股票数据服务

当前支持通过 DataManager 选择不同的数据源，
例如：

    tencent
    yinhe
    akshare
    ...

主要功能：

1. 显示当前已经注册的数据源。
2. 启动指定股票数据源。
3. 获取股票基础信息。
4. 获取最新行情。
5. 获取估值数据。
6. 获取财务数据。
7. 在终端输出统一格式的股票监控报告。
8. 最后自动关闭数据源。

股票监控报告目前包含：

- 股票名称
- 股票代码
- 行情更新时间
- 当前价格
- 开盘价
- 最高价
- 最低价
- 涨跌额
- 涨跌幅
- 总市值
- 流通市值
- 营业收入
- 营收同比
- PE（TTM）
- PE（静态）
- PE（动态）
- 成交量
- 成交额
- 换手率
- 量比
- 涨停价
- 跌停价
- 均价
- 振幅
- 技术指标

其中部分技术指标目前预留接口，
后续可以接入统一的技术指标计算模块，
例如：

    MA
    MACD
    RSI
    Williams %R
    BIAS
    Bollinger Bands

本模块属于 tools 工具目录，
不参与核心业务逻辑，主要用于：

- 数据源联调
- 数据模型测试
- 数据完整性检查
- 命令行快速查看股票信息

执行：

    python -m tools.stock_monitor
"""


def print_stock_report(
    stock,
    quote,
    valuation,
    financial,
) -> None:

    # ==========================================================
    # 股票基本信息
    # ==========================================================

    name = stock.get("name", "--") if stock else "--"

    symbol = stock.get("symbol", "--") if stock else "--"

    print("=" * 40)

    print(f"股票名称: {name} ({symbol})")

    print(f"更新时间: " f"{quote.timestamp if quote else '--'}")

    print("-" * 40)

    # ==========================================================
    # 行情
    # ==========================================================

    print(
        f"现价: {quote.price if quote else '--'}"
        f"      "
        f"开盘: {quote.open if quote else '--'}"
    )

    print(
        f"最高: {quote.high if quote else '--'}"
        f"     "
        f"最低: {quote.low if quote else '--'}"
    )

    print(
        f"涨跌: {quote.change if quote else '--'}"
        f"      "
        f"幅度: {quote.change_percent if quote else '--'}%"
    )

    print("-" * 40)

    # ==========================================================
    # 市值
    # ==========================================================

    print(f"总市值: " f"{quote.market_cap if quote else '--'}")

    print(f"流通市值: " f"{quote.circulating_market_cap if quote else '--'}")

    print("-" * 40)

    # ==========================================================
    # 财务数据
    # ==========================================================

    revenue = "--"
    revenue_yoy = "--"

    if financial is not None:

        try:
            if hasattr(financial, "columns"):

                # 根据实际财务表字段获取
                if "REVENUE" in financial.columns:
                    revenue = financial["REVENUE"].iloc[-1]

                if "REVENUE_YOY" in financial.columns:
                    revenue_yoy = financial["REVENUE_YOY"].iloc[-1]

        except Exception:
            pass

    print(f"营业总收入: " f"{revenue}" f"  " f"(同比: {revenue_yoy})")

    # ==========================================================
    # 估值
    # ==========================================================

    print(f"PE(TTM): " f"{valuation.pe_ttm if valuation else '--'}")

    print(f"PE(静态): " f"{valuation.pe_static if valuation else '--'}")

    print(f"PE(动态): " f"{valuation.pe_dynamic if valuation else '--'}")

    print("-" * 40)

    # ==========================================================
    # 成交数据
    # ==========================================================

    print(
        f"成交量: "
        f"{quote.volume if quote else '--'}"
        f" 股"
        f"      "
        f"成交额: "
        f"{quote.amount if quote else '--'}"
        f" 亿元"
    )

    print(
        f"换手率: "
        f"{quote.turnover_rate if quote else '--'}"
        f"        "
        f"量比: "
        f"{quote.volume_ratio if quote else '--'}"
    )

    print("-" * 40)

    # ==========================================================
    # 涨跌停
    # ==========================================================

    print(
        f"涨停: "
        f"{quote.high_limit if quote else '--'}"
        f"      "
        f"跌停: "
        f"{quote.low_limit if quote else '--'}"
    )

    # Quote 当前没有 average_price / amplitude
    print(f"均价: --" f"      " f"振幅: --")

    print("-" * 40)

    # ==========================================================
    # 技术指标
    # ==========================================================

    print("移动平均价 (MA):")

    print("MA3:  --")
    print("MA5:  --")
    print("MA10: --")
    print("MA20: --")
    print("MA30: --")
    print("MA60: --")

    print("-" * 40)

    print("威廉指标(14): --")
    print("乖离率(5): --")

    print("=" * 40)


def main():
    print("可用数据源：")

    for name in GatewayRegistry.names():
        gateway_class = GatewayRegistry.get(name)

        display_name = getattr(
            gateway_class,
            "display_name",
            name,
        )

        print(f"  {name:<10} {display_name}")

    manager = DataManager(
        provider_name="tencent",
    )

    symbol = "600460"

    if not manager.start():
        raise RuntimeError("数据源启动失败")

    try:
        stock = manager.get_stock(symbol)
        quote = manager.get_quote(symbol)
        valuation = manager.get_valuation(symbol)
        financial = manager.get_financial(symbol)

        print_stock_report(
            stock=stock,
            quote=quote,
            valuation=valuation,
            financial=financial,
        )
    except Exception as e:
        print(f"股票数据获取失败: {e}")

    finally:
        manager.stop()


if __name__ == "__main__":
    main()
