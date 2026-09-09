from __future__ import annotations

from core.models.financial.financial import Financial
from gateways.data_manager import DataManager

"""
股票 Financial 数据测试。

测试内容：

    get_financial()

运行：

    python -m tests.gateways.test_financial
"""


def run_financial_test(
    data: DataManager,
    symbol: str,
) -> None:
    """
    使用已有 DataManager 测试 Financial 数据接口。
    """

    print("=" * 80)
    print(f"【股票 Financial】{symbol}")
    print("=" * 80)

    # ==========================================================
    # Financial
    # ==========================================================

    print("\n[1] Financial")

    try:
        financial: Financial | None = data.get_financial(symbol)

        if financial is None:
            print("❌ 未获取到 Financial 数据")
        else:
            financial.display()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现 Financial 接口")

    except Exception as exc:
        print(f"❌ 获取 Financial 失败：{exc}")


def test_financial(
    provider_name: str,
    symbol: str,
) -> None:
    """
    独立测试入口。

    自己管理 DataManager 生命周期。
    """

    print(f"【股票 Financial 测试】{provider_name} / {symbol}")

    data: DataManager | None = None

    try:
        data = DataManager(provider_name)

        data.start()

        run_financial_test(
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
    """
    默认测试银河 Financial 接口。
    """

    test_financial(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
