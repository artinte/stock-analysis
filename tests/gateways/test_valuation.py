from __future__ import annotations

from core.models.valuation import Valuation
from gateways.data_manager import DataManager

"""
股票估值数据测试。

运行：
python -m tests.gateways.test_valuation
"""


def run_valuation_test(
    data: DataManager,
    symbol: str,
) -> None:
    """使用已有 DataManager 测试估值信息。

    用于集成测试。
    """
    print(f"【股票估值数据】{symbol}")

    try:
        # 调用获取估值的方法
        valuation: Valuation | None = data.get_valuation(symbol)

        if valuation is None:
            print("❌ 未获取到估值数据")
            return

        # 打印估值数据
        valuation.display()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现估值数据接口")

    except Exception as exc:
        print(f"❌ 获取股票估值失败：{exc}")


def test_valuation(
    provider_name: str,
    symbol: str,
) -> None:
    """独立测试入口。

    自己管理 DataManager 生命周期。
    """
    print(f"【股票估值测试】" f"{provider_name} / {symbol}")

    data: DataManager | None = None

    try:
        data = DataManager(provider_name)
        data.start()

        run_valuation_test(
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
    # 默认测试银河证券的贵州茅台估值
    test_valuation(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
