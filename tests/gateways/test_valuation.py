from __future__ import annotations

from gateways.analysis.valuation_analyzer import ValuationAnalyzer
from gateways.data_manager import DataManager

"""
股票估值分析测试。

运行：
python -m tests.analysis.test_valuation
"""


def run_valuation_test(
    data: DataManager,
    symbol: str,
) -> None:
    """使用已有 DataManager 获取原始数据，并测试估值分析。"""

    print(f"【股票估值分析】{symbol}")

    try:
        quote = data.get_quote(
            symbol=symbol,
        )

        if quote is None:
            print("❌ 未获取到 Quote 数据")
            return

        income_statements = data.get_income_statement(
            symbol=symbol,
        )

        if not income_statements:
            print("❌ 未获取到 Financial 数据")
            return

        balance_sheets = data.get_balance_sheet(
            symbol=symbol,
        )

        cash_flows = data.get_cash_flow(
            symbol=symbol,
        )

        analyzer = ValuationAnalyzer()

        valuation = analyzer.analyze(
            quote=quote,
            income_statements=income_statements,
            balance_sheets=balance_sheets,
            cash_flows=cash_flows,
        )

        if valuation is None:
            print("❌ 未生成估值数据")
            return

        print("✅ 估值分析完成")

        valuation.display()

    except NotImplementedError as exc:
        print(f"⚠️ 当前数据源暂未实现接口：{exc}")

    except Exception as exc:
        print(f"❌ 估值分析失败：{exc}")


def test_valuation(
    provider_name: str,
    symbol: str,
) -> None:
    """独立测试股票估值分析。"""

    print(f"【股票估值测试】{provider_name} / {symbol}")

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
    test_valuation(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
