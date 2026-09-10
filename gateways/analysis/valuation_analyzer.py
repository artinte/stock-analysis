from __future__ import annotations

from typing import Optional

from core.models.financial.balance_sheet import BalanceSheet
from core.models.financial.cash_flow import CashFlow
from core.models.financial.income_statement import IncomeStatement
from core.models.quote import Quote
from core.models.valuation import Valuation


class ValuationAnalyzer:
    """股票估值分析器。

    Gateway / DataManager：
        负责获取原始数据。

    ValuationAnalyzer：
        负责根据原始数据计算估值指标。

    Valuation：
        保存最终计算结果。
    """

    def analyze(
        self,
        *,
        quote: Quote,
        income_statements: list[IncomeStatement],
        balance_sheets: Optional[list[BalanceSheet]] = None,
        cash_flows: Optional[list[CashFlow]] = None,
    ) -> Valuation:
        """计算股票估值。"""

        statements = self._sort_by_report_date(
            income_statements
        )

        balance_sheets = balance_sheets or []
        cash_flows = cash_flows or []

        # =========================================================
        # 最新财务数据
        # =========================================================

        latest_income = self._latest(statements)

        latest_balance_sheet = self._latest(
            self._sort_by_report_date(balance_sheets)
        )

        # =========================================================
        # 年报数据
        # =========================================================

        annual_income = self._find_latest_annual(
            statements
        )

        annual_net_profit = self._net_profit(
            annual_income
        )

        annual_revenue = self._value(
            annual_income,
            "revenue",
        )

        annual_ebitda = self._value(
            annual_income,
            "ebitda",
        )

        # =========================================================
        # TTM
        # =========================================================

        ttm_net_profit = self._calculate_ttm(
            statements,
            field="net_profit_attributable",
            fallback_field="net_profit",
        )

        ttm_revenue = self._calculate_ttm(
            statements,
            field="revenue",
        )

        # =========================================================
        # 市值
        # =========================================================

        market_cap = quote.market_cap
        float_market_cap = quote.float_market_cap

        # =========================================================
        # PE
        # =========================================================

        pe_static = self._divide(
            market_cap,
            annual_net_profit,
        )

        pe_ttm = self._divide(
            market_cap,
            ttm_net_profit,
        )

        # 当前没有盈利预测数据。
        # 后续接入预测净利润后再计算动态 PE。
        pe_dynamic = None

        # =========================================================
        # PB
        # =========================================================

        shareholders_equity = self._shareholders_equity(
            latest_balance_sheet
        )

        pb = self._divide(
            market_cap,
            shareholders_equity,
        )

        # =========================================================
        # PS
        # =========================================================

        ps_static = self._divide(
            market_cap,
            annual_revenue,
        )

        ps_ttm = self._divide(
            market_cap,
            ttm_revenue,
        )

        # =========================================================
        # 利润增长
        # =========================================================

        profit_growth = self._calculate_profit_growth(
            statements
        )

        # =========================================================
        # PEG
        # =========================================================

        peg = self._calculate_peg(
            pe_ttm=pe_ttm,
            profit_growth=profit_growth,
        )

        # =========================================================
        # Enterprise Value
        # =========================================================

        cash = self._cash(
            latest_balance_sheet
        )

        debt = self._debt(
            latest_balance_sheet
        )

        enterprise_value = self._enterprise_value(
            market_cap=market_cap,
            debt=debt,
            cash=cash,
        )

        # =========================================================
        # EV / EBITDA
        # =========================================================

        ev_ebitda = self._divide(
            enterprise_value,
            annual_ebitda,
        )

        # =========================================================
        # Earnings Yield
        # =========================================================

        earnings_yield = self._yield_from_pe(
            pe_ttm
        )

        # =========================================================
        # Dividend Yield
        # =========================================================

        # 当前没有股息数据源。
        dividend_yield = None

        # =========================================================
        # 返回 Valuation
        # =========================================================

        return Valuation(
            symbol=quote.symbol,
            timestamp=quote.timestamp,
            report_date=self._report_date(latest_income),
            source=quote.source,

            market_cap=market_cap,
            float_market_cap=float_market_cap,

            pe_static=self._round(pe_static),
            pe_dynamic=self._round(pe_dynamic),
            pe_ttm=self._round(pe_ttm),

            pb=self._round(pb),

            ps_static=self._round(ps_static),
            ps_ttm=self._round(ps_ttm),

            peg=self._round(peg),

            enterprise_value=self._round(
                enterprise_value
            ),
            ev_ebitda=self._round(
                ev_ebitda
            ),

            earnings_yield=self._round(
                earnings_yield
            ),
            dividend_yield=self._round(
                dividend_yield
            ),
        )

    # =============================================================
    # 报告期
    # =============================================================

    @staticmethod
    def _report_date(item) -> Optional[str]:
        """获取报告期。

        项目统一使用 report_date，例如：

            20260630
            20260331
            20251231
        """

        if item is None:
            return None

        value = getattr(
            item,
            "report_date",
            None,
        )

        if value is None:
            return None

        return str(value).strip()

    @classmethod
    def _report_date_key(
        cls,
        report_date: Optional[str],
    ) -> str:
        """转换报告期为可排序格式。"""

        if not report_date:
            return ""

        return (
            str(report_date)
            .strip()
            .replace("-", "")
            .replace("/", "")
            .replace(".", "")
        )

    @classmethod
    def _sort_by_report_date(cls, items):
        """按照 report_date 从新到旧排序。"""

        if not items:
            return []

        return sorted(
            items,
            key=lambda item: cls._report_date_key(
                cls._report_date(item)
            ),
            reverse=True,
        )

    @classmethod
    def _latest(cls, items):
        """获取最新一期数据。"""

        if not items:
            return None

        return cls._sort_by_report_date(items)[0]

    # =============================================================
    # 年报
    # =============================================================

    @classmethod
    def _find_latest_annual(
        cls,
        statements: list[IncomeStatement],
    ) -> Optional[IncomeStatement]:
        """获取最近一期年度报告。

        优先根据 report_date 的 1231 判断。
        """

        for statement in statements:
            report_date = cls._report_date(statement)

            if not report_date:
                continue

            report_date = cls._report_date_key(
                report_date
            )

            if report_date.endswith("1231"):
                return statement

        # 如果 report_date 无法判断，
        # 再兼容 report_type 的年度标识。
        for statement in statements:
            report_type = getattr(
                statement,
                "report_type",
                None,
            )

            if cls._is_annual_report_type(
                report_type
            ):
                return statement

        return None

    @staticmethod
    def _is_annual_report_type(
        report_type,
    ) -> bool:
        """判断 report_type 是否为年度报告。"""

        if report_type is None:
            return False

        value = str(report_type).strip().lower()

        return value in {
            "annual",
            "year",
            "yearly",
            "fy",
            "年报",
            "年度",
            "年度报告",
            "年",
        }

    # =============================================================
    # 财务字段
    # =============================================================

    @staticmethod
    def _value(
        item,
        field: str,
    ) -> Optional[float]:
        """安全获取数值字段。"""

        if item is None:
            return None

        value = getattr(
            item,
            field,
            None,
        )

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _value_with_fallback(
        cls,
        item,
        field: str,
        fallback_field: Optional[str] = None,
    ) -> Optional[float]:
        """获取字段，不存在时使用备用字段。"""

        value = cls._value(
            item,
            field,
        )

        if value is not None:
            return value

        if fallback_field:
            return cls._value(
                item,
                fallback_field,
            )

        return None

    @classmethod
    def _net_profit(
        cls,
        statement: Optional[IncomeStatement],
    ) -> Optional[float]:
        """获取净利润。

        优先使用归母净利润。
        """

        value = cls._value(
            statement,
            "net_profit_attributable",
        )

        if value is not None:
            return value

        return cls._value(
            statement,
            "net_profit",
        )

    # =============================================================
    # TTM
    # =============================================================

    @classmethod
    def _calculate_ttm(
        cls,
        statements: list[IncomeStatement],
        *,
        field: str,
        fallback_field: Optional[str] = None,
    ) -> Optional[float]:
        """计算 TTM。

        优先使用四个单季度数据。

        如果没有四个单季度数据，则使用：

            本期累计
            + 上年全年
            - 上年同期

        例如：

            20260630
            + 20251231
            - 20250630

        = 20260630 TTM
        """

        if not statements:
            return None

        statements = cls._sort_by_report_date(
            statements
        )

        # ---------------------------------------------------------
        # 1. 优先使用单季度数据
        # ---------------------------------------------------------

        single_quarters = cls._get_single_quarters(
            statements
        )

        if len(single_quarters) >= 4:
            values = []

            for statement in single_quarters[:4]:
                value = cls._value_with_fallback(
                    statement,
                    field,
                    fallback_field,
                )

                if value is None:
                    values = []
                    break

                values.append(value)

            if len(values) == 4:
                return sum(values)

        # ---------------------------------------------------------
        # 2. 使用累计数据计算
        # ---------------------------------------------------------

        return cls._calculate_ttm_from_cumulative(
            statements,
            field=field,
            fallback_field=fallback_field,
        )

    @classmethod
    def _get_single_quarters(
        cls,
        statements: list[IncomeStatement],
    ) -> list[IncomeStatement]:
        """获取单季度财务数据。"""

        result = []

        for statement in statements:
            statement_type = getattr(
                statement,
                "statement_type",
                None,
            )

            if cls._is_single_quarter(
                statement_type
            ):
                result.append(statement)

        return cls._sort_by_report_date(
            result
        )

    @staticmethod
    def _is_single_quarter(
        statement_type,
    ) -> bool:
        """判断是否为单季度报表。"""

        if statement_type is None:
            return False

        value = str(
            statement_type
        ).strip().lower()

        return any(
            keyword in value
            for keyword in (
                "single",
                "single_quarter",
                "quarter",
                "单季度",
                "单季",
            )
        )

    @classmethod
    def _calculate_ttm_from_cumulative(
        cls,
        statements: list[IncomeStatement],
        *,
        field: str,
        fallback_field: Optional[str] = None,
    ) -> Optional[float]:
        """通过累计财务数据计算 TTM。"""

        latest = cls._latest(statements)

        if latest is None:
            return None

        latest_date = cls._report_date(
            latest
        )

        if not latest_date:
            return None

        latest_key = cls._report_date_key(
            latest_date
        )

        if len(latest_key) != 8:
            return None

        year = latest_key[:4]
        month_day = latest_key[4:]

        # ---------------------------------------------------------
        # 年报：本身就是完整年度
        # ---------------------------------------------------------

        if month_day == "1231":
            return cls._value_with_fallback(
                latest,
                field,
                fallback_field,
            )

        # ---------------------------------------------------------
        # 本期累计 + 上年全年 - 上年同期
        # ---------------------------------------------------------

        previous_year = str(
            int(year) - 1
        )

        previous_year_end = (
            previous_year + "1231"
        )

        previous_same_period = (
            previous_year + month_day
        )

        current_value = cls._value_with_fallback(
            latest,
            field,
            fallback_field,
        )

        previous_year_value = cls._find_period_value(
            statements,
            previous_year_end,
            field,
            fallback_field,
        )

        previous_same_period_value = (
            cls._find_period_value(
                statements,
                previous_same_period,
                field,
                fallback_field,
            )
        )

        if (
            current_value is None
            or previous_year_value is None
            or previous_same_period_value is None
        ):
            return None

        return (
            current_value
            + previous_year_value
            - previous_same_period_value
        )

    @classmethod
    def _find_period_value(
        cls,
        statements,
        report_date: str,
        field: str,
        fallback_field: Optional[str] = None,
    ) -> Optional[float]:
        """根据 report_date 查找数据。"""

        target = cls._report_date_key(
            report_date
        )

        for statement in statements:
            current = cls._report_date(
                statement
            )

            if cls._report_date_key(
                current
            ) != target:
                continue

            return cls._value_with_fallback(
                statement,
                field,
                fallback_field,
            )

        return None

    # =============================================================
    # 利润增长
    # =============================================================

    @classmethod
    def _calculate_profit_growth(
        cls,
        statements: list[IncomeStatement],
    ) -> Optional[float]:
        """计算最近两个年度的净利润增长率。

        返回百分数：

            20.5

        表示 20.5%。
        """

        annuals = []

        for statement in statements:
            report_date = cls._report_date(
                statement
            )

            if not report_date:
                continue

            report_date = cls._report_date_key(
                report_date
            )

            if not report_date.endswith("1231"):
                continue

            profit = cls._net_profit(
                statement
            )

            if profit is None:
                continue

            annuals.append(
                (
                    report_date,
                    profit,
                )
            )

        annuals.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        if len(annuals) < 2:
            return None

        current_profit = annuals[0][1]
        previous_profit = annuals[1][1]

        if previous_profit == 0:
            return None

        return (
            (
                current_profit
                - previous_profit
            )
            / abs(previous_profit)
            * 100
        )

    # =============================================================
    # PEG
    # =============================================================

    @staticmethod
    def _calculate_peg(
        *,
        pe_ttm: Optional[float],
        profit_growth: Optional[float],
    ) -> Optional[float]:
        """计算 PEG。"""

        if pe_ttm is None:
            return None

        if profit_growth is None:
            return None

        if profit_growth <= 0:
            return None

        return pe_ttm / profit_growth

    # =============================================================
    # Balance Sheet
    # =============================================================

    @classmethod
    def _shareholders_equity(
        cls,
        balance_sheet: Optional[BalanceSheet],
    ) -> Optional[float]:
        """获取股东权益。"""

        if balance_sheet is None:
            return None

        value = cls._value(
            balance_sheet,
            "shareholders_equity",
        )

        if value is not None:
            return value

        return cls._value(
            balance_sheet,
            "total_equity",
        )

    @classmethod
    def _cash(
        cls,
        balance_sheet: Optional[BalanceSheet],
    ) -> Optional[float]:
        """获取现金。"""

        if balance_sheet is None:
            return None

        value = cls._value(
            balance_sheet,
            "cash",
        )

        if value is not None:
            return value

        return cls._value(
            balance_sheet,
            "cash_equivalent",
        )

    @classmethod
    def _debt(
        cls,
        balance_sheet: Optional[BalanceSheet],
    ) -> Optional[float]:
        """计算债务。"""

        if balance_sheet is None:
            return None

        total = 0.0
        found = False

        for field in (
            "short_term_debt",
            "long_term_debt",
            "bonds_payable",
        ):
            value = cls._value(
                balance_sheet,
                field,
            )

            if value is None:
                continue

            total += value
            found = True

        if not found:
            return None

        return total

    # =============================================================
    # Enterprise Value
    # =============================================================

    @staticmethod
    def _enterprise_value(
        *,
        market_cap: Optional[float],
        debt: Optional[float],
        cash: Optional[float],
    ) -> Optional[float]:
        """计算企业价值。

        EV = 市值 + 有息债务 - 现金
        """

        if market_cap is None:
            return None

        if debt is None and cash is None:
            return None

        return (
            market_cap
            + (debt or 0.0)
            - (cash or 0.0)
        )

    # =============================================================
    # 通用计算
    # =============================================================

    @staticmethod
    def _divide(
        numerator: Optional[float],
        denominator: Optional[float],
    ) -> Optional[float]:
        """安全除法。"""

        if numerator is None:
            return None

        if denominator is None:
            return None

        if denominator <= 0:
            return None

        try:
            return numerator / denominator
        except (
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):
            return None

    @staticmethod
    def _yield_from_pe(
        pe: Optional[float],
    ) -> Optional[float]:
        """根据 PE 计算盈利收益率。

        Earnings Yield = 1 / PE × 100
        """

        if pe is None:
            return None

        if pe <= 0:
            return None

        return 100 / pe

    @staticmethod
    def _round(
        value: Optional[float],
        digits: int = 2,
    ) -> Optional[float]:
        """统一保留小数位。"""

        if value is None:
            return None

        return round(
            value,
            digits,
        )