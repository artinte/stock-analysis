from __future__ import annotations

from typing import Optional

from core.models.financial.financial import Financial
from core.models.financial.income_statement import IncomeStatement
from core.models.financial.balance_sheet import BalanceSheet
from core.models.financial.cash_flow import CashFlow
from core.models.financial.financial_indicators import FinancialIndicators


class FinancialAnalyzer:
    """
    财务分析器。

    负责根据多个报告期的 Financial 数据计算财务分析指标。

    输入：

        list[Financial]

    输出：

        FinancialIndicators

    注意：

        1. 不负责获取数据
        2. 不修改原始财务报表
        3. 不负责估值指标
        4. 不负责股票价格
        5. 自己选择分析报告期
        6. 自己寻找上一季度
        7. 自己寻找去年同期
        8. 自己处理累计数据与单季度数据
        9. 自己计算同比、环比
    """

    # ==========================================================
    # 主入口
    # ==========================================================

    def analyze(
        self,
        financials: list[Financial],
        report_date: str | None = None,
    ) -> FinancialIndicators:
        """
        分析财务数据。

        参数：

            financials:
                多个报告期的 Financial 数据。

            report_date:
                指定分析报告期。

                例如：

                    "20260630"

                如果不指定：

                    使用 financials 中最新报告期。

                如果指定报告期不存在：

                    返回空的 FinancialIndicators。

        返回：

            FinancialIndicators
        """

        if not financials:
            return FinancialIndicators()

        # ======================================================
        # 清理无效数据
        # ======================================================

        financials = [financial for financial in financials if financial.report_date]

        if not financials:
            return FinancialIndicators()

        # ======================================================
        # 按报告期排序
        # ======================================================

        financials.sort(key=lambda item: item.report_date or "")

        # ======================================================
        # 确定当前分析期
        # ======================================================

        current = self._find_current(
            financials,
            report_date,
        )

        if current is None:
            return FinancialIndicators()

        # ======================================================
        # 找上一报告期
        # ======================================================

        previous_quarter = self._find_previous_period(
            financials,
            current.report_date,
        )

        # ======================================================
        # 找去年同期
        # ======================================================

        previous_year = self._find_previous_year(
            financials,
            current.report_date,
        )

        # ======================================================
        # 找上一报告期的上一报告期
        #
        # 用于：
        #
        # 2026Q1
        #
        # 需要计算：
        #
        # 2025Q4 = 2025FY - 2025Q3
        #
        # 因此需要再向前找一期。
        # ======================================================

        previous_previous_quarter = None

        if previous_quarter is not None:

            previous_previous_quarter = self._find_previous_period(
                financials,
                previous_quarter.report_date,
            )

        # ======================================================
        # 转换利润表
        #
        # 将累计数据转换成单季度数据。
        # ======================================================

        current_income = self._to_quarter_income(
            current.income,
            previous_quarter.income if previous_quarter else None,
        )

        previous_quarter_income = self._to_quarter_income(
            previous_quarter.income if previous_quarter else None,
            previous_previous_quarter.income if previous_previous_quarter else None,
        )

        previous_year_previous_quarter = None

        if previous_year is not None:

            previous_year_previous_quarter = self._find_previous_period(
                financials,
                previous_year.report_date,
            )

        previous_year_income = self._to_quarter_income(
            previous_year.income if previous_year else None,
            (
                previous_year_previous_quarter.income
                if previous_year_previous_quarter
                else None
            ),
        )

        # ======================================================
        # 转换现金流量表
        # ======================================================

        current_cash_flow = self._to_quarter_cash_flow(
            current.cash_flow,
            previous_quarter.cash_flow if previous_quarter else None,
        )

        # ======================================================
        # 盈利能力
        # ======================================================

        gross_margin = self._calculate_gross_margin(current.income)

        operating_margin = self._calculate_operating_margin(current.income)

        net_margin = self._calculate_net_margin(current.income)

        roe = self._calculate_roe(
            current.income,
            current.balance,
        )

        roa = self._calculate_roa(
            current.income,
            current.balance,
        )

        roic = self._calculate_roic(
            current.income,
            current.balance,
        )

        # ======================================================
        # 营收增长
        # ======================================================

        revenue_yoy = self._calculate_growth(
            self._get_revenue(current_income),
            self._get_revenue(previous_year_income),
        )

        revenue_qoq = self._calculate_growth(
            self._get_revenue(current_income),
            self._get_revenue(previous_quarter_income),
        )

        # ======================================================
        # 净利润增长
        # ======================================================

        profit_yoy = self._calculate_growth(
            self._get_profit(current_income),
            self._get_profit(previous_year_income),
        )

        profit_qoq = self._calculate_growth(
            self._get_profit(current_income),
            self._get_profit(previous_quarter_income),
        )

        # ======================================================
        # EPS 增长
        #
        # 累计 EPS 不能简单相减。
        #
        # 当前模型没有可靠的季度 EPS 计算所需股本数据，
        # 因此暂时只计算同比。
        # ======================================================

        eps_yoy = self._calculate_growth(
            self._get_eps(current_income),
            self._get_eps(previous_year_income),
        )

        # ======================================================
        # 财务健康
        # ======================================================

        debt_to_asset_ratio = self._calculate_debt_to_asset_ratio(current.balance)

        current_ratio = self._calculate_current_ratio(current.balance)

        quick_ratio = self._calculate_quick_ratio(current.balance)

        interest_coverage = self._calculate_interest_coverage(current.income)

        # ======================================================
        # 营运能力
        # ======================================================

        receivable_turnover = self._calculate_receivable_turnover(
            current_income,
            current.balance,
        )

        inventory_turnover = self._calculate_inventory_turnover(
            current_income,
            current.balance,
        )

        # ======================================================
        # 现金流质量
        # ======================================================

        cash_flow_quality = self._calculate_cash_flow_quality(
            current_cash_flow,
            current_income,
        )

        # ======================================================
        # 每股指标
        # ======================================================

        book_value_per_share = self._calculate_book_value_per_share(current.balance)

        operating_cash_flow_per_share = self._calculate_operating_cash_flow_per_share(
            current_cash_flow
        )

        # ======================================================
        # 返回结果
        # ======================================================

        return FinancialIndicators(
            # ==================================================
            # 盈利能力
            # ==================================================
            gross_margin=gross_margin,
            operating_margin=operating_margin,
            net_margin=net_margin,
            roe=roe,
            roa=roa,
            roic=roic,
            # ==================================================
            # 成长能力
            # ==================================================
            revenue_growth=revenue_yoy,
            revenue_yoy=revenue_yoy,
            revenue_qoq=revenue_qoq,
            profit_growth=profit_yoy,
            net_profit_yoy=profit_yoy,
            net_profit_qoq=profit_qoq,
            eps_growth=eps_yoy,

            # ==================================================
            # 财务健康
            # ==================================================
            debt_to_asset_ratio=debt_to_asset_ratio,
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            interest_coverage=interest_coverage,
            # ==================================================
            # 营运能力
            # ==================================================
            receivable_turnover=receivable_turnover,
            inventory_turnover=inventory_turnover,
            # ==================================================
            # 现金流质量
            # ==================================================
            cash_flow_quality=cash_flow_quality,
            # ==================================================
            # 每股指标
            # ==================================================
            book_value_per_share=book_value_per_share,
            operating_cash_flow_per_share=(operating_cash_flow_per_share),
        )

    # ==========================================================
    # 当前报告期
    # ==========================================================

    @staticmethod
    def _find_current(
        financials: list[Financial],
        report_date: str | None,
    ) -> Optional[Financial]:

        # 未指定报告期
        # 使用最新报告期
        if report_date is None:
            return financials[-1]

        # 指定报告期
        for financial in financials:

            if financial.report_date == report_date:
                return financial

        # 指定报告期不存在
        return None

    # ==========================================================
    # 上一个报告期
    # ==========================================================

    @staticmethod
    def _find_previous_period(
        financials: list[Financial],
        report_date: str | None,
    ) -> Optional[Financial]:

        if not report_date:
            return None

        previous = None

        for financial in financials:

            if not financial.report_date:
                continue

            if financial.report_date >= report_date:
                break

            previous = financial

        return previous

    # ==========================================================
    # 去年同期
    # ==========================================================

    @staticmethod
    def _find_previous_year(
        financials: list[Financial],
        report_date: str | None,
    ) -> Optional[Financial]:

        if not report_date:
            return None

        if len(report_date) != 8:
            return None

        try:
            year = int(report_date[:4])
        except ValueError:
            return None

        target_date = f"{year - 1}{report_date[4:]}"

        for financial in financials:

            if financial.report_date == target_date:
                return financial

        return None

    # ==========================================================
    # 累计利润表 → 单季度利润表
    # ==========================================================

    def _to_quarter_income(
        self,
        current: Optional[IncomeStatement],
        previous: Optional[IncomeStatement],
    ) -> Optional[IncomeStatement]:

        if current is None:
            return None

        # Q1 累计值就是单季度值
        if self._is_q1(current.report_date):
            return current

        # 没有上一期
        if previous is None:
            return current

        return self._subtract_income(
            current,
            previous,
        )

    # ==========================================================
    # 利润表相减
    # ==========================================================

    def _subtract_income(
        self,
        current: IncomeStatement,
        previous: IncomeStatement,
    ) -> IncomeStatement:

        return IncomeStatement(
            symbol=current.symbol,
            report_date=current.report_date,
            report_type=current.report_type,
            statement_type=current.statement_type,
            announcement_date=current.announcement_date,
            currency=current.currency,
            revenue=self._subtract(
                current.revenue,
                previous.revenue,
            ),
            total_operating_income=self._subtract(
                current.total_operating_income,
                previous.total_operating_income,
            ),
            operating_cost=self._subtract(
                current.operating_cost,
                previous.operating_cost,
            ),
            total_operating_cost=self._subtract(
                current.total_operating_cost,
                previous.total_operating_cost,
            ),
            selling_expense=self._subtract(
                current.selling_expense,
                previous.selling_expense,
            ),
            administrative_expense=self._subtract(
                current.administrative_expense,
                previous.administrative_expense,
            ),
            financial_expense=self._subtract(
                current.financial_expense,
                previous.financial_expense,
            ),
            rd_expense=self._subtract(
                current.rd_expense,
                previous.rd_expense,
            ),
            business_tax_and_surcharge=self._subtract(
                current.business_tax_and_surcharge,
                previous.business_tax_and_surcharge,
            ),
            asset_impairment_loss=self._subtract(
                current.asset_impairment_loss,
                previous.asset_impairment_loss,
            ),
            credit_impairment_loss=self._subtract(
                current.credit_impairment_loss,
                previous.credit_impairment_loss,
            ),
            investment_income=self._subtract(
                current.investment_income,
                previous.investment_income,
            ),
            fair_value_change_income=self._subtract(
                current.fair_value_change_income,
                previous.fair_value_change_income,
            ),
            exchange_income=self._subtract(
                current.exchange_income,
                previous.exchange_income,
            ),
            other_income=self._subtract(
                current.other_income,
                previous.other_income,
            ),
            gross_profit=self._subtract(
                current.gross_profit,
                previous.gross_profit,
            ),
            operating_profit=self._subtract(
                current.operating_profit,
                previous.operating_profit,
            ),
            total_profit=self._subtract(
                current.total_profit,
                previous.total_profit,
            ),
            income_tax=self._subtract(
                current.income_tax,
                previous.income_tax,
            ),
            net_profit=self._subtract(
                current.net_profit,
                previous.net_profit,
            ),
            net_profit_attributable=self._subtract(
                current.net_profit_attributable,
                previous.net_profit_attributable,
            ),
            non_recurring_net_profit=self._subtract(
                current.non_recurring_net_profit,
                previous.non_recurring_net_profit,
            ),
            non_operating_income=self._subtract(
                current.non_operating_income,
                previous.non_operating_income,
            ),
            non_operating_expense=self._subtract(
                current.non_operating_expense,
                previous.non_operating_expense,
            ),
            other_comprehensive_income=self._subtract(
                current.other_comprehensive_income,
                previous.other_comprehensive_income,
            ),
            ebit=self._subtract(
                current.ebit,
                previous.ebit,
            ),
            ebitda=self._subtract(
                current.ebitda,
                previous.ebitda,
            ),
            # 累计 EPS 不能直接相减
            eps=None,
            diluted_eps=None,
        )

    # ==========================================================
    # 累计现金流 → 单季度现金流
    # ==========================================================

    def _to_quarter_cash_flow(
        self,
        current: Optional[CashFlow],
        previous: Optional[CashFlow],
    ) -> Optional[CashFlow]:

        if current is None:
            return None

        # Q1
        if self._is_q1(current.report_date):
            return current

        if previous is None:
            return current

        return self._subtract_cash_flow(
            current,
            previous,
        )

    # ==========================================================
    # 现金流相减
    # ==========================================================

    def _subtract_cash_flow(
        self,
        current: CashFlow,
        previous: CashFlow,
    ) -> CashFlow:

        return CashFlow(
            symbol=current.symbol,
            report_date=current.report_date,
            report_type=current.report_type,
            statement_type=current.statement_type,
            announcement_date=current.announcement_date,
            currency=current.currency,
            operating_cash_flow=self._subtract(
                current.operating_cash_flow,
                previous.operating_cash_flow,
            ),
            cash_flow_from_operations=self._subtract(
                current.cash_flow_from_operations,
                previous.cash_flow_from_operations,
            ),
            operating_cash_inflow=self._subtract(
                current.operating_cash_inflow,
                previous.operating_cash_inflow,
            ),
            operating_cash_outflow=self._subtract(
                current.operating_cash_outflow,
                previous.operating_cash_outflow,
            ),
            cash_received_from_sales=self._subtract(
                current.cash_received_from_sales,
                previous.cash_received_from_sales,
            ),
            cash_paid_for_goods=self._subtract(
                current.cash_paid_for_goods,
                previous.cash_paid_for_goods,
            ),
            cash_paid_to_employees=self._subtract(
                current.cash_paid_to_employees,
                previous.cash_paid_to_employees,
            ),
            taxes_paid=self._subtract(
                current.taxes_paid,
                previous.taxes_paid,
            ),
            tax_refund_received=self._subtract(
                current.tax_refund_received,
                previous.tax_refund_received,
            ),
            investing_cash_flow=self._subtract(
                current.investing_cash_flow,
                previous.investing_cash_flow,
            ),
            investing_cash_inflow=self._subtract(
                current.investing_cash_inflow,
                previous.investing_cash_inflow,
            ),
            investing_cash_outflow=self._subtract(
                current.investing_cash_outflow,
                previous.investing_cash_outflow,
            ),
            capital_expenditure=self._subtract(
                current.capital_expenditure,
                previous.capital_expenditure,
            ),
            cash_received_from_investments=self._subtract(
                current.cash_received_from_investments,
                previous.cash_received_from_investments,
            ),
            investment_income_received=self._subtract(
                current.investment_income_received,
                previous.investment_income_received,
            ),
            financing_cash_flow=self._subtract(
                current.financing_cash_flow,
                previous.financing_cash_flow,
            ),
            financing_cash_inflow=self._subtract(
                current.financing_cash_inflow,
                previous.financing_cash_inflow,
            ),
            financing_cash_outflow=self._subtract(
                current.financing_cash_outflow,
                previous.financing_cash_outflow,
            ),
            cash_received_from_borrowings=self._subtract(
                current.cash_received_from_borrowings,
                previous.cash_received_from_borrowings,
            ),
            cash_paid_for_debt=self._subtract(
                current.cash_paid_for_debt,
                previous.cash_paid_for_debt,
            ),
            dividends_interest_paid=self._subtract(
                current.dividends_interest_paid,
                previous.dividends_interest_paid,
            ),
            cash_from_equity_investment=self._subtract(
                current.cash_from_equity_investment,
                previous.cash_from_equity_investment,
            ),
            beginning_cash_balance=previous.ending_cash_balance,
            ending_cash_balance=current.ending_cash_balance,
            net_change_in_cash=self._subtract(
                current.net_change_in_cash,
                previous.net_change_in_cash,
            ),
            exchange_rate_effect=self._subtract(
                current.exchange_rate_effect,
                previous.exchange_rate_effect,
            ),
            free_cash_flow=self._subtract(
                current.free_cash_flow,
                previous.free_cash_flow,
            ),
            fcff=None,
            fcfe=None,
        )

    # ==========================================================
    # 盈利能力
    # ==========================================================

    @staticmethod
    def _calculate_gross_margin(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if income is None:
            return None

        return FinancialAnalyzer._divide_percent(
            income.gross_profit,
            income.revenue,
        )

    @staticmethod
    def _calculate_operating_margin(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if income is None:
            return None

        return FinancialAnalyzer._divide_percent(
            income.operating_profit,
            income.revenue,
        )

    @staticmethod
    def _calculate_net_margin(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if income is None:
            return None

        profit = FinancialAnalyzer._get_profit(income)

        return FinancialAnalyzer._divide_percent(
            profit,
            income.revenue,
        )

    # ==========================================================
    # ROE
    # ==========================================================

    @staticmethod
    def _calculate_roe(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if income is None or balance is None:
            return None

        profit = FinancialAnalyzer._get_profit(income)

        return FinancialAnalyzer._divide_percent(
            profit,
            balance.shareholders_equity,
        )

    # ==========================================================
    # ROA
    # ==========================================================

    @staticmethod
    def _calculate_roa(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if income is None or balance is None:
            return None

        profit = FinancialAnalyzer._get_profit(income)

        return FinancialAnalyzer._divide_percent(
            profit,
            balance.total_assets,
        )

    # ==========================================================
    # ROIC
    # ==========================================================

    @staticmethod
    def _calculate_roic(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if income is None or balance is None:
            return None

        if income.ebit is None:
            return None

        if (
            income.income_tax is None
            or income.total_profit is None
            or income.total_profit <= 0
        ):
            return None

        tax_rate = income.income_tax / income.total_profit

        tax_rate = max(
            0.0,
            min(tax_rate, 1.0),
        )

        nopat = income.ebit * (1 - tax_rate)

        equity = (
            balance.shareholders_equity
            if balance.shareholders_equity is not None
            else balance.total_equity
        )

        if equity is None:
            return None

        invested_capital = (
            equity
            + (balance.short_term_debt or 0)
            + (balance.long_term_debt or 0)
            - (balance.cash or 0)
        )

        if invested_capital <= 0:
            return None

        return nopat / invested_capital * 100

    # ==========================================================
    # 财务健康
    # ==========================================================

    @staticmethod
    def _calculate_debt_to_asset_ratio(
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if balance is None:
            return None

        return FinancialAnalyzer._divide_percent(
            balance.total_liabilities,
            balance.total_assets,
        )

    @staticmethod
    def _calculate_current_ratio(
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if balance is None:
            return None

        return FinancialAnalyzer._divide(
            balance.current_assets,
            balance.current_liabilities,
        )

    @staticmethod
    def _calculate_quick_ratio(
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if balance is None:
            return None

        if (
            balance.current_assets is None
            or balance.inventory is None
            or balance.current_liabilities in (None, 0)
        ):
            return None

        return (
            balance.current_assets - balance.inventory
        ) / balance.current_liabilities

    @staticmethod
    def _calculate_interest_coverage(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if income is None:
            return None

        if income.ebit is None or income.financial_expense in (None, 0):
            return None

        return income.ebit / abs(income.financial_expense)

    # ==========================================================
    # 营运能力
    # ==========================================================

    @staticmethod
    def _calculate_receivable_turnover(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if income is None or balance is None:
            return None

        if balance.accounts_receivable in (None, 0):
            return None

        return income.revenue / balance.accounts_receivable

    @staticmethod
    def _calculate_inventory_turnover(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        if income is None or balance is None:
            return None

        if income.operating_cost is None or balance.inventory in (None, 0):
            return None

        return income.operating_cost / balance.inventory

    # ==========================================================
    # 现金流质量
    # ==========================================================

    @staticmethod
    def _calculate_cash_flow_quality(
        cash_flow: Optional[CashFlow],
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if cash_flow is None or income is None:
            return None

        if cash_flow.operating_cash_flow is None:
            return None

        profit = FinancialAnalyzer._get_profit(income)

        if profit in (None, 0):
            return None

        return cash_flow.operating_cash_flow / profit

    # ==========================================================
    # 每股净资产
    # ==========================================================

    @staticmethod
    def _calculate_book_value_per_share(
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:

        # 当前 BalanceSheet 没有可靠的总股数。
        return None

    # ==========================================================
    # 每股经营现金流
    # ==========================================================

    @staticmethod
    def _calculate_operating_cash_flow_per_share(
        cash_flow: Optional[CashFlow],
    ) -> Optional[float]:

        # 当前 CashFlow 没有可靠的总股数。
        return None

    # ==========================================================
    # 数据读取
    # ==========================================================

    @staticmethod
    def _get_revenue(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if income is None:
            return None

        return income.revenue

    @staticmethod
    def _get_profit(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if income is None:
            return None

        if income.net_profit_attributable is not None:
            return income.net_profit_attributable

        return income.net_profit

    @staticmethod
    def _get_eps(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:

        if income is None:
            return None

        return income.eps

    # ==========================================================
    # 数学工具
    # ==========================================================

    @staticmethod
    def _calculate_growth(
        current: Optional[float],
        previous: Optional[float],
    ) -> Optional[float]:

        if current is None or previous is None:
            return None

        if previous == 0:
            return None

        return (current - previous) / abs(previous) * 100

    @staticmethod
    def _subtract(
        current: Optional[float],
        previous: Optional[float],
    ) -> Optional[float]:

        if current is None or previous is None:
            return None

        return current - previous

    @staticmethod
    def _divide(
        numerator: Optional[float],
        denominator: Optional[float],
    ) -> Optional[float]:

        if numerator is None or denominator in (None, 0):
            return None

        return numerator / denominator

    @staticmethod
    def _divide_percent(
        numerator: Optional[float],
        denominator: Optional[float],
    ) -> Optional[float]:

        if numerator is None or denominator in (None, 0):
            return None

        return numerator / denominator * 100

    # ==========================================================
    # Q1 判断
    # ==========================================================

    @staticmethod
    def _is_q1(
        report_date: Optional[str],
    ) -> bool:

        if not report_date:
            return False

        return report_date.endswith("0331")
