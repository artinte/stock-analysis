import datetime
import os
from typing import List, Optional
import pandas
from gateways.broker_gateway import BrokerGateway
from models.constants import Interval
from models.kline import Kline
from stock_detail import StockDetail
from utils_func import add_exchange_suffix
import AmazingData


class AmazingDataGateway(BrokerGateway):
    def __init__(self):
        self._is_connected = False
        self._user = ""
        self._host = ""
        self._port = 0

        self.info_data = None
        self.base_data = None
        self.calendar = None
        self.market_data = None

    def login(self, config: dict) -> bool:
        self.user = config.get("username")
        self.host = config.get("host")
        self.port = int(config.get("port", 0))  # 强制转为整数
        self.local_path = config.get("local_path", os.path.curdir)  # 可选的本地路径
        print(f"[银河网关] 尝试登录: {self.host}:{self.port} 用户: {self.user}")
        try:
            AmazingData.login(
                username=config["username"],
                password=config["password"],
                host=config["host"],
                port=int(config["port"]),
            )

            self.info_data = AmazingData.InfoData()
            self.base_data = AmazingData.BaseData()
            self.calendar = self.base_data.get_calendar()
            self.market_data = AmazingData.MarketData(self.calendar)

            self._is_connected = True
            print("登录成功")
            return True
        except ValueError:
            print("[错误] 端口格式无效，请检查配置。")
            return False
        except Exception as e:
            print(f"[错误] 登录异常: {e}")
            return False

    def fetch_kline(
        self,
        symbol: str,
        interval: Interval,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 10000,
    ) -> List[Kline]:
        """
        实现获取 K 线数据的逻辑
        """
        if not self._is_connected:
            raise ConnectionError("请先执行 login() 成功后再获取数据")

        # 1. 周期映射
        period_map = {
            Interval.MINUTE_1: AmazingData.constant.Period.min1.value,
            Interval.MINUTE_5: AmazingData.constant.Period.min5.value,
            Interval.MINUTE_15: AmazingData.constant.Period.min15.value,
            Interval.MINUTE_30: AmazingData.constant.Period.min30.value,
            Interval.HOUR_1: AmazingData.constant.Period.min60.value,
            Interval.DAY_1: AmazingData.constant.Period.day.value,
            Interval.WEEK_1: AmazingData.constant.Period.week.value,
        }
        period = period_map.get(interval, AmazingData.constant.Period.day.value)

        # 2. 代码标准化
        code = add_exchange_suffix(symbol)

        # 3. 日期处理：如果没有提供则默认取今天
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        begin_str = start_time.strftime("%Y%m%d") if start_time else today_str
        end_str = end_time.strftime("%Y%m%d") if end_time else today_str

        # 5. 执行查询
        try:
            # 根据你之前的描述，query_kline 接受 list 格式的代码并返回字典
            kline_dict = self.market_data.query_kline(
                [code], period=period, begin_date=int(begin_str), end_date=int(end_str)
            )

            df = kline_dict.get(code)

            # 检查数据是否存在
            if df is None or (hasattr(df, "empty") and df.empty):
                print(f"DEBUG: {code} 无返回数据")
                return []

            # --- 关键：将 DataFrame 转化为字典列表，这样 item 才是每一行的数据字典 ---
            if hasattr(df, "to_dict"):
                raw_bars = df.to_dict("records")
            else:
                raw_bars = df

            # 如果本地有 limit 要求，进行末尾切片
            if limit and len(raw_bars) > limit:
                raw_bars = raw_bars[-limit:]

        except Exception as e:
            print(f"[数据错误] query_kline 查询失败: {e}")
            return []

        # 6. 解析数据为 Kline 对象
        klines = []
        for item in raw_bars:
            try:
                t_time = item.get("kline_time")
                if hasattr(t_time, "to_pydatetime"):
                    t_time = t_time.to_pydatetime()
                klines.append(
                    Kline(
                        code=code,
                        trade_time=t_time,
                        open=float(item["open"]),
                        high=float(item["high"]),
                        low=float(item["low"]),
                        close=float(item["close"]),
                        volume=int(item["volume"]),
                        amount=float(item["amount"]),
                    )
                )
            except Exception as e:
                print(f"DEBUG: 转换单条 Kline 失败: {e}, 数据内容: {item}")
                continue

        return klines

    def fetch_market_data(self, symbol):
        if not self._is_connected:
            raise ConnectionError("请先执行 login() 成功后再获取数据")

        stock = StockDetail(code=symbol)
        return stock

    def fetch_stock_name(self, symbol):
        # 1. 格式化代码
        formatted_symbol = symbol if "." in symbol else add_exchange_suffix(symbol)

        try:
            # 2. 传入列表获取基础数据
            stock_basic = self.info_data.get_stock_basic([formatted_symbol])

            # 3. 处理返回结果
            # 如果返回的是 DataFrame (常见情况)
            if hasattr(stock_basic, "empty"):
                if not stock_basic.empty:
                    # 假设返回的行索引或第一行就是我们要的数据
                    return stock_basic["SECURITY_NAME"].iloc[0]

            # 如果返回的是 List[Dict]
            elif isinstance(stock_basic, list) and len(stock_basic) > 0:
                return stock_basic[0].get("SECURITY_NAME", "未知名称")

            return "未知名称"

        except Exception as e:
            print(f"DEBUG: 获取失败 {formatted_symbol}, 错误: {e}")
            return "获取失败"

    def fetch_pe(self, symbol: str, pe_type: str = "TTM") -> float:
        """
        通过原始财报数据流计算并获取指定股票的 PE (针对 2026年 环境优化版)
        :param symbol: 股票代码
        :param pe_type: 'TTM' (滚动), 'STATIC' (静态), 'DYNAMIC' (动态)
        """
        if not self._is_connected:
            raise ConnectionError("请先执行 login() 成功后再获取数据")

        formatted_symbol = symbol if "." in symbol else add_exchange_suffix(symbol)
        print(format(f"[{formatted_symbol}] 正在计算 PE({pe_type})..."))
        # 1. 获取利润表数据
        financials_dict = self.info_data.get_income(
            code_list=[formatted_symbol],
            local_path=self.local_path if hasattr(self, "local_path") else None,
            is_local=False,
            begin_date="20220101",
            end_date=self.calendar[-1],
        )

        df = financials_dict.get(formatted_symbol)
        if df is None or df.empty:
            print(f"[{formatted_symbol}] 未能获取到有效的利润表数据")
            return float("nan")

        PROFIT_FIELD = "NET_PRO_EXCL_MIN_INT_INC"
        PERIOD_FIELD = "REPORTING_PERIOD"

        profit_data = df.set_index(df[PERIOD_FIELD].astype(str))[PROFIT_FIELD].to_dict()

        # 💡 2. 核心前置条件：获取当前的总市值（单位：亿元）
        equity_structure = self.info_data.get_equity_structure(
            [formatted_symbol], local_path=self.local_path, is_local=False
        )

        # 获取总市值
        total_share = 0
        if not equity_structure.empty:
            equity_structure = equity_structure.sort_values("CHANGE_DATE")
            latest_row = equity_structure.iloc[-1]
            total_share = latest_row["TOT_SHARE"]
            print(f"[{formatted_symbol}] 成功获取到总股本: {total_share} 股")
        else:
            print(f"[{formatted_symbol}] 未能获取到有效的股本结构数据")

        klines = self.fetch_kline(
            symbol=formatted_symbol,
            interval=Interval.DAY_1,
            start_time=datetime.datetime.now() - pandas.Timedelta(days=30),
            end_time=datetime.datetime.now(),
            limit=30,
        )

        df_kline = pandas.DataFrame(
            [
                {"o": k.open, "h": k.high, "l": k.low, "c": k.close, "v": k.volume}
                for k in klines
            ]
        )

        cap = round((total_share * df_kline["c"].iloc[-1]) / 10000, 2)
        print(f"[{formatted_symbol}] 当前总市值约为: {cap} 亿元")

        # 4. 动态回溯寻找“最新可用季报” (针对当前 2026年 时间线优化)
        now = datetime.datetime.now()
        q_map = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}
        target_period = None
        q_num = 0

        for i in range(1, 7):
            dt = now - datetime.timedelta(days=i * 90)
            for q in [4, 3, 2, 1]:
                period_key = f"{dt.year}{q_map[q]}"
                if period_key in profit_data and not pandas.isna(
                    profit_data[period_key]
                ):
                    target_period = period_key
                    q_num = q
                    break
            if target_period:
                break

        if not target_period:
            print(f"[{formatted_symbol}] 未能找到可用历史财报数据周期")
            return float("nan")
        else:
            print(f"[{formatted_symbol}] 最新可用财报周期: {target_period} (Q{q_num})")
            # 打印最近四个季度的利润数据，方便调试
            print(f"[{formatted_symbol}] 最近四个季度利润数据:")
            for period, profit in list(profit_data.items())[:4]:  # 只显示最近四个季度
                print(f"  {period}: {profit}")

        try:
            # 5. 确定参照年份
            current_report_year = int(target_period[:4])
            base_year = current_report_year - 1

            # A. 本期累计净利润 (如 2025-Q3)
            curr_q_cum = profit_data.get(target_period, 0)
            # B. 基准年全年净利润 (如 2024-12-31)
            last_full_year = profit_data.get(f"{base_year}1231", 0)
            # C. 基准年同期净利润 (如 2024-Q3)
            prev_q_cum = profit_data.get(f"{base_year}{q_map[q_num]}", 0)

            # 6. 根据请求的 pe_type 计算并返回对应的 PE 结果
            requested_type = pe_type.upper()

            if requested_type == "TTM":
                # TTM 利润 = 本期累计 + (基准年全年 - 基准年同期)
                profit_ttm_yuan = curr_q_cum + (last_full_year - prev_q_cum)
                if profit_ttm_yuan > 0:
                    return round(cap / (profit_ttm_yuan / 1e8), 2)

            elif requested_type in ["STATIC", "LYR"]:
                # 静态 PE 使用上一年度全年利润
                if last_full_year > 0:
                    return round(cap / (last_full_year / 1e8), 2)

            elif requested_type in ["DYNAMIC", "FORWARD"]:
                # 动态 PE (按当前季度进度线性外推全年)
                if q_num > 0 and curr_q_cum > 0:
                    return round(cap / ((curr_q_cum / q_num * 4) / 1e8), 2)

            return float("nan")

        except Exception as e:
            print(f"[{formatted_symbol}] 动态计算 PE({pe_type}) 出错: {e}")
            return float("nan")

    def logout(self):
        if self._is_connected:
            AmazingData.logout(self.user)
