from __future__ import annotations

from gateways.data_manager import DataManager
from core.models.etf.composition import ETFComposition

"""
ETF 成分股测试。

运行：
    python -m tests.gateways.test_etf_composition
"""


def run_etf_composition_test(
    manager: DataManager,
    symbol: str,
) -> None:
    """测试单个 ETF 成分股及申赎信息。"""

    print(f"【ETF成分股及申赎信息】{symbol}")

    try:
        composition: ETFComposition | None = manager.get_etf_composition(symbol)

        if composition is None:
            print("❌ 未获取到 ETF 成分股信息")
            return

        composition.display()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现 ETF 成分股信息")

    except Exception as exc:
        print(f"❌ 获取 ETF 成分股信息失败：{exc}")


def main() -> None:
    provider_name = "yinhe"

    manager = DataManager(provider_name)

    try:
        manager.start()

        print("=" * 80)
        print(f"【ETF成分股测试】{provider_name}")
        print("=" * 80)

        # 单个 ETF
        run_etf_composition_test(
            manager,
            "510300.SH",
        )

        print("=" * 80)

    finally:
        try:
            manager.stop()
            print("✅ 数据源已关闭")
        except Exception as exc:
            print(f"⚠️ 关闭数据源失败：{exc}")


if __name__ == "__main__":
    main()
