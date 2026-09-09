from typing import Any

import pandas

from core.models.financial.financial import Financial
from core.models.financial.income_statement import IncomeStatement
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

    def _fetch_income_statement(
        self,
        symbol: str,
        start_year: int | None = None,
        start_quarter: int | None = None,
        end_year: int | None = None,
        end_quarter: int | None = None,
    ) -> list[Financial]:
        """
        获取利润表数据。

        将银河证券返回的利润表 DataFrame
        转换为统一 Financial 模型。

        数据流：

            AmazingData
                |
                ↓
            DataFrame
        """

        try:
            # ======================================================
            # 获取银河原始数据
            # ======================================================

            result = self.gateway.info_data.get_income(
                [symbol],
                local_path=self.gateway.local_path,
                is_local=True,
            )

            if not result:
                print(f"[银河] 未获取到利润表数据: {symbol}")
                return []

            # ======================================================
            # 获取当前股票 DataFrame
            # ======================================================

            df = result.get(symbol)

            if "REPORTING_PERIOD" in df.columns:
                for period in df["REPORTING_PERIOD"]:
                    print(f"    {period}")
            else:
                print("[银河] 未找到 REPORTING_PERIOD 字段")

            if df is None:
                print(f"[银河] 未找到股票利润表: {symbol}")
                return []

            if df.empty:
                print(f"[河] 利润表为空: {symbol}")
                return []

            if "REPORTING_PERIOD" not in df.columns:
                print(f"[银河] 利润表缺少 REPORTING_PERIOD: " f"{symbol}")
                return []

            # ======================================================
            # 根据报告期筛选
            # ======================================================

            selected_rows = []

            for _, row in df.iterrows():

                report_date = str(row.get("REPORTING_PERIOD"))
                if not report_date:
                    continue

                report_year, report_quarter = self.gateway._parse_report_period(
                    report_date
                )

                # --------------------------------------------------
                # 起始报告期
                # --------------------------------------------------

                if start_year is not None:
                    if self.gateway._quarter_index(
                        report_year,
                        report_quarter,
                    ) < self.gateway._quarter_index(
                        start_year,
                        start_quarter,
                    ):
                        continue

                # --------------------------------------------------
                # 结束报告期
                # --------------------------------------------------

                if end_year is not None:
                    if self.gateway._quarter_index(
                        report_year,
                        report_quarter,
                    ) > self.gateway._quarter_index(
                        end_year,
                        end_quarter,
                    ):
                        continue

                selected_rows.append(row)

            if not selected_rows:
                return []

            # ======================================================
            # 转换为标准 IncomeStatement
            # ======================================================

            statements: list[IncomeStatement] = []

            for row in selected_rows:
                statements.append(
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
                        total_operating_income=self._to_float(row.get("TOT_OPERA_REV")),
                        # ==================================================
                        # 成本费用
                        # ==================================================
                        operating_cost=self._to_float(row.get("LESS_OPERA_COST")),
                        total_operating_cost=self._to_float(row.get("TOT_OPERA_COST")),
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
                        investment_income=self._to_float(row.get("PLUS_NET_INV_INC")),
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
                        net_profit=self._to_float(row.get("NET_PRO_INCL_MIN_INT_INC")),
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
                            row.get("PLUS_NON_OPER_A_REV")
                        ),
                        non_operating_expense=self._to_float(
                            row.get("LESS_NON_OPER_A_EXP")
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

            statements.sort(key=lambda item: item.report_date or "")
            return statements
        except Exception as exc:
            print(f"[银河] 获取利润表失败 " f"{symbol}: {exc}")
            return []

    def fetch_financial(
        self,
        symbol: str,
    ) -> Financial | None:
        """
        获取股票财务数据。

        将银河证券返回的财务指标 DataFrame
        转换为统一 Financial 模型。

        数据流：

            AmazingData
                |
                ↓
            DataFrame
                |
                ↓
            Financial
        """

        self.gateway._ensure_started()

        formatted_symbol = normalize_symbol(symbol)

        try:
            if not self.gateway.calendar:
                print(
                    f"[银河网关] 财务数据获取失败 " f"{formatted_symbol}: 交易日历为空"
                )
                return None

            financials_dict = self.gateway.info_data.get_income(
                code_list=[formatted_symbol],
                local_path=self.gateway.local_path,
                is_local=False,
                begin_date="20220101",
                end_date=self.gateway.calendar[-1],
            )

            if not financials_dict:
                return None

            df = financials_dict.get(formatted_symbol)

            if df is None or df.empty:
                return None

            # 最新一期财务数据
            latest = self.gateway._get_latest_financial_row(df)

            if latest is None:
                return None

            financial = Financial(
                symbol=formatted_symbol,
                # ==================================================
                # 基础信息
                # ==================================================
                report_date=str(
                    latest.get(
                        "REPORTING_PERIOD",
                        "",
                    )
                ),
            )

            return financial

        except Exception as e:

            print(f"[银河网关] 获取财务数据失败 " f"{formatted_symbol}: {e}")

            return None

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
