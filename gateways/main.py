from datetime import datetime, timedelta
from models.constants import Interval
from manager import DataManager

def print_separator(title: str = "") -> None:
    print()
    print("=" * 72)

    if title:
        print(f"  {title}")

    print("=" * 72)


def test_provider(
    provider_name: str,
    symbol: str,
) -> None:

    print_separator(
        f"测试数据源：{provider_name}"
    )

    try:
        data = DataManager(provider_name)
        
        data.start()

        print(f"数据源：{data.provider}")
        print(
            f"可用数据源："
            f"{', '.join(data.available_providers())}"
        )

    except Exception as exc:
        print(
            f"❌ 创建数据源失败：{exc}"
        )
        return

    print()
    print("正在检查数据源...")

    try:
        if data.health_check():
            print("✅ 数据源可用")
        else:
            print("❌ 数据源不可用")
            return

    except Exception as exc:
        print(
            f"❌ 数据源检查失败：{exc}"
        )
        return

    try:
        print()
        print("正在获取股票基础信息...")

        stock = data.get_stock(symbol)

        print("✅ 股票基础信息")
        print(f"   代码：{stock.symbol}")
        print(f"   名称：{stock.name}")
        print(f"   行业：{stock.industry}")
        print(f"   市场：{stock.market}")

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现股票基础信息")

    except Exception as exc:
        print(
            f"❌ 获取股票基础信息失败：{exc}"
        )

    try:
        print()
        print("正在获取最新行情...")

        quote = data.get_quote(symbol)

        print("✅ 最新行情")
        print(f"   股票：{quote.name}")
        print(f"   最新价：{quote.price}")
        print(f"   涨跌额：{quote.change}")
        print(f"   涨跌幅：{quote.change_percent}%")
        print(f"   今开：{quote.open}")
        print(f"   最高：{quote.high}")
        print(f"   最低：{quote.low}")
        print(f"   成交量：{quote.volume}")
        print(f"   成交额：{quote.amount}")
        print(f"   换手率：{quote.turnover_rate}%")
        print(f"   总市值：{quote.market_cap}")

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现最新行情")

    except Exception as exc:
        print(
            f"❌ 获取最新行情失败：{exc}"
        )

    try:
        print()
        print("正在获取日 K 线...")

        klines = data.get_kline(
            symbol=symbol,
            interval=Interval.DAY_1,
            start_time=(
                datetime.now()
                - timedelta(days=365)
            ),
            end_time=datetime.now(),
            limit=10,
        )

        print(
            f"✅ 获取到 {len(klines)} 条 K 线"
        )

        for item in klines[-5:]:
            print(
                f"   {item.timestamp:%Y-%m-%d} "
                f"O:{item.open:.2f} "
                f"H:{item.high:.2f} "
                f"L:{item.low:.2f} "
                f"C:{item.close:.2f} "
                f"V:{item.volume}"
            )

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现 K 线")

    except Exception as exc:
        print(
            f"❌ 获取 K 线失败：{exc}"
        )

    try:
        print()
        print("正在获取估值数据...")

        valuation = data.get_valuation(
            symbol
        )

        print("✅ 估值数据")
        print(f"   当前价格：{valuation.price}")
        print(f"   总市值：{valuation.market_cap}")
        print(
            f"   流通市值："
            f"{valuation.circulating_market_cap}"
        )
        print(
            f"   PE(TTM)："
            f"{valuation.pe_ttm}"
        )
        print(
            f"   PE(动态)："
            f"{valuation.pe_dynamic}"
        )
        print(
            f"   PE(静态)："
            f"{valuation.pe_static}"
        )
        print(f"   PB：{valuation.pb}")
        print(f"   PS：{valuation.ps}")

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现估值")

    except Exception as exc:
        print(
            f"❌ 获取估值失败：{exc}"
        )

    try:
        print()
        print("正在关闭数据源...")

        data.stop()

        print("✅ 数据源已关闭")

    except Exception as exc:
        print(
            f"⚠️ 关闭数据源失败：{exc}"
        )


def test_batch_quotes(
    provider_name: str,
    symbols: list[str],
) -> None:

    print_separator(
        f"批量行情测试：{provider_name}"
    )

    try:
        data = DataManager(provider_name)

        data.start()

        print(
            f"正在获取 {len(symbols)} 只股票..."
        )

        quotes = data.get_quotes(symbols)

        print(
            f"✅ 返回 {len(quotes)} 条行情"
        )

        for quote in quotes:
            print(
                f"   {quote.symbol:<12} "
                f"{quote.name or '-':<8} "
                f"{quote.price or 0:>10} "
                f"{quote.change_percent or 0:>8.2f}%"
            )

        data.stop()

    except Exception as exc:
        print(
            f"❌ 批量行情测试失败：{exc}"
        )


def main() -> None:

    print_separator(
        "Stock Analysis - Gateway Test"
    )

    print(
        "股票数据网关测试程序"
    )

    print(
        "用于验证不同数据源是否可以"
        "通过统一 DataManager 正常访问。"
    )

    print()

    print(
        "当前支持的数据源："
    )

    try:
        providers = (
            DataManager.available_providers()
        )

        for provider in providers:
            print(f"   • {provider}")

    except Exception as exc:
        print(
            f"❌ 获取数据源列表失败：{exc}"
        )
        return

    # ==========================================================
    # 测试股票
    # ==========================================================

    symbol = "600519.SH"

    print()
    print(f"测试股票：{symbol}")

    # ==========================================================
    # 默认数据源
    # ==========================================================

    test_provider(
        "yinhe",
        symbol,
    )

    # ==========================================================
    # 批量行情
    # ==========================================================

    test_batch_quotes(
        "yinhe",
        [
            "600519.SH",
            "000001.SZ",
            "601318.SH",
        ],
    )

    # ==========================================================
    # 银河
    #
    # 如果本机已经配置银河环境，可以取消注释。
    # ==========================================================

    # test_provider(
    #     "yinhe",
    #     symbol,
    # )

    # ==========================================================
    # TDX
    #
    # 当前如果还没有实现 TDX，可以暂时不测试。
    # ==========================================================

    # test_provider(
    #     "tdx",
    #     symbol,
    # )

    print_separator(
        "测试完成"
    )


if __name__ == "__main__":
    main()