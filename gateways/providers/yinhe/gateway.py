from __future__ import annotations

import datetime
import os
from typing import Optional

import AmazingData
import pandas
from dotenv import load_dotenv
import tgw

from gateways.gateway import StockDataGateway
from common.constants import Interval, TEN_THOUSAND
from core.models.financial import Financial
from core.models.kline import Kline
from core.models.valuation import Valuation
from core.models.quote import Quote
from core.models.industry import Industry
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
                "username": os.getenv(
                    "amazing_username",
                    "",
                ),
                "password": os.getenv(
                    "amazing_password",
                    "",
                ),
                "host": os.getenv(
                    "amazing_host",
                    "",
                ),
                "port": int(
                    os.getenv(
                        "amazing_port",
                        "0",
                    )
                ),
                "local_path": os.getenv(
                    "local_path",
                    os.path.curdir,
                ),
            }

        try:
            self.user = self.config.get(
                "username",
                "default",
            )

            self.host = self.config.get(
                "host",
                "127.0.0.1",
            )

            self.port = int(
                self.config.get(
                    "port",
                    0,
                )
            )

            self.local_path = self.config.get(
                "local_path",
                os.path.curdir,
            )

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

    # ==========================================================
    # 股票基础信息
    # ==========================================================

    def fetch_stock(
        self,
        symbol: str,
    ):
        """
        获取股票基础信息。

        当前返回：

            {
                "symbol": "...",
                "name": "..."
            }
        """
        return self.stock.fetch_stock(symbol)

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

    # ==========================================================
    # 实时行情
    # ==========================================================

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

        self._ensure_started()

        formatted_symbol = normalize_symbol(symbol)

        try:
            # --------------------------------------------------
            # 1. 获取最近两根日 K 线
            # --------------------------------------------------

            klines = self.fetch_kline(
                symbol=formatted_symbol,
                interval=Interval.DAY_1,
                start_time=(datetime.datetime.now() - pandas.Timedelta(days=30)),
                end_time=datetime.datetime.now(),
                limit=2,
            )

            if not klines:
                print(f"[银河网关] 获取行情失败 " f"{formatted_symbol}: 无 K 线数据")
                return None

            latest = klines[-1]

            previous = klines[-2] if len(klines) >= 2 else None

            # --------------------------------------------------
            # 2. 价格
            # --------------------------------------------------

            price = latest.close

            prev_close = previous.close if previous is not None else None

            # --------------------------------------------------
            # 3. 涨跌
            # --------------------------------------------------

            change = None
            change_percent = None

            if prev_close is not None:

                change = price - prev_close

                if prev_close != 0:

                    change_percent = change / prev_close * 100

            # --------------------------------------------------
            # 4. 股票名称
            # --------------------------------------------------

            stock = self.fetch_stock(formatted_symbol)

            name = None

            if stock:
                name = stock.name

            # --------------------------------------------------
            # 5. 股本
            # --------------------------------------------------

            total_shares = None
            circulating_shares = None
            try:
                equity_structure = self.info_data.get_equity_structure(
                    [formatted_symbol],
                    local_path=self.local_path,
                    is_local=False,
                )

                if equity_structure is not None and not equity_structure.empty:
                    equity_structure = equity_structure.sort_values("CHANGE_DATE")
                    latest_row = equity_structure.iloc[-1]

                    if "TOT_SHARE" in equity_structure.columns:
                        # 原始数据是万为单位
                        total_shares = float(latest_row["TOT_SHARE"]) * TEN_THOUSAND

                    # 如果存在流通股字段，根据实际字段读取。
                    if "FLOAT_SHARE" in equity_structure.columns:
                        circulating_shares = (
                            float(latest_row["FLOAT_SHARE"]) * TEN_THOUSAND
                        )
                    elif "CIRC_SHARE" in equity_structure.columns:
                        circulating_shares = (
                            float(latest_row["CIRC_SHARE"]) * TEN_THOUSAND
                        )
            except Exception as e:
                print(f"[银河网关] 获取股本失败 " f"{formatted_symbol}: {e}")

            # --------------------------------------------------
            # 6. 市值
            # --------------------------------------------------

            # 总市值计算：
            # 总市值 = 总股本 × 当前股价
            # 单位：亿元（取决于 total_shares 和 price 的单位）
            market_cap = None

            # 流通市值计算：
            # 流通市值 = 流通股本 × 当前股价
            # 单位：亿元（取决于 circulating_shares 和 price 的单位）
            circulating_market_cap = None

            if total_shares is not None:
                market_cap = total_shares * price

            if circulating_shares is not None:
                circulating_market_cap = circulating_shares * price

            # --------------------------------------------------
            # 7. 换手率
            # --------------------------------------------------

            turnover = None

            if (
                circulating_shares is not None
                and circulating_shares > 0
                and latest.volume is not None
            ):

                turnover = latest.volume / circulating_shares * 100

            # --------------------------------------------------
            # 8. 均价
            # --------------------------------------------------

            average_price = None

            if (
                latest.volume is not None
                and latest.volume != 0
                and latest.amount is not None
            ):

                average_price = latest.amount / latest.volume

            # --------------------------------------------------
            # 9. 振幅
            # --------------------------------------------------

            amplitude = None
            if prev_close is not None and prev_close != 0:
                amplitude = (latest.high - latest.low) / prev_close * 100

            # --------------------------------------------------
            # 10. 涨跌停
            # --------------------------------------------------

            high_limit = None
            low_limit = None

            # 这里暂时根据前收盘价计算。
            #
            # A 股普通股票：
            #   ±10%
            #
            # 创业板 / 科创板：
            #   ±20%
            #
            # ST：
            #   ±5%
            #
            # 由于当前没有直接获取 ST 状态，
            # 暂不特殊处理 ST。

            if prev_close is not None:

                if formatted_symbol.endswith((".BJ",)):

                    # 北交所通常为 ±30%
                    high_limit = round(
                        prev_close * 1.30,
                        2,
                    )

                    low_limit = round(
                        prev_close * 0.70,
                        2,
                    )

                elif formatted_symbol.startswith(
                    (
                        "300",
                        "301",
                        "688",
                        "689",
                    )
                ):

                    high_limit = round(
                        prev_close * 1.20,
                        2,
                    )

                    low_limit = round(
                        prev_close * 0.80,
                        2,
                    )

                else:

                    high_limit = round(
                        prev_close * 1.10,
                        2,
                    )

                    low_limit = round(
                        prev_close * 0.90,
                        2,
                    )

            # --------------------------------------------------
            # 11. PE
            # --------------------------------------------------

            pe_ttm = self._calculate_pe(
                formatted_symbol,
                "TTM",
                market_cap,
            )

            pe_dynamic = self._calculate_pe(
                formatted_symbol,
                "DYNAMIC",
                market_cap,
            )

            # --------------------------------------------------
            # 12. Quote
            # --------------------------------------------------

            return Quote(
                symbol=formatted_symbol,
                name=name,
                timestamp=latest.timestamp,
                price=price,
                prev_close=prev_close,
                open=latest.open,
                high=latest.high,
                low=latest.low,
                change=change,
                change_percent=change_percent,
                volume=latest.volume,
                amount=latest.amount,
                turnover=turnover,
                volume_ratio=None,
                total_shares=total_shares,
                circulating_shares=circulating_shares,
                market_cap=market_cap,
                circulating_market_cap=circulating_market_cap,
                pe_dynamic=pe_dynamic,
                pe_ttm=pe_ttm,
                pb=None,
                high_limit=high_limit,
                low_limit=low_limit,
                average_price=average_price,
                amplitude=amplitude,
            )

        except Exception as e:

            print(f"[银河网关] 获取行情失败 " f"{formatted_symbol}: {e}")

            return None

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

    # ==========================================================
    # K 线
    # ==========================================================

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

    # ==========================================================
    # 财务数据
    # ==========================================================

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
        return self.financial.fetch_financial(symbol)

    # ==========================================================
    # 估值
    # ==========================================================

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

        self._ensure_started()

        formatted_symbol = normalize_symbol(symbol)

        print(f"[{formatted_symbol}] " f"正在获取估值数据...")

        # ------------------------------------------------------
        # 获取最近 K 线
        # ------------------------------------------------------

        klines = self.fetch_kline(
            symbol=formatted_symbol,
            interval=Interval.DAY_1,
            start_time=(datetime.datetime.now() - pandas.Timedelta(days=30)),
            end_time=datetime.datetime.now(),
            limit=30,
        )

        if not klines:

            return Valuation(
                symbol=formatted_symbol,
                timestamp=datetime.datetime.now(),
            )

        current_price = klines[-1].close

        # ------------------------------------------------------
        # 获取总市值
        # ------------------------------------------------------

        total_shares = None
        circulating_shares = None
        try:
            equity_structure = self.info_data.get_equity_structure(
                [formatted_symbol],
                local_path=self.local_path,
                is_local=False,
            )

            if equity_structure is not None and not equity_structure.empty:
                equity_structure = equity_structure.sort_values("CHANGE_DATE")
                latest_row = equity_structure.iloc[-1]

                if "TOT_SHARE" in equity_structure.columns:
                    # 原始数据是万为单位
                    total_shares = float(latest_row["TOT_SHARE"]) * TEN_THOUSAND

                # 如果存在流通股字段，根据实际字段读取。
                if "FLOAT_SHARE" in equity_structure.columns:
                    circulating_shares = (
                        float(latest_row["FLOAT_SHARE"]) * TEN_THOUSAND
                    )
                elif "CIRC_SHARE" in equity_structure.columns:
                    circulating_shares = (
                        float(latest_row["CIRC_SHARE"]) * TEN_THOUSAND
                    )
        except Exception as e:
            print(f"[银河网关] 获取股本失败 " f"{formatted_symbol}: {e}")

        # 总市值计算：
        # 总市值 = 总股本 × 当前股价
        # 单位：亿元（取决于 total_shares 和 current_price 的单位）
        market_cap = None

        # 流通市值计算：
        # 流通市值 = 流通股本 × 当前股价
        # 单位：亿元（取决于 circulating_shares 和 current_price 的单位）
        circulating_market_cap = None

        if total_shares is not None:
            market_cap = total_shares * current_price

        if circulating_shares is not None:
            circulating_market_cap = circulating_shares * current_price

        # ------------------------------------------------------
        # 计算 PE
        # ------------------------------------------------------

        pe_ttm = self._calculate_pe(
            formatted_symbol,
            "TTM",
            market_cap,
        )

        pe_static = self._calculate_pe(
            formatted_symbol,
            "STATIC",
            market_cap,
        )

        pe_dynamic = self._calculate_pe(
            formatted_symbol,
            "DYNAMIC",
            market_cap,
        )

        # ------------------------------------------------------
        # 统一成 Valuation
        # ------------------------------------------------------

        return Valuation(
            symbol=formatted_symbol,
            timestamp=datetime.datetime.now(),
            price=current_price,
            market_cap=market_cap,
            circulating_market_cap=circulating_market_cap,
            pe_static=pe_static,
            pe_dynamic=pe_dynamic,
            pe_ttm=pe_ttm,
        )

    # ==========================================================
    # PE
    # ==========================================================

    def _calculate_pe(
        self,
        symbol: str,
        pe_type: str,
        market_cap: Optional[float] = None,
    ) -> float:
        """
        计算 PE。

        支持：

            TTM
            STATIC
            DYNAMIC
        """

        formatted_symbol = normalize_symbol(symbol)

        try:

            print(f"[{formatted_symbol}] " f"正在计算 PE({pe_type})...")

            # --------------------------------------------------
            # 1. 获取利润表
            # --------------------------------------------------

            financials_dict = self.info_data.get_income(
                code_list=[formatted_symbol],
                local_path=self.local_path,
                is_local=False,
                begin_date="20220101",
                end_date=self.calendar[-1],
            )

            if financials_dict is None:
                return float("nan")

            df = financials_dict.get(formatted_symbol)

            if df is None or df.empty:

                print(f"[{formatted_symbol}] " f"未能获取有效利润表")

                return float("nan")

            profit_field = "NET_PRO_EXCL_MIN_INT_INC"

            period_field = "REPORTING_PERIOD"

            profit_data = df.set_index(df[period_field].astype(str))[
                profit_field
            ].to_dict()

            # --------------------------------------------------
            # 2. 获取总股本
            # --------------------------------------------------

            equity_structure = self.info_data.get_equity_structure(
                [formatted_symbol],
                local_path=self.local_path,
                is_local=False,
            )

            total_share = 0

            if equity_structure is not None and not equity_structure.empty:

                equity_structure = equity_structure.sort_values("CHANGE_DATE")

                latest_row = equity_structure.iloc[-1]

                total_share = float(latest_row["TOT_SHARE"])

            # --------------------------------------------------
            # 3. 如果没有传入市值，则自己计算
            # --------------------------------------------------

            if market_cap is None:

                klines = self.fetch_kline(
                    symbol=formatted_symbol,
                    interval=Interval.DAY_1,
                    start_time=(datetime.datetime.now() - pandas.Timedelta(days=30)),
                    end_time=datetime.datetime.now(),
                    limit=30,
                )

                if not klines:
                    return float("nan")

                current_price = klines[-1].close

                market_cap = total_share * current_price / 10000

            # --------------------------------------------------
            # 4. 找到最新可用财报
            # --------------------------------------------------

            now = datetime.datetime.now()

            q_map = {
                1: "0331",
                2: "0630",
                3: "0930",
                4: "1231",
            }

            target_period = None
            q_num = 0

            for i in range(1, 7):

                dt = now - datetime.timedelta(days=i * 90)

                for q in [4, 3, 2, 1]:

                    period_key = f"{dt.year}" f"{q_map[q]}"

                    if period_key in profit_data and not pandas.isna(
                        profit_data[period_key]
                    ):

                        target_period = period_key

                        q_num = q

                        break

                if target_period:
                    break

            if not target_period:
                return float("nan")

            # --------------------------------------------------
            # 5. 计算
            # --------------------------------------------------

            current_report_year = int(target_period[:4])

            base_year = current_report_year - 1

            curr_q_cum = profit_data.get(
                target_period,
                0,
            )

            last_full_year = profit_data.get(
                f"{base_year}1231",
                0,
            )

            prev_q_cum = profit_data.get(
                f"{base_year}" f"{q_map[q_num]}",
                0,
            )

            requested_type = pe_type.upper()

            # --------------------------------------------------
            # TTM PE
            # --------------------------------------------------

            if requested_type == "TTM":

                profit_ttm = curr_q_cum + (last_full_year - prev_q_cum)

                if profit_ttm > 0:

                    return round(
                        market_cap / (profit_ttm / 1e8),
                        2,
                    )

            # --------------------------------------------------
            # 静态 PE
            # --------------------------------------------------

            elif requested_type in (
                "STATIC",
                "LYR",
            ):

                if last_full_year > 0:

                    return round(
                        market_cap / (last_full_year / 1e8),
                        2,
                    )

            # --------------------------------------------------
            # 动态 PE
            # --------------------------------------------------

            elif requested_type in (
                "DYNAMIC",
                "FORWARD",
            ):

                if q_num > 0 and curr_q_cum > 0:

                    annual_profit = curr_q_cum / q_num * 4

                    return round(
                        market_cap / (annual_profit / 1e8),
                        2,
                    )

            return float("nan")

        except Exception as e:

            print(f"[{formatted_symbol}] " f"计算 PE({pe_type}) 出错: {e}")

            return float("nan")

    # ==========================================================
    # 市值
    # ==========================================================

    def _fetch_market_cap(
        self,
        symbol: str,
        current_price: float,
    ) -> Optional[float]:
        """
        获取当前总市值。

        返回单位：

            亿元
        """

        try:

            equity_structure = self.info_data.get_equity_structure(
                [symbol],
                local_path=self.local_path,
                is_local=False,
            )

            if equity_structure is None or equity_structure.empty:

                return None

            equity_structure = equity_structure.sort_values("CHANGE_DATE")

            latest_row = equity_structure.iloc[-1]

            total_share = float(latest_row["TOT_SHARE"])

            market_cap = total_share * current_price / 10000

            return round(
                market_cap,
                2,
            )

        except Exception as e:

            print(f"[银河网关] 获取市值失败 " f"{symbol}: {e}")

            return None

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

    def _ensure_started(self) -> None:
        """
        确保数据源已经启动。
        """

        if not self._started:

            raise RuntimeError("银河数据源尚未启动，" "请先调用 DataManager.start()")

    @property
    def version(self) -> str:
        try:
            return tgw.GetVersion()
        except Exception:
            return "unknown"
