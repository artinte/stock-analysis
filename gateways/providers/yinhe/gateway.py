from __future__ import annotations

import datetime
import os
from typing import Any, Optional

import AmazingData
import pandas
from dotenv import load_dotenv
import tgw

from core.models.stock import Stock
from gateways.data_gateway import StockDataGateway
from common.constants import Interval, TEN_THOUSAND
from core.models.financial.financial import IncomeStatement
from core.models.financial.financial import CashFlowStatement
from core.models.financial.financial import BalanceSheet
from core.models.financial.financial import Financial
from core.models.kline import Kline
from core.models.valuation import Valuation
from core.models.quote import Quote
from gateways.analysis.financial import FinancialAnalyzer
from gateways.providers.yinhe.financial import YinheFinancial
from gateways.providers.yinhe.kline import YinheKline
from gateways.providers.yinhe.quote import YinheQuote
from gateways.providers.yinhe.stock import YinheStock
from gateways.providers.yinhe.valuation import YinheValuation
from gateways.registry import GatewayRegistry

from utils.stock_mapping import normalize_symbol

"""
银河证券数据网关。

银河证券提供两组API：
pip install tgw-1.7.1-py3-none-any.whl 
pip install AmazingData-1.0.0-cp312-none-any.whl

具体介绍联系相关券商。

本模块实现基于 AmazingData 的银河证券数据源适配器，
将 AmazingData 提供的原始数据转换为项目内部统一的数据模型
和接口，使上层业务无需直接依赖具体的数据源实现。

主要功能包括：

- 管理 AmazingData 数据源的登录、注销和运行状态。
- 获取股票基础信息。
- 获取历史 K 线，并转换为统一的 Kline 模型。
- 获取股票财务数据。
- 获取股票最新价格及总市值。
- 根据财务数据和市值计算静态 PE、动态 PE 和 TTM PE。
- 将估值结果转换为统一的 Valuation 模型。
- 对股票代码进行标准化，自动识别上海、深圳和北京市场。

本模块属于数据源适配层，上层业务统一通过
StockDataGateway 访问数据，不应直接依赖 AmazingData。

数据流：

    DataManager
        ↓
    StockDataGateway
        ↓
    YinheGateway
        ↓
    AmazingData
        ↓
    银河证券数据服务

当前已支持：

- 股票基础信息
- 历史 K 线
- 财务数据
- 估值数据

实时行情接口暂未接入，相关方法会明确抛出 NotImplementedError。
"""


