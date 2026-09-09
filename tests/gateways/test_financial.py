from __future__ import annotations

from core.models.financial.financial import Financial
from gateways.analysis.financial_analyzer import FinancialAnalyzer
from gateways.data_manager import DataManager

"""
股票 Financial 数据及财务分析测试。

测试内容：

    1. get_financial()
    2. FinancialAnalyzer.analyze()
    3. 默认分析最新报告期
    4. 指定报告期分析
    5. 不存在报告期测试

运行：

    python -m tests.gateways.test_financial
"""


def run_financial_test(
    data: DataManager,
    symbol: str,
) -> None:
    """
    使用已有 DataManager 测试 Financial 数据及财务分析。
    """

    print("=" * 80)
    print(f"【股票 Financial】{symbol}")
    print("=" * 80)

    # ==========================================================
    # Financial
    # ==========================================================

    print("\n[1] Financial")

    try:
        financials: list[Financial] = data.get_financial(
            symbol=symbol,
        )

        if not financials:
            print("❌ 未获取到 Financial 数据")
            return

        print(f"✅ 获取到 {len(financials)} 个报告期")
        
        # ==========================================================
        # 展示最近 3 个报告期
        # ==========================================================

        recent_financials = financials[-3:]

        print(
            f"最近 {len(recent_financials)} 个报告期："
        )

        for financial in reversed(recent_financials):
            financial.display()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现 Financial 接口")
        return

    except Exception as exc:
        print(f"❌ 获取 Financial 失败：{exc}")
        return

    # ==========================================================
    # FinancialAnalyzer
    # ==========================================================

    analyzer = FinancialAnalyzer()

    # ==========================================================
    # 测试 1：默认分析最新报告期
    # ==========================================================

    print("\n[2] FinancialAnalyzer - 最新报告期")

    try:
        indicators = analyzer.analyze(
            financials,
        )

        print("✅ 默认分析成功")

        indicators.display()

    except Exception as exc:
        print(f"❌ 最新报告期分析失败：{exc}")

    # ==========================================================
    # 测试 2：指定报告期
    # ==========================================================

    report_date = "20260331"

    print("\n[3] FinancialAnalyzer - " f"指定报告期 {report_date}")

    try:
        indicators = analyzer.analyze(
            financials,
            report_date=report_date,
        )

        print(f"✅ 指定报告期 {report_date} 分析成功")

        indicators.display()

    except Exception as exc:
        print(f"❌ 指定报告期分析失败：{exc}")

    # ==========================================================
    # 测试 3：不存在的报告期
    #
    # 验证：
    #
    #     不存在时不会 fallback 到最新报告期
    # ==========================================================

    invalid_report_date = "20991231"

    print("\n[4] FinancialAnalyzer - " f"不存在报告期 {invalid_report_date}")

    try:
        indicators = analyzer.analyze(
            financials,
            report_date=invalid_report_date,
        )

        print(f"✅ 不存在报告期 {invalid_report_date}" " 未发生异常")

        indicators.display()

    except Exception as exc:
        print(f"❌ 不存在报告期测试失败：{exc}")


def test_financial(
    provider_name: str,
    symbol: str,
) -> None:
    """
    独立测试入口。

    自己管理 DataManager 生命周期。
    """

    print(f"【股票 Financial 测试】" f"{provider_name} / {symbol}")

    data: DataManager | None = None

    try:
        data = DataManager(provider_name)

        data.start()

        run_financial_test(
            data=data,
            symbol=symbol,
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
