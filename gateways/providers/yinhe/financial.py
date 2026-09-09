from typing import Any

import pandas

from core.models.financial.financial import Financial
from core.models.financial.income_statement import IncomeStatement
from core.models.financial.balance_sheet import BalanceSheet
from core.models.financial.cash_flow import CashFlow
from gateways.analysis.financial_analyzer import FinancialAnalyzer
from utils.stock_mapping import normalize_symbol


class YinheFinancial:
    """
    银河证券财务数据适配。
    """

    def __init__(self, gateway):
        """
        保存主网关引用。

        可以访问：

            gateway.info_data
            gateway.calendar
            gateway.local_path

        """

        self.gateway = gateway

        self.financial_analyzer = FinancialAnalyzer()

    def fetch_balance_sheet(
        self,
        symbol: str,
        start_year: int | None = None,
        start_quarter: int | None = None,
        end_year: int | None = None,
        end_quarter: int | None = None,
    ) -> list[BalanceSheet]:
        return self.fetch_balance_sheets(
            [symbol],
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        ).get(symbol, [])

    def fetch_cash_flow(
        self,
        symbol: str,
        start_year: int | None = None,
        start_quarter: int | None = None,
        end_year: int | None = None,
        end_quarter: int | None = None,
    ) -> list[CashFlow]:
        return self.fetch_cash_flows(
            [symbol],
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        ).get(symbol, [])

    def fetch_income_statement(
        self,
        symbol: str,
        start_year: int | None = None,
        start_quarter: int | None = None,
        end_year: int | None = None,
        end_quarter: int | None = None,
    ) -> list[IncomeStatement]:
        """
        获取银河利润表数据。

        将银河证券返回的利润表 DataFrame
        转换为统一 IncomeStatement 模型。

        数据流：

            AmazingData
                |
                ↓
            DataFrame
                |
                ↓
            IncomeStatement
        参数：
            symbols: 股票代码列表
            start_year: 起始报告年度
            start_quarter: 起始报告季度
            end_year: 结束报告年度
            end_quarter: 结束报告季度
        返回：
            符合查询条件的利润表数据列表。
            如果没有匹配数据，则返回空列表。
        """
        return self.fetch_income_statements(
            [symbol],
            start_year,
            start_quarter,
            end_year,
            end_quarter,
        ).get(symbol, [])

    def fetch_balance_sheets(
        self,
        symbols: list[str],
        start_year: int | None = None,
        start_quarter: int | None = None,
        end_year: int | None = None,
        end_quarter: int | None = None,
    ) -> dict[str, list[BalanceSheet]]:

        balance_sheets: dict[str, list[BalanceSheet]] = {}

        try:
            # ======================================================
            # 获取银河指定股票列表的上市公司的资产负债表数据
            # 本地保存全量历史数据，且每次调用接口默认增量更新本地数据，从而加速接口读取速度
            # ======================================================

            result = self.gateway.info_data.get_balance_sheet(
                symbols,
                local_path=self.gateway.local_path,
                is_local=True,
            )

            if not result:
                print(f"[银河] 未获取到资产负债表数据: {symbols}")
                return {}

            for symbol in symbols:

                # ======================================================
                # 获取当前股票 DataFrame
                # ======================================================

                df = result.get(symbol)

                if df is None:
                    print(f"[银河] 未找到股票资产负债表: {symbol}")
                    continue

                if df.empty:
                    print(f"[银河] 资产负债表为空: {symbol}")
                    continue

                if "REPORTING_PERIOD" not in df.columns:
                    print(f"[银河] 资产负债表缺少 REPORTING_PERIOD: " f"{symbol}")
                    continue

                # ======================================================
                # 根据报告期筛选
                # ======================================================

                selected_rows = []

                for _, row in df.iterrows():

                    statement_type = row.get("STATEMENT_TYPE")

                    # --------------------------------------------------
                    # 只使用合并报表
                    # --------------------------------------------------

                    if statement_type != "1":
                        continue

                    report_date = str(row.get("REPORTING_PERIOD"))

                    if not report_date:
                        continue

                    report_year, report_quarter = self._parse_report_period(report_date)

                    # --------------------------------------------------
                    # 起始报告期
                    # --------------------------------------------------

                    if start_year is not None:
                        if self._quarter_index(
                            report_year,
                            report_quarter,
                        ) < self._quarter_index(
                            start_year,
                            start_quarter,
                        ):
                            continue

                    # --------------------------------------------------
                    # 结束报告期
                    # --------------------------------------------------

                    if end_year is not None:
                        if self._quarter_index(
                            report_year,
                            report_quarter,
                        ) > self._quarter_index(
                            end_year,
                            end_quarter,
                        ):
                            continue

                    selected_rows.append(row)

                if not selected_rows:
                    continue

                # ======================================================
                # 转换为标准 BalanceSheet
                # ======================================================

                symbol_balance_sheets: list[BalanceSheet] = []

                for row in selected_rows:

                    symbol_balance_sheets.append(
                        BalanceSheet(
                            # ==================================================
                            # 基础信息
                            # ==================================================
                            symbol=symbol,
                            report_date=self._to_str(row.get("REPORTING_PERIOD")),
                            report_type=self._to_str(row.get("REPORT_TYPE")),
                            statement_type=self._to_str(row.get("STATEMENT_TYPE")),
                            announcement_date=self._to_str(row.get("ANN_DATE")),
                            currency=self._to_str(row.get("CURRENCY_CODE")),
                            # ==================================================
                            # 资产
                            # ==================================================
                            total_assets=self._to_float(row.get("TOTAL_ASSETS")),
                            current_assets=self._to_float(row.get("TOTAL_CUR_ASSETS")),
                            non_current_assets=self._to_float(
                                row.get("TOT_NONCUR_ASSETS")
                            ),
                            cash=self._to_float(row.get("CURRENCY_CAP")),
                            accounts_receivable=self._to_float(
                                row.get("ACCT_RECEIVABLE")
                            ),
                            inventory=self._to_float(row.get("INV")),
                            fixed_assets=self._to_float(row.get("FIXED_ASSETS")),
                            construction_in_progress=self._to_float(
                                row.get("CONST_IN_PROC")
                            ),
                            intangible_assets=self._to_float(
                                row.get("INTANGIBLE_ASSETS")
                            ),
                            goodwill=self._to_float(row.get("GOODWILL")),
                            long_term_equity_investment=self._to_float(
                                row.get("LT_EQUITY_INV")
                            ),
                            investment_real_estate=self._to_float(
                                row.get("INV_REALESTATE")
                            ),
                            right_of_use_assets=self._to_float(
                                row.get("USE_RIGHT_ASSETS")
                            ),
                            # ==================================================
                            # 负债
                            # ==================================================
                            total_liabilities=self._to_float(row.get("TOTAL_LIAB")),
                            current_liabilities=self._to_float(
                                row.get("TOTAL_CUR_LIAB")
                            ),
                            non_current_liabilities=self._to_float(
                                row.get("TOTAL_NONCUR_LIAB")
                            ),
                            short_term_debt=self._to_float(row.get("ST_BORROWING")),
                            long_term_debt=self._to_float(row.get("LT_LOAN")),
                            accounts_payable=self._to_float(row.get("ACCT_PAYABLE")),
                            notes_payable=self._to_float(row.get("NOTES_PAYABLE")),
                            bonds_payable=self._to_float(row.get("BONDS_PAYABLE")),
                            lease_liability=self._to_float(row.get("LEASE_LIABILITY")),
                            tax_payable=self._to_float(row.get("TAX_PAYABLE")),
                            dividends_payable=self._to_float(row.get("DIV_PAYABLE")),
                            # ==================================================
                            # 所有者权益
                            # ==================================================
                            total_equity=self._to_float(
                                row.get("TOT_SHARE_EQUITY_INCL_MIN_INT")
                            ),
                            shareholders_equity=self._to_float(
                                row.get("TOT_SHARE_EQUITY_EXCL_MIN_INT")
                            ),
                            minority_interest=self._to_float(
                                row.get("MINORITY_EQUITY")
                            ),
                            share_capital=self._to_float(row.get("CAP_STOCK")),
                            capital_reserve=self._to_float(row.get("CAP_RESV")),
                            surplus_reserve=self._to_float(row.get("SURPLUS_RESV")),
                            undistributed_profit=self._to_float(
                                row.get("UNDISTRIBUTED_PRO")
                            ),
                            treasury_stock=self._to_float(row.get("LESS_TREASURY_STK")),
                        )
                    )

                # ======================================================
                # 按报告期升序排列
                # ======================================================

                symbol_balance_sheets.sort(key=lambda item: item.report_date or "")

                balance_sheets[symbol] = symbol_balance_sheets

            return balance_sheets

        except SystemExit as exc:
            print(f"[银河] get_balance_sheet 调用了 exit(): " f"{exc}")
            return {}

        except BaseException as exc:
            print(f"[银河] get_balance_sheet 异常: " f"{type(exc).__name__}: {exc}")
            return {}

    def fetch_cash_flows(
        self,
        symbols: list[str],
        start_year: int | None = None,
        start_quarter: int | None = None,
        end_year: int | None = None,
        end_quarter: int | None = None,
    ) -> dict[str, list[CashFlow]]:

        cash_flows: dict[str, list[CashFlow]] = {}

        try:
            # ======================================================
            # 获取银河指定股票列表的上市公司的现金流量表数据
            # 本地保存全量历史数据，且每次调用接口默认增量更新本地数据，从而加速接口读取速度
            # ======================================================

            result = self.gateway.info_data.get_cash_flow(
                symbols,
                local_path=self.gateway.local_path,
                is_local=True,
            )

            if not result:
                print(f"[银河] 未获取到现金流量表数据: {symbols}")
                return {}

            for symbol in symbols:

                # ======================================================
                # 获取当前股票 DataFrame
                # ======================================================

                df = result.get(symbol)

                if df is None:
                    print(f"[银河] 未找到股票现金流量表: {symbol}")
                    continue

                if df.empty:
                    print(f"[银河] 现金流量表为空: {symbol}")
                    continue

                if "REPORTING_PERIOD" not in df.columns:
                    print(f"[银河] 现金流量表缺少 REPORTING_PERIOD: " f"{symbol}")
                    continue

                # ======================================================
                # 根据报告期筛选
                # ======================================================

                selected_rows = []

                for _, row in df.iterrows():

                    statement_type = row.get("STATEMENT_TYPE")

                    # --------------------------------------------------
                    # 只使用合并报表
                    # --------------------------------------------------

                    if statement_type != "1":
                        continue

                    report_date = str(row.get("REPORTING_PERIOD"))

                    if not report_date:
                        continue

                    report_year, report_quarter = self._parse_report_period(report_date)

                    # --------------------------------------------------
                    # 起始报告期
                    # --------------------------------------------------

                    if start_year is not None:
                        if self._quarter_index(
                            report_year,
                            report_quarter,
                        ) < self._quarter_index(
                            start_year,
                            start_quarter,
                        ):
                            continue

                    # --------------------------------------------------
                    # 结束报告期
                    # --------------------------------------------------

                    if end_year is not None:
                        if self._quarter_index(
                            report_year,
                            report_quarter,
                        ) > self._quarter_index(
                            end_year,
                            end_quarter,
                        ):
                            continue

                    selected_rows.append(row)

                if not selected_rows:
                    continue

                # ======================================================
                # 转换为标准 CashFlow
                # ======================================================

                symbol_cash_flows: list[CashFlow] = []

                for row in selected_rows:

                    symbol_cash_flows.append(
                        CashFlow(
                            # ==================================================
                            # 基础信息
                            # ==================================================
                            symbol=symbol,
                            report_date=self._to_str(row.get("REPORTING_PERIOD")),
                            report_type=self._to_str(row.get("REPORT_TYPE")),
                            statement_type=self._to_str(row.get("STATEMENT_TYPE")),
                            announcement_date=self._to_str(row.get("ANN_DATE")),
                            currency=self._to_str(row.get("CURRENCY_CODE")),
                            # ==================================================
                            # 经营活动
                            # ==================================================
                            operating_cash_flow=self._to_float(
                                row.get("NET_CASH_FLOWS_OPERA_ACT")
                            ),
                            cash_flow_from_operations=self._to_float(
                                row.get("IND_NET_CASH_FLOWS_OPERA_ACT")
                            ),
                            operating_cash_inflow=self._to_float(
                                row.get("TOT_CASH_INFLOW_OPER_ACT")
                            ),
                            operating_cash_outflow=self._to_float(
                                row.get("TOT_CASH_OUTFLOW_OPERA_ACT")
                            ),
                            cash_received_from_sales=self._to_float(
                                row.get("CASH_RECP_SG_AND_RS")
                            ),
                            cash_paid_for_goods=self._to_float(
                                row.get("CASH_PAY_GOODS_SERVICES")
                            ),
                            cash_paid_to_employees=self._to_float(
                                row.get("CASH_PAY_EMPLOYEE")
                            ),
                            taxes_paid=self._to_float(row.get("PAY_ALL_TAX")),
                            tax_refund_received=self._to_float(
                                row.get("RECP_TAX_REFUND")
                            ),
                            # ==================================================
                            # 投资活动
                            # ==================================================
                            investing_cash_flow=self._to_float(
                                row.get("NET_CASH_FLOWS_INV_ACT")
                            ),
                            investing_cash_inflow=self._to_float(
                                row.get("TOT_CASH_INFLOW_INV_ACT")
                            ),
                            investing_cash_outflow=self._to_float(
                                row.get("TOT_CASH_OUTFLOW_INV_ACT")
                            ),
                            capital_expenditure=self._to_float(
                                row.get("CASH_PAID_PUR_CONST_FIOLTA")
                            ),
                            cash_received_from_investments=self._to_float(
                                row.get("CASH_RECP_RECOV_INV")
                            ),
                            investment_income_received=self._to_float(
                                row.get("CASH_RECP_INV_INCOME")
                            ),
                            # ==================================================
                            # 筹资活动
                            # ==================================================
                            financing_cash_flow=self._to_float(
                                row.get("NET_CASH_FLOWS_FIN_ACT")
                            ),
                            financing_cash_inflow=self._to_float(
                                row.get("TOT_CASH_INFLOW_FIN_ACT")
                            ),
                            financing_cash_outflow=self._to_float(
                                row.get("TOT_CASH_OUTFLOW_FIN_ACT")
                            ),
                            cash_received_from_borrowings=self._to_float(
                                row.get("CASH_RECE_BORROW")
                            ),
                            cash_paid_for_debt=self._to_float(
                                row.get("CASH_PAY_FOR_DEBT")
                            ),
                            dividends_interest_paid=self._to_float(
                                row.get("CASH_PAY_DIST_DIV_PRO_INT")
                            ),
                            cash_from_equity_investment=self._to_float(
                                row.get("ABSORB_CASH_RECP_INV")
                            ),
                            # ==================================================
                            # 现金及现金等价物
                            # ==================================================
                            beginning_cash_balance=self._to_float(
                                row.get("BEG_BAL_CASH_CASH_EQU")
                            ),
                            ending_cash_balance=self._to_float(
                                row.get("END_BAL_CASH_CASH_EQU")
                            ),
                            net_change_in_cash=self._to_float(
                                row.get("NET_INCR_CASH_AND_CASH_EQU")
                            ),
                            exchange_rate_effect=self._to_float(
                                row.get("EFF_FX_FLUC_CASH")
                            ),
                            # ==================================================
                            # 自由现金流
                            # ==================================================
                            free_cash_flow=self._to_float(row.get("FREE_CASH_FLOW")),
                        )
                    )

                # ======================================================
                # 按报告期升序排列
                # ======================================================

                symbol_cash_flows.sort(key=lambda item: item.report_date or "")

                cash_flows[symbol] = symbol_cash_flows

            return cash_flows

        except Exception as exc:
            print(f"[银河] 获取现金流量表失败 " f"{symbols}: {exc}")
            return {}

    def fetch_income_statements(
        self,
        symbols: list[str],
        start_year: int | None = None,
        start_quarter: int | None = None,
        end_year: int | None = None,
        end_quarter: int | None = None,
    ) -> dict[str, list[IncomeStatement]]:

        statements: dict[str, list[IncomeStatement]] = {}

        try:
            # ======================================================
            # 获取银河指定股票列表的上市公司的利润表数据
            # 本地保存全量历史数据，且每次调用接口默认增量更新本地数据，从而加速接口读取速度
            # ======================================================

            result = self.gateway.info_data.get_income(
                symbols,
                local_path=self.gateway.local_path,
                is_local=True,
            )

            if not result:
                print(f"[银河] 未获取到利润表数据: {symbols}")
                return {}

            for symbol in symbols:

                # ======================================================
                # 获取当前股票 DataFrame
                # ======================================================

                df = result.get(symbol)

                if df is None:
                    print(f"[银河] 未找到股票利润表: {symbol}")
                    continue

                if df.empty:
                    print(f"[银河] 利润表为空: {symbol}")
                    continue

                if "REPORTING_PERIOD" not in df.columns:
                    print(f"[银河] 利润表缺少 REPORTING_PERIOD: " f"{symbol}")
                    continue

                # ======================================================
                # 根据报告期筛选
                # ======================================================

                selected_rows = []

                for _, row in df.iterrows():
                    statement_type = row.get("STATEMENT_TYPE")
                    if statement_type != "1":
                        continue

                    report_date = str(row.get("REPORTING_PERIOD"))
                    if not report_date:
                        continue

                    report_year, report_quarter = self._parse_report_period(report_date)

                    # --------------------------------------------------
                    # 起始报告期
                    # --------------------------------------------------

                    if start_year is not None:
                        if self._quarter_index(
                            report_year,
                            report_quarter,
                        ) < self._quarter_index(
                            start_year,
                            start_quarter,
                        ):
                            continue

                    # --------------------------------------------------
                    # 结束报告期
                    # --------------------------------------------------

                    if end_year is not None:
                        if self._quarter_index(
                            report_year,
                            report_quarter,
                        ) > self._quarter_index(
                            end_year,
                            end_quarter,
                        ):
                            continue

                    selected_rows.append(row)

                if not selected_rows:
                    continue

                # ======================================================
                # 转换为标准 IncomeStatement
                # ======================================================

                symbol_statements: list[IncomeStatement] = []

                for row in selected_rows:
                    symbol_statements.append(
                        IncomeStatement(
                            # ==================================================
                            # 基础信息
                            # ==================================================
                            symbol=symbol,
                            report_date=self._to_str(row.get("REPORTING_PERIOD")),
                            report_type=self._to_str(row.get("REPORT_TYPE")),
                            statement_type=self._to_str(row.get("STATEMENT_TYPE")),
                            announcement_date=self._to_str(row.get("ANN_DATE")),
                            currency=self._to_str(row.get("CURRENCY_CODE")),
                            # ==================================================
                            # 收入
                            # ==================================================
                            revenue=self._to_float(row.get("OPERA_REV")),
                            total_operating_income=self._to_float(
                                row.get("TOT_OPERA_REV")
                            ),
                            # ==================================================
                            # 成本费用
                            # ==================================================
                            operating_cost=self._to_float(row.get("LESS_OPERA_COST")),
                            total_operating_cost=self._to_float(
                                row.get("TOT_OPERA_COST")
                            ),
                            selling_expense=self._to_float(row.get("LESS_SELLING_EXP")),
                            administrative_expense=self._to_float(
                                row.get("LESS_ADMIN_EXP")
                            ),
                            financial_expense=self._to_float(row.get("LESS_FIN_EXP")),
                            rd_expense=self._to_float(row.get("RD_EXP")),
                            business_tax_and_surcharge=self._to_float(
                                row.get("LESS_BUS_TAX_SURCHARGE")
                            ),
                            asset_impairment_loss=self._to_float(
                                row.get("LESS_ASSETS_IMPAIR_LOSS")
                            ),
                            credit_impairment_loss=self._to_float(
                                row.get("CREDIT_IMPAIR_LOSS")
                            ),
                            # ==================================================
                            # 收益项目
                            # ==================================================
                            investment_income=self._to_float(
                                row.get("PLUS_NET_INV_INC")
                            ),
                            fair_value_change_income=self._to_float(
                                row.get("PLUS_NET_GAIN_CHG_FV")
                            ),
                            exchange_income=self._to_float(row.get("PLUS_NET_FX_INC")),
                            other_income=self._to_float(row.get("OTH_INCOME")),
                            # ==================================================
                            # 利润
                            # ==================================================
                            gross_profit=self._calculate_gross_profit(row),
                            operating_profit=self._to_float(row.get("OPERA_PROFIT")),
                            total_profit=self._to_float(row.get("TOTAL_PROFIT")),
                            income_tax=self._to_float(row.get("INCOME_TAX")),
                            net_profit=self._to_float(
                                row.get("NET_PRO_INCL_MIN_INT_INC")
                            ),
                            net_profit_attributable=self._to_float(
                                row.get("NET_PRO_EXCL_MIN_INT_INC")
                            ),
                            non_recurring_net_profit=self._first_float(
                                row.get("NET_PRO_AFTER_DED_NR_GL"),
                                row.get("NET_PRO_AFTER_DED_NR_GL_COR"),
                            ),
                            # ==================================================
                            # 营业外收支
                            # ==================================================
                            non_operating_income=self._to_float(
                                row.get("PLUS_NON_OPERA_REV")
                            ),
                            non_operating_expense=self._to_float(
                                row.get("LESS_NON_OPERA_EXP")
                            ),
                            # ==================================================
                            # 其他综合收益
                            # ==================================================
                            other_comprehensive_income=self._to_float(
                                row.get("OTH_COMPRE_INC")
                            ),
                            # ==================================================
                            # EBIT / EBITDA
                            # ==================================================
                            ebit=self._to_float(row.get("EBIT")),
                            ebitda=self._to_float(row.get("EBITDA")),
                            # ==================================================
                            # 每股收益
                            # ==================================================
                            eps=self._to_float(row.get("BASIC_EPS")),
                            diluted_eps=self._to_float(row.get("DILUTED_EPS")),
                        )
                    )

                # ======================================================
                # 按报告期升序排列
                # ======================================================

                symbol_statements.sort(key=lambda item: item.report_date or "")

                statements[symbol] = symbol_statements

            return statements

        except Exception as exc:
            print(f"[银河] 获取利润表失败 " f"{symbols}: {exc}")
            return {}


    @staticmethod
    def _safe_float(value):
        """
        安全转换 float。
        """

        if value is None:
            return None

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float | None:
        """
        将数据源字段安全转换为 float。
        """

        if value is None:
            return None

        try:
            if pandas.isna(value):
                return None
        except (TypeError, ValueError):
            pass

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_str(
        value: object,
    ) -> str | None:
        """
        安全转换为字符串。
        """

        if value is None:
            return None

        try:
            if pandas.isna(value):
                return None
        except (TypeError, ValueError):
            pass

        value = str(value).strip()

        return value or None

    @classmethod
    def _calculate_gross_profit(
        cls,
        row: pandas.Series,
    ) -> float | None:
        """
        计算毛利润。

        Gross Profit =
            营业收入 - 营业成本
        """

        revenue = cls._to_float(row.get("OPERA_REV"))

        cost = cls._to_float(row.get("LESS_OPERA_COST"))

        if revenue is None or cost is None:
            return None

        return revenue - cost

    @staticmethod
    def _first_float(*values: object) -> float | None:
        for value in values:
            result = YinheFinancial._to_float(value)

            if result is not None:
                return result

        return None

    @staticmethod
    def _parse_report_period(
        report_date: str,
    ) -> tuple[int, int]:
        """
        将报告期转换为报告年度和季度。

        支持以下格式：

            20260630
            2026-06-30
            2026/06/30

        返回：

            (2026, 2)

        对应：

            03-31 -> Q1
            06-30 -> Q2
            09-30 -> Q3
            12-31 -> Q4
        """

        if report_date is None:
            raise ValueError("报告期不能为空")

        value = str(report_date).strip()

        # ==========================================================
        # 统一日期格式
        # ==========================================================

        value = value.replace("-", "")
        value = value.replace("/", "")

        if len(value) != 8 or not value.isdigit():
            raise ValueError(f"无效的财务报告期: {report_date}")

        # ==========================================================
        # 提取年月日
        # ==========================================================

        year = int(value[:4])
        month = int(value[4:6])
        day = int(value[6:8])

        # ==========================================================
        # 根据报告期月份判断季度
        # ==========================================================

        quarter_map = {
            (3, 31): 1,
            (6, 30): 2,
            (9, 30): 3,
            (12, 31): 4,
        }

        quarter = quarter_map.get((month, day))

        if quarter is None:
            raise ValueError(f"无效的财务报告期: {report_date}")

        return year, quarter

    @staticmethod
    def _quarter_index(
        year: int,
        quarter: int,
    ) -> int:
        """
        将报告年度和季度转换为连续季度序号。

        用于报告期之间的先后比较。

        示例：
            2025Q1 < 2025Q2
            2025Q4 < 2026Q1
        """

        return year * 4 + quarter - 1

    def fetch_financial(
        self,
        symbol: str,
        year: int | None = None,
        quarter: int | None = None,
    ) -> Financial | None:
        """
        获取股票完整财务数据。

        参数：
            symbol:
                股票代码。

            year:
                报告年份。

            quarter:
                报告季度：
                    1 -> Q1
                    2 -> Q2
                    3 -> Q3
                    4 -> Q4

        返回：
            Financial | None

        规则：

            1. year 和 quarter 都为空：
               获取最新报告期。

            2. year 和 quarter 都指定：
               获取指定报告期。
               如果指定报告期不存在，返回 None。

            3. 只指定 year：
               获取该年度最新可用报告期。
               如果该年度不存在，返回 None。

            4. quarter 不能单独指定。

        注意：

            Financial 只表示当前报告期。

            YOY / QOQ 所需要的历史报告期，
            由 FinancialAnalyzer 负责计算。
        """

        # ======================================================
        # 参数校验
        # ======================================================

        if year is None and quarter is not None:
            raise ValueError("quarter 不能单独指定，必须同时指定 year")

        if year is not None and year <= 0:
            raise ValueError(f"year 必须大于 0: {year}")

        if quarter is not None and quarter not in (
            1,
            2,
            3,
            4,
        ):
            raise ValueError(f"quarter 必须为 1、2、3、4: {quarter}")

        # ======================================================
        # 获取三张财务报表
        #
        # 这里获取全量历史数据。
        # 后面统一按照 report_date 对齐。
        # ======================================================

        income_statements = self.fetch_income_statement(
            symbol=symbol,
        )

        balance_sheets = self.fetch_balance_sheet(
            symbol=symbol,
        )

        cash_flows = self.fetch_cash_flow(
            symbol=symbol,
        )

        # ======================================================
        # 三张表都没有数据
        # ======================================================

        if not income_statements and not balance_sheets and not cash_flows:
            print(f"[财务] 未获取到财务数据: {symbol}")
            return None

        # ======================================================
        # 获取三张表的报告期
        # ======================================================

        income_dates = {
            item.report_date for item in income_statements if item.report_date
        }

        balance_dates = {
            item.report_date for item in balance_sheets if item.report_date
        }

        cash_flow_dates = {item.report_date for item in cash_flows if item.report_date}

        # ======================================================
        # 优先使用三张表共同存在的报告期
        #
        # 一个 Financial 最好由同一个报告期的
        # 利润表、资产负债表、现金流量表组成。
        # ======================================================

        common_dates = income_dates & balance_dates & cash_flow_dates

        # ======================================================
        # 如果三张表没有完全共同的报告期，
        # 则使用所有可用报告期。
        #
        # 这样可以允许某一张表暂时缺失。
        # ======================================================

        if common_dates:
            available_dates = sorted(common_dates)
        else:
            available_dates = sorted(income_dates | balance_dates | cash_flow_dates)

        if not available_dates:
            print(f"[财务] 未找到有效报告期: {symbol}")
            return None

        # ======================================================
        # 确定当前报告期
        # ======================================================

        selected_report_date = self._select_financial_report_date(
            symbol=symbol,
            available_dates=available_dates,
            year=year,
            quarter=quarter,
        )

        # ======================================================
        # 指定报告期不存在
        #
        # 注意：
        # 这里绝对不能 fallback 到最新报告期。
        # ======================================================

        if selected_report_date is None:
            return None

        # ======================================================
        # 获取当前报告期三张表
        # ======================================================

        income = self._find_report(
            income_statements,
            selected_report_date,
        )

        balance = self._find_report(
            balance_sheets,
            selected_report_date,
        )

        cash_flow = self._find_report(
            cash_flows,
            selected_report_date,
        )

        # ======================================================
        # 当前报告期完全没有数据
        # ======================================================

        if income is None and balance is None and cash_flow is None:
            print(f"[财务] 未找到报告期数据: " f"{symbol} {selected_report_date}")
            return None

        # ======================================================
        # 构建当前 Financial
        # ======================================================

        financial = self._build_financial(
            symbol=symbol,
            report_date=selected_report_date,
            income_statements=income_statements,
            balance_sheets=balance_sheets,
            cash_flows=cash_flows,
        )

        if financial is None:
            print(f"[财务] 构建 Financial 失败: " f"{symbol} {selected_report_date}")
            return None

        # ======================================================
        # 获取上一年度同期
        #
        # 例如：
        #
        # 2026-06-30
        #     ->
        # 2025-06-30
        #
        # 用于 YOY。
        # ======================================================

        previous_year_date = self._previous_year_report_date(selected_report_date)

        previous_year_financial = self._build_financial(
            symbol=symbol,
            report_date=previous_year_date,
            income_statements=income_statements,
            balance_sheets=balance_sheets,
            cash_flows=cash_flows,
        )

        # ======================================================
        # 获取上一季度
        #
        # 例如：
        #
        # 2026-06-30
        #     ->
        # 2026-03-31
        #
        # 2026-03-31
        #     ->
        # 2025-12-31
        #
        # 用于 QOQ。
        # ======================================================

        previous_quarter_date = self._previous_quarter_report_date(selected_report_date)

        previous_quarter_financial = self._build_financial(
            symbol=symbol,
            report_date=previous_quarter_date,
            income_statements=income_statements,
            balance_sheets=balance_sheets,
            cash_flows=cash_flows,
        )

        # ======================================================
        # 财务指标计算
        #
        # 当前 Financial：
        #     current
        #
        # 上年同期：
        #     previous_year
        #
        # 上一季度：
        #     previous_quarter
        #
        # FinancialAnalyzer 负责计算：
        #
        #     YOY
        #     QOQ
        #     ROE
        #     ROA
        #     ROIC
        #     各类财务指标
        # ======================================================

        if hasattr(self, "financial_analyzer"):

            financial.indicators = self.financial_analyzer.analyze(
                current=financial,
                previous_year=previous_year_financial,
                previous_quarter=previous_quarter_financial,
            )

        return financial

    # ==========================================================
    # 选择报告期
    # ==========================================================

    @staticmethod
    def _select_financial_report_date(
        symbol: str,
        available_dates: list[str],
        year: int | None,
        quarter: int | None,
    ) -> str | None:
        """
        根据用户指定的年份和季度选择报告期。

        规则：

            year=None, quarter=None
                -> 最新报告期

            year + quarter
                -> 指定报告期
                -> 不存在返回 None

            year only
                -> 该年度最新季度
                -> 不存在返回 None

            quarter only
                -> 参数错误
        """

        if not available_dates:
            return None

        # ======================================================
        # 没有指定报告期
        #
        # 默认使用最新报告期
        # ======================================================

        if year is None and quarter is None:

            return available_dates[-1]

        # ======================================================
        # quarter 不能单独指定
        # ======================================================

        if year is None and quarter is not None:

            raise ValueError("quarter 不能单独指定，必须同时指定 year")

        # ======================================================
        # 指定 year + quarter
        #
        # 必须精确匹配。
        #
        # 不存在：
        #     返回 None
        #
        # 不允许：
        #     自动使用最新报告期
        # ======================================================

        if year is not None and quarter is not None:

            requested_report_date = StockDataGateway._build_report_date(
                year,
                quarter,
            )

            if requested_report_date not in available_dates:

                print(
                    f"[财务] {symbol} " f"未找到指定报告期: " f"{requested_report_date}"
                )

                return None

            return requested_report_date

        # ======================================================
        # 只指定 year
        #
        # 取该年度最新可用季度。
        #
        # 例如：
        #
        # 2026 年只有 Q1、Q2
        #     -> 取 2026Q2
        # ======================================================

        if year is not None:

            year_dates = [
                report_date
                for report_date in available_dates
                if report_date.startswith(str(year))
            ]

            if not year_dates:

                print(f"[财务] {symbol} " f"未找到指定年份: {year}")

                return None

            return year_dates[-1]

        return None

    # ==========================================================
    # 构建报告期
    # ==========================================================

    @staticmethod
    def _build_report_date(
        year: int,
        quarter: int,
    ) -> str:
        """
        根据年份和季度生成报告期。

        例如：

            2026, 1 -> 2026-03-31
            2026, 2 -> 2026-06-30
            2026, 3 -> 2026-09-30
            2026, 4 -> 2026-12-31
        """

        quarter_dates = {
            1: "-03-31",
            2: "-06-30",
            3: "-09-30",
            4: "-12-31",
        }

        if quarter not in quarter_dates:
            raise ValueError(f"无效季度: {quarter}")

        return f"{year}" f"{quarter_dates[quarter]}"

    # ==========================================================
    # 获取上一年度同期
    # ==========================================================

    @staticmethod
    def _previous_year_report_date(
        report_date: str,
    ) -> str:
        """
        获取上一年度同期报告期。

        例如：

            2026-03-31
                ->
            2025-03-31

            2026-06-30
                ->
            2025-06-30
        """

        if not report_date:
            return ""

        try:

            year = int(report_date[:4])

            return f"{year - 1}" f"{report_date[4:]}"

        except (
            ValueError,
            TypeError,
        ):

            return ""

    # ==========================================================
    # 获取上一季度
    # ==========================================================

    @staticmethod
    def _previous_quarter_report_date(
        report_date: str,
    ) -> str:
        """
        获取上一季度报告期。

        例如：

            2026-06-30
                ->
            2026-03-31

            2026-09-30
                ->
            2026-06-30

            2026-03-31
                ->
            2025-12-31
        """

        if not report_date:
            return ""

        quarter_map = {
            "-03-31": 1,
            "-06-30": 2,
            "-09-30": 3,
            "-12-31": 4,
        }

        try:

            year = int(report_date[:4])

            month_day = report_date[4:]

            quarter = quarter_map.get(month_day)

            if quarter is None:
                return ""

            # --------------------------------------------------
            # Q1 的上一季度是上一年的 Q4
            # --------------------------------------------------

            if quarter == 1:

                year -= 1
                quarter = 4

            else:

                quarter -= 1

            return StockDataGateway._build_report_date(
                year,
                quarter,
            )

        except (
            ValueError,
            TypeError,
        ):

            return ""

    # ==========================================================
    # 查找指定报告期
    # ==========================================================

    @staticmethod
    def _find_report(
        reports: list,
        report_date: str,
    ):
        """
        从报告列表中查找指定报告期。
        """

        if not reports or not report_date:
            return None

        for report in reports:

            if report.report_date == report_date:
                return report

        return None

    # ==========================================================
    # 构建 Financial
    # ==========================================================

    def _build_financial(
        self,
        symbol: str,
        report_date: str,
        income_statements: list[IncomeStatement],
        balance_sheets: list[BalanceSheet],
        cash_flows: list[CashFlow],
    ) -> Financial | None:
        """
        根据报告期构建 Financial。

        Financial 只表示一个报告期。

        如果该报告期三张表均不存在，
        返回 None。
        """

        if not report_date:
            return None

        # ======================================================
        # 查找三张报表
        # ======================================================

        income = self._find_report(
            income_statements,
            report_date,
        )

        balance = self._find_report(
            balance_sheets,
            report_date,
        )

        cash_flow = self._find_report(
            cash_flows,
            report_date,
        )

        # ======================================================
        # 三张表都不存在
        # ======================================================

        if income is None and balance is None and cash_flow is None:
            return None

        # ======================================================
        # 构建 Financial
        # ======================================================

        return Financial(
            symbol=symbol,
            report_date=report_date,
            income=income,
            balance=balance,
            cash_flow=cash_flow,
        )
