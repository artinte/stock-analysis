from __future__ import annotations

from gateways.manager import DataManager
from core.models.stock import Stock

"""
股票基础信息测试。

运行：
python -m tests.gateways.test_stock
"""


def run_stock_test(
    data: DataManager,
    symbol: str,
) -> None:
    """
    使用已有 DataManager 测试股票信息。

    用于集成测试。
    """

    print(f"【股票基础信息】{symbol}")

    try:

        stock: Stock | None = data.get_stock(symbol)

        if stock is None:
            print("❌ 未获取到股票信息")
            return

        stock.display()

    except NotImplementedError:

        print("⚠️ 当前数据源暂未实现股票基础信息")

    except Exception as exc:

        print(f"❌ 获取股票基础信息失败：{exc}")


def test_stock(
    provider_name: str,
    symbol: str,
) -> None:
    """
    独立测试入口。

    自己管理 DataManager 生命周期。
    """

    print(f"【股票基础信息测试】" f"{provider_name} / {symbol}")

    data: DataManager | None = None

    try:

        data = DataManager(provider_name)

        data.start()

        run_stock_test(
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

    test_stock(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
