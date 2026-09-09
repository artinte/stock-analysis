from __future__ import annotations

from typing import Optional

from gateways.data_manager import DataManager
from core.models.financial.cash_flow import CashFlow

"""
现金流量表测试。

运行：
python -m tests.gateways.test_cash_flow
"""


def run_cash_flow_test(
    data_manager: DataManager,
    symbol: str,
    start_year: Optional[int] = None,
    start_quarter: Optional[int] = None,
    end_year: Optional[int] = None,
    end_quarter: Optional[int] = None,
) -> None:
    """
    使用已有 DataManager 测试现金流量表。

    用于集成测试。
    """

    print(f"【现金流量表】{symbol}")

    if start_year is not None:
        print(
            f"报告期："
            f"{start_year}Q{start_quarter}"
            f" ~ "
            f"{end_year}Q{end_quarter}"
        )
    else:
        print("报告期：全部")

    try:
        statements: list[CashFlow] = data_manager.get_cash_flow(
            symbol,
            start_year=start_year,
            start_quarter=start_quarter,
            end_year=end_year,
            end_quarter=end_quarter,
        )

        if not statements:
            print("❌ 未获取到现金流量表数据")
            return

        print(f"✅ 获取到 {len(statements)} 条现金流量表数据")

        print()

        for statement in statements:
            print("-" * 80)
            statement.display()

            print()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现现金流量表")

    except Exception as exc:
        print(f"❌ 获取现金流量表失败：{exc}")


def test_cash_flow(
    provider_name: str,
    symbol: str,
    start_year: Optional[int] = None,
    start_quarter: Optional[int] = None,
    end_year: Optional[int] = None,
    end_quarter: Optional[int] = None,
) -> None:
    """
    独立测试入口。

    自己管理 DataManager 生命周期。
    """

    print(f"【现金流量表测试】" f"{provider_name} / {symbol}")

    data: DataManager | None = None

    try:
        data = DataManager(provider_name)

        data.start()

        run_cash_flow_test(
            data_manager=data,
            symbol=symbol,
            start_year=start_year,
            start_quarter=start_quarter,
            end_year=end_year,
            end_quarter=end_quarter,
        )

    finally:
        if data is not None:
            try:
                data.stop()
                print("✅ 数据源已关闭")

            except Exception as exc:
                print(f"⚠️ 关闭数据源失败：{exc}")


def main() -> None:
    test_cash_flow(
        provider_name="yinhe",
        symbol="600519.SH",
        # ======================================================
        # 测试 2024Q1 ~ 2025Q4
        # ======================================================
        start_year=2024,
        start_quarter=1,
        end_year=2025,
        end_quarter=4,
    )


if __name__ == "__main__":
    main()
