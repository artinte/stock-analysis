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
