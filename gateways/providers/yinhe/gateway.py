from __future__ import annotations

import datetime
import os
from typing import Any, Optional

import pandas
import AmazingData

from base import StockDataGateway
from models.constants import Interval
from models.kline import Kline
from models.valuation import Valuation
from registry import GatewayRegistry


@GatewayRegistry.register("yinhe")
class YinheGateway(StockDataGateway):
    """
    银河证券数据网关。

    负责将 AmazingData 数据接口适配到统一的
    StockDataGateway 接口。

    上层业务只依赖 StockDataGateway，
    不应该直接依赖 AmazingData。

    数据流：

        DataManager
            ↓
        StockDataGateway
            ↓
        YinheGateway
            ↓
        AmazingData
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

        Parameters
        ----------
        config:
            登录配置。

        Returns
        -------
        bool
            登录成功返回 True，否则返回 False。
        """

        if config:
            self.config.update(config)

        try:
            self.user = self.config.get(
                "username",
                "",
            )

            self.host = self.config.get(
                "host",
                "",
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
                f"{self.host}:{self.port} "
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
            print("[银河网关] 端口格式无效，" "请检查配置。")

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

        Returns
        -------
        bool
            True 表示已经启动。
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

        注意：

        这里不再使用 StockDetail。

        由于当前项目提供的 Stock 模型字段尚未给出，
        因此这里暂时不强行构造一个未知的数据模型。

        等 Stock 模型确定后，只需要在这里完成：

            AmazingData
                ↓
            Stock

        的转换即可。
        """

        self._ensure_started()

        formatted_symbol = self._normalize_symbol(symbol)

        try:
            stock_basic = self.info_data.get_stock_basic([formatted_symbol])

            if stock_basic is None:
                return None

            # DataFrame
            if hasattr(
                stock_basic,
                "empty",
            ):

                if stock_basic.empty:
                    return None

                row = stock_basic.iloc[0]

                return {
                    "symbol": formatted_symbol,
                    "name": row.get("SECURITY_NAME"),
                }

            # List[Dict]
            if isinstance(
                stock_basic,
                list,
            ):

                if not stock_basic:
                    return None

                item = stock_basic[0]

                return {
                    "symbol": formatted_symbol,
                    "name": item.get("SECURITY_NAME"),
                }

            return None

        except Exception as e:

            print(f"[银河网关] 获取股票基础信息失败 " f"{formatted_symbol}: {e}")

            return None

    def fetch_stock_name(
        self,
        symbol: str,
    ) -> str:
        """
        获取股票名称。

        这是银河数据源内部辅助方法。

        不使用 StockDetail。
        """

        self._ensure_started()

        formatted_symbol = self._normalize_symbol(symbol)

        try:
            stock_basic = self.info_data.get_stock_basic([formatted_symbol])

            # DataFrame
            if hasattr(
                stock_basic,
                "empty",
            ):

                if not stock_basic.empty:

                    return stock_basic["SECURITY_NAME"].iloc[0]

            # List[Dict]
            elif isinstance(
                stock_basic,
                list,
            ):

                if stock_basic:

                    return stock_basic[0].get(
                        "SECURITY_NAME",
                        "未知名称",
                    )

            return "未知名称"

        except Exception as e:

            print(f"[银河网关] 获取股票名称失败 " f"{formatted_symbol}: {e}")

            return "获取失败"

    # ==========================================================
    # 实时行情
    # ==========================================================

    def fetch_quote(
        self,
        symbol: str,
    ):
        """
        获取单只股票最新行情。

        当前 AmazingData 的实时行情接口
        尚未在现有代码中提供，因此暂不猜测
        AmazingData 的接口名称和返回字段。
        """

        self._ensure_started()

        raise NotImplementedError(
            "YinheGateway.fetch_quote() " "尚未接入银河证券实时行情接口"
        )

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
        interval: Interval,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 10000,
    ) -> list[Kline]:
        """
        获取历史 K 线。

        AmazingData 原始数据：

            DataFrame

        转换为：

            list[Kline]
        """

        self._ensure_started()

        # ------------------------------------------------------
        # 1. 周期映射
        # ------------------------------------------------------

        period_map = {
            Interval.MINUTE_1: AmazingData.constant.Period.min1.value,
            Interval.MINUTE_5: AmazingData.constant.Period.min5.value,
            Interval.MINUTE_15: AmazingData.constant.Period.min15.value,
            Interval.MINUTE_30: AmazingData.constant.Period.min30.value,
            Interval.HOUR_1: AmazingData.constant.Period.min60.value,
            Interval.DAY_1: AmazingData.constant.Period.day.value,
            Interval.WEEK_1: AmazingData.constant.Period.week.value,
        }

        period = period_map.get(
            interval,
            AmazingData.constant.Period.day.value,
        )

        # ------------------------------------------------------
        # 2. 股票代码标准化
        # ------------------------------------------------------

        code = self._normalize_symbol(symbol)

        # ------------------------------------------------------
        # 3. 日期处理
        # ------------------------------------------------------

        today_str = datetime.datetime.now().strftime("%Y%m%d")

        begin_str = start_time.strftime("%Y%m%d") if start_time else today_str

        end_str = end_time.strftime("%Y%m%d") if end_time else today_str

        # ------------------------------------------------------
        # 4. 查询数据
        # ------------------------------------------------------

        try:

            kline_dict = self.market_data.query_kline(
                [code],
                period=period,
                begin_date=int(begin_str),
                end_date=int(end_str),
            )

            df = kline_dict.get(code)

            if df is None:

                print(f"[银河网关] " f"{code} 无返回数据")

                return []

            if hasattr(df, "empty") and df.empty:

                print(f"[银河网关] " f"{code} 返回数据为空")

                return []

            # --------------------------------------------------
            # DataFrame → List[Dict]
            # --------------------------------------------------

            if hasattr(
                df,
                "to_dict",
            ):

                raw_bars = df.to_dict("records")

            else:

                raw_bars = df

            # --------------------------------------------------
            # limit
            # --------------------------------------------------

            if limit and len(raw_bars) > limit:

                raw_bars = raw_bars[-limit:]

        except Exception as e:

            print(f"[银河网关] " f"query_kline 查询失败: {e}")

            return []

        # ------------------------------------------------------
        # 5. 转换成统一 Kline
        # ------------------------------------------------------

        klines: list[Kline] = []

        for item in raw_bars:

            try:

                kline_time = item.get("kline_time")

                if hasattr(
                    kline_time,
                    "to_pydatetime",
                ):

                    kline_time = kline_time.to_pydatetime()

                klines.append(
                    Kline(
                        code=code,
                        trade_time=kline_time,
                        open=float(item["open"]),
                        high=float(item["high"]),
                        low=float(item["low"]),
                        close=float(item["close"]),
                        volume=int(item["volume"]),
                        amount=float(item["amount"]),
                    )
                )

            except Exception as e:

                print(f"[银河网关] " f"转换 Kline 失败: {e}")

                print(f"    原始数据: {item}")

                continue

        return klines

    # ==========================================================
    # 估值
    # ==========================================================

    def fetch_valuation(
        self,
        symbol: str,
    ) -> Valuation:
        """
        获取股票估值数据。

        返回统一的 Valuation。

        包括：

            当前价格
            总市值
            静态 PE
            动态 PE
            TTM PE

        当前可以进一步扩展：

            PB
            PS
            PEG
            股息率
            EV
            EV/EBITDA
        """

        self._ensure_started()

        formatted_symbol = self._normalize_symbol(symbol)

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

        market_cap = self._fetch_market_cap(
            formatted_symbol,
            current_price,
        )

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

        注意：

        这里是 YinheGateway 内部实现，
        不作为 StockDataGateway 的公共接口。
        """

        formatted_symbol = self._normalize_symbol(symbol)

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

                total_share = latest_row["TOT_SHARE"]

            # --------------------------------------------------
            # 3. 如果没有传入市值，则自己计算
            # --------------------------------------------------

            if market_cap is None:

                klines = self.fetch_kline(
                    symbol=formatted_symbol,
                    interval=Interval.DAY_1,
                    start_time=(datetime.datetime.now() - pandas.Timedelta(days=30)),
                    end_time=(datetime.datetime.now()),
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

                for q in [
                    4,
                    3,
                    2,
                    1,
                ]:

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

    # ==========================================================
    # 工具方法
    # ==========================================================

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """
        标准化股票代码。

        支持：

            600519
            600519.SH
            000001
            000001.SZ
            300750
            688981
        """

        symbol = symbol.strip().upper()

        # 已经带交易所后缀
        if "." in symbol:
            return symbol

        # 上海证券交易所
        if symbol.startswith(("600", "601", "603", "605", "688", "689")):
            return f"{symbol}.SH"

        # 深圳证券交易所
        if symbol.startswith(("000", "001", "002", "003", "300", "301")):
            return f"{symbol}.SZ"

        # 北京证券交易所
        if symbol.startswith(("4", "8")):
            return f"{symbol}.BJ"

        # 无法判断时直接返回原代码
        return symbol

    def _ensure_started(self) -> None:
        """
        确保数据源已经启动。
        """

        if not self._started:

            raise RuntimeError("银河数据源尚未启动，" "请先调用 DataManager.start()")



def main() -> None:
    """
    银河证券数据网关测试入口。

    测试内容：

        1. 登录数据源
        2. 检查数据源状态
        3. 股票代码标准化
        4. 获取股票基础信息
        5. 获取股票名称
        6. 获取历史 K 线
        7. 获取估值数据
        8. 注销数据源

    注意：
        需要提前配置真实的银河证券 / AmazingData
        登录信息。
    """

    print()
    print("=" * 72)
    print("银河证券数据网关测试")
    print("=" * 72)

    config = {
        "username": os.getenv(
            "YINHE_USERNAME",
            "",
        ),
        "password": os.getenv(
            "YINHE_PASSWORD",
            "",
        ),
        "host": os.getenv(
            "YINHE_HOST",
            "",
        ),
        "port": int(
            os.getenv(
                "YINHE_PORT",
                "0",
            )
        ),
        "local_path": os.getenv(
            "YINHE_LOCAL_PATH",
            os.path.curdir,
        ),
    }

    gateway = YinheGateway(config)

    try:
        # ======================================================
        # 1. 登录
        # ======================================================

        print()
        print("[1/7] 登录数据源")

        if not gateway.login():
            print("❌ 银河数据源登录失败")
            return

        print("✅ 银河数据源登录成功")

        # ======================================================
        # 2. 健康检查
        # ======================================================

        print()
        print("[2/7] 健康检查")

        if gateway.health_check():
            print("✅ 数据源运行正常")
        else:
            print("❌ 数据源未启动")
            return

        # ======================================================
        # 3. 测试股票代码标准化
        # ======================================================

        print()
        print("[3/7] 股票代码标准化")

        test_symbols = [
            "600519",
            "600519.SH",
            "000001",
            "000001.SZ",
            "300750",
            "688981",
        ]

        for symbol in test_symbols:
            normalized = gateway._normalize_symbol(symbol)

            print(
                f"    {symbol:<12} -> {normalized}"
            )

        # ======================================================
        # 4. 获取股票基础信息
        # ======================================================

        symbol = "600519"

        print()
        print(f"[4/7] 获取股票基础信息: {symbol}")

        stock = gateway.fetch_stock(symbol)

        if stock is None:
            print("❌ 未获取到股票基础信息")
        else:
            print("✅ 股票基础信息:")
            print(f"    代码: {stock.get('symbol')}")
            print(f"    名称: {stock.get('name')}")

        # ======================================================
        # 5. 获取股票名称
        # ======================================================

        print()
        print(f"[5/7] 获取股票名称: {symbol}")

        name = gateway.fetch_stock_name(symbol)

        print(
            f"    股票名称: {name}"
        )

        # ======================================================
        # 6. 获取历史 K 线
        # ======================================================

        print()
        print(f"[6/7] 获取历史 K 线: {symbol}")

        end_time = datetime.datetime.now()

        start_time = end_time - datetime.timedelta(
            days=30
        )

        klines = gateway.fetch_kline(
            symbol=symbol,
            interval=Interval.DAY_1,
            start_time=start_time,
            end_time=end_time,
            limit=10,
        )

        if not klines:
            print("❌ 未获取到 K 线数据")
        else:
            print(
                f"✅ 获取到 {len(klines)} 条 K 线"
            )

            print()

            for kline in klines:
                print(
                    f"    {kline.trade_time} "
                    f"O={kline.open:.2f} "
                    f"H={kline.high:.2f} "
                    f"L={kline.low:.2f} "
                    f"C={kline.close:.2f} "
                    f"V={kline.volume}"
                )

        # ======================================================
        # 7. 获取估值
        # ======================================================

        print()
        print(f"[7/7] 获取估值数据: {symbol}")

        valuation = gateway.fetch_valuation(symbol)

        print("✅ 估值数据:")

        print(
            f"    代码      : {valuation.symbol}"
        )

        print(
            f"    时间      : {valuation.timestamp}"
        )

        print(
            f"    当前价格  : {valuation.price}"
        )

        print(
            f"    总市值    : {valuation.market_cap}"
        )

        print(
            f"    静态 PE   : {valuation.pe_static}"
        )

        print(
            f"    动态 PE   : {valuation.pe_dynamic}"
        )

        print(
            f"    TTM PE    : {valuation.pe_ttm}"
        )

        print()
        print("=" * 72)
        print("✅ 银河证券数据网关测试完成")
        print("=" * 72)

    except KeyboardInterrupt:

        print()
        print("⚠️ 用户中断测试")

    except Exception as e:

        print()
        print(f"❌ 测试过程中发生异常: {e}")

        import traceback

        traceback.print_exc()

    finally:

        print()
        print("正在注销银河数据源...")

        gateway.logout()

        print("银河数据源已注销")


if __name__ == "__main__":
    main()
