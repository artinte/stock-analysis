from __future__ import annotations

from core.models.quote import Quote
from gateways.manager import DataManager

"""
股票行情数据测试。

运行：
python -m tests.gateways.test_quote
"""


def run_quote_test(
    data: DataManager,
    symbol: str,
) -> None:
    """使用已有 DataManager 测试行情信息。

    用于集成测试。
    """
    print(f"【股票行情数据】{symbol}")

    try:
        # 调用获取行情的方法，假设为 get_quote
        quote: Quote | None = data.get_quote(symbol)

        if quote is None:
            print("❌ 未获取到行情数据")
            return

        # 打印行情快照，假设模型支持 display 方法
        quote.display()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现行情数据接口")

    except Exception as exc:
        print(f"❌ 获取股票行情失败：{exc}")


def test_quote(
    provider_name: str,
    symbol: str,
) -> None:
    """独立测试入口。

    自己管理 DataManager 生命周期。
    """
    print(f"【股票行情测试】{provider_name} / {symbol}")

    data: DataManager | None = None

    try:
        data = DataManager(provider_name)
        data.start()

        run_quote_test(
            data,
            symbol,
        )

    finally:
        if data is not None:
            try:
                data.stop()
                print("✅ 数据源已关闭")
            except Exception as exc:
                print(f"⚠️ 关闭数据源失败：{exc}")


def main() -> None:
    # 默认测试银河证券的贵州茅台行情
    test_quote(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
