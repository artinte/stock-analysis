from __future__ import annotations

from typing import Optional

from gateways.manager import DataManager
from core.models.financial.income_statement import IncomeStatement

"""
利润表测试。

运行：
python -m tests.gateways.test_income_statement
"""


def run_income_statement_test(
    data: DataManager,
    symbol: str,
    start_year: Optional[int] = None,
    start_quarter: Optional[int] = None,
    end_year: Optional[int] = None,
    end_quarter: Optional[int] = None,
) -> None:
    """
    使用已有 DataManager 测试利润表。

    用于集成测试。
    """

    print(f"【利润表】{symbol}")

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
        statements: list[IncomeStatement] = data.fetch_income_statement(
            symbol,
            start_year=start_year,
            start_quarter=start_quarter,
            end_year=end_year,
            end_quarter=end_quarter,
        )

        if not statements:
            print("❌ 未获取到利润表数据")
            return

        print(f"✅ 获取到 {len(statements)} 条利润表数据")

        print()

        for statement in statements:
            print("-" * 80)
            statement.display()

            print()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现利润表")

    except Exception as exc:
        print(f"❌ 获取利润表失败：{exc}")


def test_income_statement(
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

    print(f"【利润表测试】" f"{provider_name} / {symbol}")

    data: DataManager | None = None

    try:
        data = DataManager(provider_name)

        data.start()

        run_income_statement_test(
            data,
            symbol,
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
    test_income_statement(
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
