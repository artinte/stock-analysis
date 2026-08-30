from core.models.financial.financial import Financial
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
                statement_type=latest.get("STATEMENT_TYPE"),
                announcement_date=str(latest.get("ANN_DATE", "")),
                currency=latest.get(
                    "CURRENCY_CODE",
                    "CNY",
                ),
                # ==================================================
                # 利润表
                # ==================================================
                operating_income=self._safe_float(latest.get("OPERA_REV")),
                revenue=self._safe_float(latest.get("TOT_OPERA_REV")),
                operating_cost=self._safe_float(latest.get("LESS_OPERA_COST")),
                total_operating_cost=self._safe_float(latest.get("TOT_OPERA_COST")),
                operating_profit=self._safe_float(latest.get("OPERA_PROFIT")),
                total_profit=self._safe_float(latest.get("TOTAL_PROFIT")),
                net_profit=self._safe_float(latest.get("NET_PRO_INCL_MIN_INT_INC")),
                net_profit_attributable=self._safe_float(
                    latest.get("NET_PRO_EXCL_MIN_INT_INC")
                ),
                non_recurring_net_profit=self._safe_float(
                    latest.get("NET_PRO_AFTER_DED_NR_GL")
                ),
                # ==================================================
                # 费用
                # ==================================================
                selling_expense=self._safe_float(latest.get("LESS_SELLING_EXP")),
                administrative_expense=self._safe_float(latest.get("LESS_ADMIN_EXP")),
                financial_expense=self._safe_float(latest.get("LESS_FIN_EXP")),
                rd_expense=self._safe_float(latest.get("RD_EXP")),
                # ==================================================
                # 盈利能力
                # ==================================================
                gross_margin=self._safe_float(latest.get("GROSS_PROFIT_MARGIN")),
                net_margin=self._safe_float(latest.get("NET_PROFIT_MARGIN")),
                roe=self._safe_float(latest.get("ROE")),
                roa=self._safe_float(latest.get("DUPONT_ROA")),
                # ==================================================
                # EBIT / EBITDA
                # ==================================================
                ebit=self._safe_float(latest.get("EBIT")),
                ebitda=self._safe_float(latest.get("EBITDA")),
                # ==================================================
                # 每股指标
                # ==================================================
                eps=self._safe_float(latest.get("BASIC_EPS")),
                diluted_eps=self._safe_float(latest.get("DILUTED_EPS")),
                book_value_per_share=self._safe_float(latest.get("BPS")),
                operating_cash_flow_per_share=self._safe_float(latest.get("OCFPS")),
                # ==================================================
                # 资产负债
                # ==================================================
                total_assets=self._safe_float(latest.get("TOTAL_ASSETS")),
                total_liabilities=self._safe_float(latest.get("TOTAL_LIABILITIES")),
                shareholders_equity=self._safe_float(latest.get("TOTAL_EQUITY")),
                # ==================================================
                # 财务健康
                # ==================================================
                debt_to_asset_ratio=self._safe_float(latest.get("DEBT_TO_ASSETS")),
                current_ratio=self._safe_float(latest.get("CURRENT_RATIO")),
                quick_ratio=self._safe_float(latest.get("QUICK_RATIO")),
                # ==================================================
                # 运营效率
                # ==================================================
                receivable_turnover=self._safe_float(latest.get("AR_TURN")),
                inventory_turnover=self._safe_float(latest.get("INV_TURN")),
                # ==================================================
                # 现金流
                # ==================================================
                operating_cash_flow=self._safe_float(latest.get("OCF")),
                fcff=self._safe_float(latest.get("FCFF")),
                fcfe=self._safe_float(latest.get("FCFE")),
                source="yinhe",
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
