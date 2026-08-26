from __future__ import annotations

from gateways.manager import DataManager
from core.models.stock import Stock

"""
股票基础信息测试。

运行：python -m tests.gateways.test_stock
"""


def test_stock(
    provider_name: str,
    symbol: str,
) -> None:
    """
    测试指定数据源的股票基础信息接口。

    Args:
        provider_name: 数据源名称，例如 yinhe、akshare。
        symbol: 标准证券代码，例如 600519.SH。
    """
    print(f"【股票基础信息】{provider_name} / {symbol}")

    data: DataManager | None = None

    try:
        data = DataManager(provider_name)

        data.start()

        stock: Stock | None = data.get_stock(symbol)

        if stock is None:
            print("❌ 未获取到股票信息")
            return

        stock.display()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现股票基础信息")

    except Exception as exc:
        print(f"❌ 获取股票基础信息失败：{exc}")

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
