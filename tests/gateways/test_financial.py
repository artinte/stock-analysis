from __future__ import annotations

from core.models.financial.financial import Financial
from gateways.manager import DataManager

"""
股票财务数据测试。

测试内容：

    fetch_income_statement()
    fetch_balance_sheet()
    fetch_cash_flow()
    fetch_financial()

运行：

    python -m tests.gateways.test_financial
"""


def run_financial_test(
    data: DataManager,
    symbol: str,
) -> None:
    """
    使用已有 DataManager 测试财务数据接口。

    测试四个公开财务接口：

        1. 利润表
        2. 资产负债表
        3. 现金流量表
        4. 统一 Financial
    """

    print("=" * 80)
    print(f"【股票财务数据】{symbol}")
    print("=" * 80)

    # ==========================================================
    # 1. 利润表
    # ==========================================================

    print("\n[1] 利润表")

    try:
        income = data.get_income_statement(symbol)

        if income:
            income.display()
        else:
            print("❌ 未获取到利润表数据")

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现利润表接口")

    except Exception as exc:
        print(f"❌ 获取利润表失败：{exc}")

    # ==========================================================
    # 2. 资产负债表
    # ==========================================================

    print("\n[2] 资产负债表")

    try:
        balance_sheet = data.get_balance_sheet(symbol)

        if balance_sheet:
            balance_sheet.display()
        else:
            print("❌ 未获取到资产负债表数据")

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现资产负债表接口")

    except Exception as exc:
        print(f"❌ 获取资产负债表失败：{exc}")

    # ==========================================================
    # 3. 现金流量表
    # ==========================================================

    print("\n[3] 现金流量表")

    try:
        cash_flow = data.get_cash_flow(symbol)

        if cash_flow:
            cash_flow.display()
        else:
            print("❌ 未获取到现金流量表数据")

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现现金流量表接口")

    except Exception as exc:
        print(f"❌ 获取现金流量表失败：{exc}")

    # ==========================================================
    # 4. 统一 Financial
    # ==========================================================

    print("\n[4] Financial")

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

    print(f"【股票财务测试】" f"{provider_name} / {symbol}")

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
    默认测试 AkShare 财务接口。

    当前使用 Mock 实现，
    不依赖真实网络数据。
    """

    test_financial(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
