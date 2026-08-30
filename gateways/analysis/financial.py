from __future__ import annotations

from typing import Optional

from core.models.financial import (
    BalanceSheet,
    CashFlowStatement,
    Financial,
    FinancialIndicators,
    IncomeStatement,
)


class FinancialAnalyzer:
    """
    财务分析器。

    负责根据财务报表数据计算财务分析指标。

    数据来源：

        IncomeStatement
        BalanceSheet
        CashFlowStatement

    输出：

        FinancialIndicators

    注意：

        1. 不负责获取数据
        2. 不修改原始财务报表
        3. 不负责估值指标
        4. 不负责股票价格
    """

    # ==========================================================
    # Public API
    # ==========================================================

    def analyze(
        self,
        current: Financial,
        previous: Optional[Financial] = None,
    ) -> FinancialIndicators:
        """
        分析一个报告期的财务数据。

        参数：
            current:
                当前报告期财务数据。

            previous:
                上一个可比较报告期财务数据。
                用于计算同比、环比等增长指标。

        返回：
            FinancialIndicators
        """

        income = current.income
        balance = current.balance
        cash_flow = current.cash_flow

        return FinancialIndicators(

            # ==================================================
            # 盈利能力
            # ==================================================

            gross_margin=self._calculate_gross_margin(income),

            operating_margin=self._calculate_operating_margin(
                income
            ),

            net_margin=self._calculate_net_margin(
                income
            ),

            roe=self._calculate_roe(
                income,
                balance,
            ),

            roa=self._calculate_roa(
                income,
                balance,
            ),

            roic=self._calculate_roic(
                income,
                balance,
            ),

            # ==================================================
            # 成长能力
            # ==================================================

            revenue_growth=self._calculate_growth(
                income.revenue if income else None,
                (
                    previous.income.revenue
                    if previous and previous.income
                    else None
                ),
            ),

            revenue_yoy=self._calculate_growth(
                income.revenue if income else None,
                (
                    previous.income.revenue
                    if previous and previous.income
                    else None
                ),
            ),

            profit_growth=self._calculate_growth(
                income.net_profit if income else None,
                (
                    previous.income.net_profit
                    if previous and previous.income
                    else None
                ),
            ),

            net_profit_yoy=self._calculate_growth(
                income.net_profit if income else None,
                (
                    previous.income.net_profit
                    if previous and previous.income
                    else None
                ),
            ),

            # ==================================================
            # 财务健康
            # ==================================================

            debt_to_asset_ratio=self._calculate_debt_to_asset_ratio(
                balance
            ),

            current_ratio=self._calculate_current_ratio(
                balance
            ),

            quick_ratio=self._calculate_quick_ratio(
                balance
            ),

            # ==================================================
            # 营运能力
            # ==================================================

            receivable_turnover=self._calculate_receivable_turnover(
                income,
                balance,
            ),

            inventory_turnover=self._calculate_inventory_turnover(
                income,
                balance,
            ),

            # ==================================================
            # 现金流质量
            # ==================================================

            cash_flow_quality=self._calculate_cash_flow_quality(
                income,
                cash_flow,
            ),

            # ==================================================
            # 每股指标
            # ==================================================

            book_value_per_share=self._calculate_book_value_per_share(
                balance,
                current,
            ),

            operating_cash_flow_per_share=(
                self._calculate_operating_cash_flow_per_share(
                    cash_flow,
                    current,
                )
            ),
        )

    # ==========================================================
    # 盈利能力
    # ==========================================================

    @staticmethod
    def _calculate_gross_margin(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:
        """
        毛利率。

        Gross Margin =
            毛利润 / 营业收入 × 100
        """

        if income is None:
            return None

        if income.gross_profit is None:
            return None

        if income.revenue is None:
            return None

        if income.revenue == 0:
            return None

        return (
            income.gross_profit
            / income.revenue
            * 100
        )

    @staticmethod
    def _calculate_operating_margin(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:
        """
        营业利润率。

        Operating Margin =
            营业利润 / 营业收入 × 100
        """

        if income is None:
            return None

        if income.operating_profit is None:
            return None

        if income.revenue is None:
            return None

        if income.revenue == 0:
            return None

        return (
            income.operating_profit
            / income.revenue
            * 100
        )

    @staticmethod
    def _calculate_net_margin(
        income: Optional[IncomeStatement],
    ) -> Optional[float]:
        """
        净利率。

        Net Margin =
            净利润 / 营业收入 × 100
        """

        if income is None:
            return None

        if income.net_profit is None:
            return None

        if income.revenue is None:
            return None

        if income.revenue == 0:
            return None

        return (
            income.net_profit
            / income.revenue
            * 100
        )

    @staticmethod
    def _calculate_roe(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        ROE：净资产收益率。

        简化计算：

            ROE =
                净利润 / 平均股东权益 × 100

        如果没有上一期数据，则使用期末股东权益。
        """

        if income is None or balance is None:
            return None

        if income.net_profit is None:
            return None

        if balance.shareholders_equity is None:
            return None

        if balance.shareholders_equity == 0:
            return None

        return (
            income.net_profit
            / balance.shareholders_equity
            * 100
        )

    @staticmethod
    def _calculate_roa(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        ROA：总资产收益率。

        简化计算：

            ROA =
                净利润 / 总资产 × 100
        """

        if income is None or balance is None:
            return None

        if income.net_profit is None:
            return None

        if balance.total_assets is None:
            return None

        if balance.total_assets == 0:
            return None

        return (
            income.net_profit
            / balance.total_assets
            * 100
        )

    @staticmethod
    def _calculate_roic(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        ROIC：投入资本回报率。

        这里采用简化计算。

            NOPAT / Invested Capital

        由于不同数据源对投入资本定义存在差异，
        当前版本暂不强行计算。

        后续可以根据完整财务数据进一步实现。
        """

        return None

    # ==========================================================
    # 成长能力
    # ==========================================================

    @staticmethod
    def _calculate_growth(
        current: Optional[float],
        previous: Optional[float],
    ) -> Optional[float]:
        """
        计算增长率。

        Growth =
            (Current - Previous) / abs(Previous) × 100
        """

        if current is None or previous is None:
            return None

        if previous == 0:
            return None

        return (
            (current - previous)
            / abs(previous)
            * 100
        )

    # ==========================================================
    # 财务健康
    # ==========================================================

    @staticmethod
    def _calculate_debt_to_asset_ratio(
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        资产负债率。

        Debt Ratio =
            总负债 / 总资产 × 100
        """

        if balance is None:
            return None

        if balance.total_liabilities is None:
            return None

        if balance.total_assets is None:
            return None

        if balance.total_assets == 0:
            return None

        return (
            balance.total_liabilities
            / balance.total_assets
            * 100
        )

    @staticmethod
    def _calculate_current_ratio(
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        流动比率。

        Current Ratio =
            流动资产 / 流动负债
        """

        if balance is None:
            return None

        # 当前 BalanceSheet 如果还没有 current_assets，
        # 暂时无法计算。
        return None

    @staticmethod
    def _calculate_quick_ratio(
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        速动比率。

        Quick Ratio =
            (流动资产 - 存货) / 流动负债
        """

        if balance is None:
            return None

        return None

    # ==========================================================
    # 营运能力
    # ==========================================================

    @staticmethod
    def _calculate_receivable_turnover(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        应收账款周转率。

        简化：

            营业收入 / 应收账款
        """

        if income is None or balance is None:
            return None

        if income.revenue is None:
            return None

        if balance.accounts_receivable is None:
            return None

        if balance.accounts_receivable == 0:
            return None

        return (
            income.revenue
            / balance.accounts_receivable
        )

    @staticmethod
    def _calculate_inventory_turnover(
        income: Optional[IncomeStatement],
        balance: Optional[BalanceSheet],
    ) -> Optional[float]:
        """
        存货周转率。

        简化：

            营业成本 / 存货
        """

        if income is None or balance is None:
            return None

        if income.operating_cost is None:
            return None

        if balance.inventory is None:
            return None

        if balance.inventory == 0:
            return None

        return (
            income.operating_cost
            / balance.inventory
        )

    # ==========================================================
    # 现金流质量
    # ==========================================================

    @staticmethod
    def _calculate_cash_flow_quality(
        income: Optional[IncomeStatement],
        cash_flow: Optional[CashFlowStatement],
    ) -> Optional[float]:
        """
        现金流质量。

        Cash Flow Quality =
            经营活动现金流 / 净利润
        """

        if income is None or cash_flow is None:
            return None

        if income.net_profit is None:
            return None

        if cash_flow.operating_cash_flow is None:
            return None

        if income.net_profit == 0:
            return None

        return (
            cash_flow.operating_cash_flow
            / income.net_profit
        )

    # ==========================================================
    # 每股指标
    # ==========================================================

    @staticmethod
    def _calculate_book_value_per_share(
        balance: Optional[BalanceSheet],
        financial: Financial,
    ) -> Optional[float]:
        """
        每股净资产。

            股东权益 / 总股本

        当前 Financial 暂未保存总股本，
        因此无法在这里可靠计算。
        """

        return None

    @staticmethod
    def _calculate_operating_cash_flow_per_share(
        cash_flow: Optional[CashFlowStatement],
        financial: Financial,
    ) -> Optional[float]:
        """
        每股经营现金流。

            经营现金流 / 总股本

        当前 Financial 暂未保存总股本，
        因此无法在这里可靠计算。
        """

        return None