@GatewayRegistry.register("yinhe")
class YinheGateway(StockDataGateway):
    """
    银河证券数据网关。

    负责将 AmazingData 数据接口适配到统一的
    StockDataGateway 接口。

    上层业务只依赖 StockDataGateway，
    不应该直接依赖 AmazingData。
    """

    name = "yinhe"
    display_name = "银河证券"

    def __init__(
        self,
        config: Optional[dict] = None,
    ) -> None:
        """
        初始化银河证券数据网关。

        Parameters
        ----------
        config:
            数据源配置，例如：

                {
                    "host": "...",
                    "port": 1234,
                    "username": "...",
                    "password": "...",
                    "local_path": "..."
                }
        """

        self.config = config or {}

        self._started = False

        self.user = ""
        self.host = ""
        self.port = 0

        self.local_path = os.path.curdir

        # AmazingData 数据接口
        self.info_data = None
        self.base_data = None
        self.calendar = None
        self.market_data = None

        # ==========================================================
        # 组合式设计（Composition）
        #
        # YinheGateway 作为银河证券数据源的统一入口，
        # 负责生命周期管理以及对外接口转发。
        #
        # 具体业务功能按照数据类型拆分到独立组件中：
        #
        #     YinheStock       股票基础信息
        #     YinheKline       K线数据
        #     YinheQuote       行情数据
        #     YinheFinancial   财务数据
        #     YinheValuation   估值数据
        #
        # 这些组件共享同一个 YinheGateway 实例，
        # 可以访问银河证券的数据连接、登录状态以及
        # AmazingData 接口对象。
        #
        # 这样可以避免 YinheGateway 成为一个过大的上帝类，
        # 同时保持 DataManager 和 StockDataGateway 接口稳定。
        #
        # 注意：
        # 这些组件并不是独立的数据源，
        # 而是 YinheGateway 内部针对不同业务能力的拆分。
        # ==========================================================

        self.stock = YinheStock(self)

        self.kline = YinheKline(self)

        self.quote = YinheQuote(self)

        self.financial = YinheFinancial(self)

        self.valuation = YinheValuation(self)

        self.financial_analyzer = FinancialAnalyzer()

    # ==========================================================
    # 生命周期
    # ==========================================================

    def login(
        self,
        config: Optional[dict] = None,
    ) -> bool:
        """
        登录银河证券数据源。

        登录成功后初始化：

            InfoData
            BaseData
            Calendar
            MarketData
        """

        if config:
            self.config.update(config)
        else:
            load_dotenv()

            self.config = {
                "username": os.getenv("amazing_username", ""),
                "password": os.getenv("amazing_password", ""),
                "host": os.getenv("amazing_host", ""),
                "port": int(os.getenv("amazing_port", "0")),
                "local_path": os.getenv("local_path", os.path.curdir),
            }

        try:
            self.user = self.config.get("username", "default")
            self.host = self.config.get("host", "127.0.0.1")
            self.port = int(self.config.get("port", 0))
            self.local_path = self.config.get("local_path", os.path.curdir)

            print(
                f"[银河网关] 尝试登录: "
                f"网址：{self.host}:{self.port}\n"
                f"用户: {self.user}"
            )

            # --------------------------------------------------
            # 登录 AmazingData
            # --------------------------------------------------

            AmazingData.login(
                username=self.config["username"],
                password=self.config["password"],
                host=self.config["host"],
                port=self.port,
            )

            # --------------------------------------------------
            # 初始化数据接口
            # --------------------------------------------------

            self.info_data = AmazingData.InfoData()
            self.base_data = AmazingData.BaseData()
            self.calendar = self.base_data.get_calendar()
            self.market_data = AmazingData.MarketData(self.calendar)
            self._started = True

            print("[银河网关] 登录成功")

            return True

        except ValueError:
            print("[银河网关] 端口格式无效，请检查配置。")

            self._started = False

            return False

        except Exception as e:
            print(f"[银河网关] 登录异常: {e}")

            self._started = False

            return False

    def logout(self) -> None:
        """
        注销银河数据源。
        """

        if self._started:
            try:
                print("[银河网关] 退出登录")
                AmazingData.logout(self.user)
            except Exception as e:
                print(f"[银河网关] 注销异常: {e}")

        self.info_data = None
        self.base_data = None
        self.calendar = None
        self.market_data = None

        self._started = False

    def health_check(self) -> bool:
        """
        检查数据源是否已经启动。
        """

        return self._started

    def fetch_stock(
        self,
        symbol: str,
    ) -> Stock:
        """
        获取股票基础信息。

        当前返回：

            {
                "symbol": "...",
                "name": "..."
            }
        """
        return self.stock.fetch_stock(symbol)

    def fetch_stocks(
        self,
        symbols: list[str],
    ) -> list[Stock]:
        """
        批量获取股票基础信息。
        """
        return self.stock.fetch_stocks(symbols)

    def fetch_stock_by_name(
        self,
        name: str,
    ) -> Stock:
        """
        根据股票名称获取股票基础信息。

        当前返回：

            {
                "symbol": "...",
                "name": "..."
            }
        """
        return self.stock.fetch_stock_by_name(name)

    def fetch_stock_name(
        self,
        symbol: str,
    ) -> str:
        """
        获取股票名称。

        这是银河数据源内部辅助方法，
        不属于 StockDataGateway 统一接口。
        """
        return self.stock.fetch_stock_name(symbol)

    def fetch_quote(
        self,
        symbol: str,
    ) -> Optional[Quote]:
        """
        获取股票最新行情。

        当前 AmazingData 未直接接入实时行情接口，
        使用最近交易日 K 线构造行情快照。

        因此：

            price = 最近交易日收盘价
            prev_close = 前一交易日收盘价

        注意：
            这里不是实时行情。
        """
        return self.quote.fetch_quote(symbol=symbol)

    def fetch_kline(
        self,
        symbol: str,
        interval: Interval = Interval.DAY_1,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 1000,
    ) -> list[Kline]:
        """
        获取历史 K 线。

        AmazingData 原始数据：

            DataFrame

        转换为：

            list[Kline]
        """
        return self.kline.fetch_kline(symbol, interval, start_time, end_time, limit)

    def fetch_quotes(
        self,
        symbols: list[str],
    ):
        """
        批量获取股票最新行情。
        """

        self._ensure_started()

        if not symbols:
            return []

        raise NotImplementedError(
            "YinheGateway.fetch_quotes() " "尚未接入银河证券批量行情接口"
        )

    def fetch_valuation(
        self,
        symbol: str,
    ) -> Valuation:
        """
        获取股票估值数据。

        包括：

            当前价格
            总市值
            静态 PE
            动态 PE
            TTM PE
        """
        return self.valuation.fetch_valuation(symbol)
    
    def fetch_etf_composition(
        self,
        symbol: str,
        trade_date: datetime.date | None = None,
    ):
        return self.etf.fetch_etf_composition(symbol, trade_date)

    def _get_latest_financial_row(
        self,
        df,
    ):
        """
        获取最新一期财务数据。
        """

        if df is None or df.empty:
            return None

        if "REPORTING_PERIOD" in df.columns:

            df = df.copy()

            df["REPORTING_PERIOD"] = df["REPORTING_PERIOD"].astype(str)

            df = df.sort_values("REPORTING_PERIOD")

        return df.iloc[-1]

    def fetch_income_statement_abandon(
        self,
        symbol: str,
    ) -> IncomeStatement | None:
        """
        获取利润表。

        银河 get_income() 返回：

            {
                "600519.SH": DataFrame
            }

        将指定股票最新一条利润表数据转换为
        统一 IncomeStatement 模型。
        """

        self._ensure_started()

        symbol = normalize_symbol(symbol)

        try:
            # ======================================================
            # 获取银河原始数据
            # ======================================================

            result = self.info_data.get_income(
                [symbol],
                local_path=self.local_path,
                is_local=False,
            )

            if not result:
                print(f"[银河] 未获取到利润表数据: {symbol}")
                return None

            # ======================================================
            # 从 dict 中取出当前股票 DataFrame
            # ======================================================

            df = result.get(symbol)

            if df is None:
                print(f"[银河] 未找到股票利润表: {symbol}")
                return None

            if df.empty:
                print(f"[银河] 利润表为空: {symbol}")
                return None

            # ======================================================
            # 输出调试信息
            # ======================================================

            print(f"[银河] get_income: " f"shape={df.shape}")

            print(f"[银河] get_income columns: " f"{list(df.columns)}")

            # ======================================================
            # 选择记录
            #
            # 当前先取第一条。
            # 后续如果需要指定报告期，
            # 再根据 REPORTING_PERIOD /
            # REPORT_TYPE / STATEMENT_TYPE 筛选。
            # ======================================================

            row = df.iloc[0]

            # ======================================================
            # 转换为标准 IncomeStatement
            # ======================================================

            return IncomeStatement(
                # ==========================================================
                # 基础信息
                # ==========================================================
                symbol=symbol,
                report_date=self._to_str(row.get("REPORTING_PERIOD")),
                report_type=self._to_str(row.get("REPORT_TYPE")),
                statement_type=self._to_str(row.get("STATEMENT_TYPE")),
                announcement_date=self._to_str(row.get("ANN_DATE")),
                currency=self._to_str(row.get("CURRENCY_CODE")),
                # ==========================================================
                # 收入
                # ==========================================================
                revenue=self._to_float(row.get("OPERA_REV")),
                total_operating_income=self._to_float(row.get("TOT_OPERA_REV")),
                # ==========================================================
                # 成本费用
                # ==========================================================
                operating_cost=self._to_float(row.get("LESS_OPERA_COST")),
                total_operating_cost=self._to_float(row.get("TOT_OPERA_COST")),
                selling_expense=self._to_float(row.get("LESS_SELLING_EXP")),
                administrative_expense=self._to_float(row.get("LESS_ADMIN_EXP")),
                financial_expense=self._to_float(row.get("LESS_FIN_EXP")),
                rd_expense=self._to_float(row.get("RD_EXP")),
                business_tax_and_surcharge=self._to_float(
                    row.get("LESS_BUS_TAX_SURCHARGE")
                ),
                asset_impairment_loss=self._to_float(
                    row.get("LESS_ASSETS_IMPAIR_LOSS")
                ),
                credit_impairment_loss=self._to_float(row.get("CREDIT_IMPAIR_LOSS")),
                # ==========================================================
                # 收益项目
                # ==========================================================
                investment_income=self._to_float(row.get("PLUS_NET_INV_INC")),
                fair_value_change_income=self._to_float(
                    row.get("PLUS_NET_GAIN_CHG_FV")
                ),
                exchange_income=self._to_float(row.get("PLUS_NET_FX_INC")),
                other_income=self._to_float(row.get("OTH_INCOME")),
                # ==========================================================
                # 利润
                # ==========================================================
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
                # ==========================================================
                # 营业外收支
                # ==========================================================
                non_operating_income=self._to_float(row.get("PLUS_NON_OPER_A_REV")),
                non_operating_expense=self._to_float(row.get("LESS_NON_OPER_A_EXP")),
                # ==========================================================
                # 其他综合收益
                # ==========================================================
                other_comprehensive_income=self._to_float(row.get("OTH_COMPRE_INC")),
                # ==========================================================
                # EBIT / EBITDA
                # ==========================================================
                ebit=self._to_float(row.get("EBIT")),
                ebitda=self._to_float(row.get("EBITDA")),
                # ==========================================================
                # 每股收益
                # ==========================================================
                eps=self._to_float(row.get("BASIC_EPS")),
                diluted_eps=self._to_float(row.get("DILUTED_EPS")),
            )

        except Exception as exc:
            print(f"[银河] 获取利润表失败 " f"{symbol}: {exc}")
            return None

    def _fetch_income_statement(
        self,
        symbol: str,
        start_year: Optional[int],
        start_quarter: Optional[int],
        end_year: Optional[int],
        end_quarter: Optional[int],
    ) -> list[IncomeStatement]:
        """
        获取银河利润表数据。

        本方法由 StockDataGateway.fetch_income_statement()
        调用，不负责校验报告期参数。

        参数：
            symbol:
                标准化后的股票代码。

            start_year:
                起始报告年度。

            start_quarter:
                起始报告季度，取值 1~4。

            end_year:
                结束报告年度。

            end_quarter:
                结束报告季度，取值 1~4。

        查询规则：
            - 不指定开始和结束报告期：返回全部历史数据。
            - 只指定开始报告期：返回从开始报告期到最新的数据。
            - 只指定结束报告期：返回从最早数据到结束报告期的数据。
            - 同时指定开始和结束报告期：返回闭区间内的数据。

        返回：
            list[IncomeStatement]:
                标准化后的利润表数据。
                如果没有数据，则返回空列表。
        """

        self._ensure_started()

        symbol = normalize_symbol(symbol)

        try:
            # ======================================================
            # 获取银河原始数据
            # ======================================================

            result = self.info_data.get_income(
                [symbol],
                local_path=self.local_path,
                is_local=False,
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
                print(f"[银河] 利润表为空: {symbol}")
                return []

            if "REPORTING_PERIOD" not in df.columns:
                print(f"[银河] 利润表缺少 REPORTING_PERIOD: " f"{symbol}")
                return []

            # ======================================================
            # 根据报告期筛选
            # ======================================================

            selected_rows = []

            for _, row in df.iterrows():

                report_date = self._to_str(row.get("REPORTING_PERIOD"))
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

    def fetch_balance_sheet(
        self,
        symbol: str,
    ) -> BalanceSheet | None:
        """
        获取资产负债表。

        银河 get_balance_sheet() 返回：

            {
                "600519.SH": DataFrame
            }

        转换为统一 BalanceSheet 模型。
        """

        self._ensure_started()
        symbol = normalize_symbol(symbol)

        try:
            result = self.info_data.get_balance_sheet(
                [symbol],
                local_path=self.local_path,
                is_local=True,
            )
            if not result:
                print(f"[银河] 未获取到资产负债表数据: {symbol}")
                return None

            df = result.get(symbol)

            if df is None:
                print(f"[银河] 未找到资产负债表: {symbol}")
                return None

            if df.empty:
                print(f"[银河] 资产负债表为空: {symbol}")
                return None

            print(f"[银河] get_balance_sheet: " f"shape={df.shape}")

            print(f"[银河] get_balance_sheet columns: " f"{list(df.columns)}")

            row = df.iloc[0]

            return BalanceSheet(
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
                non_current_assets=self._to_float(row.get("TOT_NONCUR_ASSETS")),
                cash=self._to_float(row.get("CURRENCY_CAP")),
                accounts_receivable=self._to_float(row.get("ACCT_RECEIVABLE")),
                inventory=self._to_float(row.get("INV")),
                fixed_assets=self._to_float(row.get("FIXED_ASSETS")),
                construction_in_progress=self._to_float(row.get("CONST_IN_PROC")),
                intangible_assets=self._to_float(row.get("INTANGIBLE_ASSETS")),
                goodwill=self._to_float(row.get("GOODWILL")),
                long_term_equity_investment=self._to_float(row.get("LT_EQUITY_INV")),
                investment_real_estate=self._to_float(row.get("INV_REALESTATE")),
                right_of_use_assets=self._to_float(row.get("USE_RIGHT_ASSETS")),
                # ==================================================
                # 负债
                # ==================================================
                total_liabilities=self._to_float(row.get("TOTAL_LIAB")),
                current_liabilities=self._to_float(row.get("TOTAL_CUR_LIAB")),
                non_current_liabilities=self._to_float(row.get("TOTAL_NONCUR_LIAB")),
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
                total_equity=self._to_float(row.get("TOT_SHARE_EQUITY_INCL_MIN_INT")),
                shareholders_equity=self._to_float(
                    row.get("TOT_SHARE_EQUITY_EXCL_MIN_INT")
                ),
                minority_interest=self._to_float(row.get("MINORITY_EQUITY")),
                share_capital=self._to_float(row.get("CAP_STOCK")),
                capital_reserve=self._to_float(row.get("CAP_RESV")),
                surplus_reserve=self._to_float(row.get("SURPLUS_RESV")),
                undistributed_profit=self._to_float(row.get("UNDISTRIBUTED_PRO")),
                treasury_stock=self._to_float(row.get("LESS_TREASURY_STK")),
            )

        except SystemExit as exc:
            print(f"[银河] get_balance_sheet 调用了 exit(): " f"{exc}")
            return None

        except BaseException as exc:
            print(f"[银河] get_balance_sheet 异常: " f"{type(exc).__name__}: {exc}")
            return None

    def fetch_cash_flow(
        self,
        symbol: str,
    ) -> CashFlowStatement | None:
        """
        获取现金流量表。

        银河 get_cash_flow() 返回：

            {
                "600519.SH": DataFrame
            }

        转换为统一 CashFlowStatement 模型。
        """

        self._ensure_started()

        symbol = normalize_symbol(symbol)

        try:
            result = self.info_data.get_cash_flow(
                [symbol],
                local_path=self.local_path,
                is_local=False,
            )

            if not result:
                print(f"[银河] 未获取到现金流量表数据: " f"{symbol}")
                return None

            df = result.get(symbol)

            if df is None:
                print(f"[银河] 未找到现金流量表: " f"{symbol}")
                return None

            if df.empty:
                print(f"[银河] 现金流量表为空: " f"{symbol}")
                return None

            print(f"[银河] get_cash_flow: " f"shape={df.shape}")

            print(f"[银河] get_cash_flow columns: " f"{list(df.columns)}")

            row = df.iloc[0]

            return CashFlowStatement(
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
                operating_cash_flow=self._to_float(row.get("NET_CASH_FLOWS_OPERA_ACT")),
                cash_flow_from_operations=self._to_float(
                    row.get("IND_NET_CASH_FLOWS_OPERA_ACT")
                ),
                operating_cash_inflow=self._to_float(
                    row.get("TOT_CASH_INFLOW_OPERA_ACT")
                ),
                operating_cash_outflow=self._to_float(
                    row.get("TOT_CASH_OUTFLOW_OPERA_ACT")
                ),
                cash_received_from_sales=self._to_float(row.get("CASH_RECP_SG_AND_RS")),
                cash_paid_for_goods=self._to_float(row.get("CASH_PAY_GOODS_SERVICES")),
                cash_paid_to_employees=self._to_float(row.get("CASH_PAY_EMPLOYEE")),
                taxes_paid=self._to_float(row.get("PAY_ALL_TAX")),
                tax_refund_received=self._to_float(row.get("RECP_TAX_REFUND")),
                # ==================================================
                # 投资活动
                # ==================================================
                investing_cash_flow=self._to_float(row.get("NET_CASH_FLOWS_INV_ACT")),
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
                financing_cash_flow=self._to_float(row.get("NET_CASH_FLOWS_FIN_ACT")),
                financing_cash_inflow=self._to_float(
                    row.get("TOT_CASH_INFLOW_FIN_ACT")
                ),
                financing_cash_outflow=self._to_float(
                    row.get("TOT_CASH_OUTFLOW_FIN_ACT")
                ),
                cash_received_from_borrowings=self._to_float(
                    row.get("CASH_RECE_BORROW")
                ),
                cash_paid_for_debt=self._to_float(row.get("CASH_PAY_FOR_DEBT")),
                dividends_interest_paid=self._to_float(
                    row.get("CASH_PAY_DIST_DIV_PRO_INT")
                ),
                cash_from_equity_investment=self._to_float(
                    row.get("ABSORB_CASH_RECP_INV")
                ),
                # ==================================================
                # 现金及现金等价物
                # ==================================================
                beginning_cash_balance=self._to_float(row.get("BEG_BAL_CASH_CASH_EQU")),
                ending_cash_balance=self._to_float(row.get("END_BAL_CASH_CASH_EQU")),
                net_change_in_cash=self._to_float(
                    row.get("NET_INCR_CASH_AND_CASH_EQU")
                ),
                exchange_rate_effect=self._to_float(row.get("EFF_FX_FLUC_CASH")),
                # ==================================================
                # 自由现金流
                # ==================================================
                free_cash_flow=self._to_float(row.get("FREE_CASH_FLOW")),
            )

        except Exception as exc:
            print(f"[银河] 获取现金流量表失败 " f"{symbol}: {exc}")
            return None

    def fetch_financial(
        self,
        symbol: str,
    ) -> Financial | None:
        """
        获取完整财务数据。

        由以下三个财务报表接口组合：

            fetch_income_statement()
            fetch_balance_sheet()
            fetch_cash_flow()

        转换为统一 Financial 模型。

        数据流：

            AmazingData
                |
                +--> IncomeStatement
                |
                +--> BalanceSheet
                |
                +--> CashFlowStatement
                        |
                        v
                    Financial
        """

        self._ensure_started()

        symbol = normalize_symbol(symbol)

        try:
            # ======================================================
            # 1. 利润表
            # ======================================================

            income = self.fetch_income_statement_abandon(symbol)

            # ======================================================
            # 2. 资产负债表
            # ======================================================

            balance = self.fetch_balance_sheet(symbol)

            # ======================================================
            # 3. 现金流量表
            # ======================================================

            cash_flow = self.fetch_cash_flow(symbol)

            # ======================================================
            # 三张报表全部没有获取到
            # ======================================================

            if income is None and balance is None and cash_flow is None:
                print(f"[银河] 未获取到完整财务数据: " f"{symbol}")
                return None

            # ======================================================
            # 以实际获取到的报表作为基础信息来源
            # ======================================================

            report_date = None
            report_type = None
            currency = None
            announcement_date = None

            if income is not None:
                report_date = income.report_date
                report_type = income.report_type
                currency = income.currency
                announcement_date = income.announcement_date

            elif balance is not None:
                report_date = balance.report_date
                report_type = balance.report_type
                currency = balance.currency
                announcement_date = balance.announcement_date

            elif cash_flow is not None:
                report_date = cash_flow.report_date
                report_type = cash_flow.report_type
                currency = cash_flow.currency
                announcement_date = cash_flow.announcement_date

            # ======================================================
            # 组合 Financial
            # ======================================================

            financial = Financial(
                symbol=symbol,
                report_date=report_date,
                report_type=report_type,
                currency=currency,
                announcement_date=announcement_date,
                source=self.name,
                income=income,
                balance=balance,
                cash_flow=cash_flow,
                # 财务指标由 FinancialAnalyzer 计算
                indicators=None,
            )

            # 计算财务指标
            indicators = self.financial_analyzer.analyze(current=financial)

            financial.indicators = indicators

            return financial

        except Exception as exc:
            print(f"[银河] 获取财务数据失败 " f"{symbol}: {exc}")
            return None

    def _ensure_started(self) -> None:
        """
        确保数据源已经启动。
        """

        if not self._started:
            raise RuntimeError("银河数据源尚未启动，" "请先调用 DataManager.start()")

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

    @staticmethod
    def _first_float(*values: object) -> float | None:
        for value in values:
            result = YinheGateway._to_float(value)

            if result is not None:
                return result

        return None

    @property
    def version(self) -> str:
        try:
            return tgw.GetVersion()
        except Exception:
            return "unknown"
