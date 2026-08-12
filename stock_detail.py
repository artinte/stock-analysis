import datetime
import numpy as np
import pandas
from company_financials import CompanyFinancials


class StockDetail:
    def __init__(self, code, name=""):
        self.name = name
        self.code = code
        self.update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. 价格与涨跌（核心波动）
        self.price = 0.0  # 当前价格（收盘价）
        self.last_close = 0.0  # 昨日收盘价格
        self.open = 0.0  # 开盘价
        self.high = 0.0  # 最高价
        self.low = 0.0  # 最低价

        # 2. 市值属性
        self.total_cap = 0.0  # 总市值 （亿元）
        self.float_cap = 0.0  # 流通市值（亿元）
        self.total_shares = 0.0  # 总股本（万股）
        self.float_shares = 0.0  # 流通股本（万股）

        # 3. 估值与运行指标
        self.pe_ttm = 0.0
        self.pe_dynamic = 0.0
        self.pe_static = 0.0
        self.ps = 0.0  # 市销率 TTM
        self.pb = 0.0  # 市净率

        self.profit_growth_rate = 0.0  # 利润增长率 (%)

        self.vol_ratio = 0.0  # 量比
        self.turnover = 0.0  # 换手率 (%)
        self.amount = 0.0  # 成交额（亿元）
        self.volume = 0.0  # 成交量（手）

        # 4. 扩展维度与经典技术指标
        self.total_revenue = 0.0  # 营业总收入（亿元）
        self.revenue_growth_rate = 0.0  # 营收增长率 (%)

        self.ma_dict = {}  # 存储不同周期的均价
        self.williams = 0.0  # 威廉指标 (14)
        self.bias = 0.0  # 乖离率 (MA5)

        # 新增技术指标存储
        self.macd_dif = 0.0  # MACD 快线
        self.macd_dea = 0.0  # MACD 慢线 (Signal)
        self.macd_hist = 0.0  # MACD 柱状值
        self.rsi_14 = 0.0  # RSI (14日)
        self.boll_upper = 0.0  # 布林线上轨
        self.boll_mid = 0.0  # 布林线中轨 (MA20)
        self.boll_lower = 0.0  # 布林线下轨

    @property
    def change(self):
        return round(self.price - self.last_close, 3)

    @property
    def change_pct(self):
        if self.last_close == 0:
            return 0.0
        return round((self.change / self.last_close) * 100, 2)

    def calculate_pe_from_financials(self, financials: CompanyFinancials):
        assert self.total_cap > 0
        data = financials.financial_data
        if not data:
            return

        now = datetime.datetime.now()
        curr_year = now.year
        start_q_idx = (now.month - 1) // 3

        target_q = None
        q_num = 0

        for i in range(4):
            check_idx = start_q_idx - i
            year = curr_year if check_idx >= 0 else curr_year - 1
            q_val = (check_idx % 4) + 1
            if q_val == 4:
                q_val = 3

            q_key = f"{year}-Q{q_val}"
            if q_key in data:
                target_q = q_key
                q_num = q_val
                break

        if not target_q:
            return

        year_str = target_q.split("-")[0]
        prev_year = int(year_str) - 1

        curr_q_cum = data.get(target_q, {}).get("operating_profit", 0)
        last_full_year = data.get(f"{prev_year}-Q4", {}).get("operating_profit", 0)
        prev_q_cum = data.get(f"{prev_year}-Q{q_num}", {}).get("operating_profit", 0)

        profit_ttm = curr_q_cum + (last_full_year - prev_q_cum)
        if profit_ttm > 0:
            self.pe_ttm = round(self.total_cap / (profit_ttm / 1e8), 2)

        if last_full_year > 0:
            self.pe_static = round(self.total_cap / (last_full_year / 1e8), 2)

        if curr_q_cum > 0 and q_num > 0:
            projected_profit = (curr_q_cum / q_num) * 4
            self.pe_dynamic = round(self.total_cap / (projected_profit / 1e8), 2)

    def calculate_pe(self, financials_dict: dict):
        if not hasattr(self, "total_cap") or self.total_cap <= 0:
            return

        df = financials_dict.get(self.code)
        if df is None or df.empty:
            return

        PROFIT_FIELD = "NET_PRO_EXCL_MIN_INT_INC"
        REVENUE_FIELD = "TOT_OPERA_REV"
        PERIOD_FIELD = "REPORTING_PERIOD"
        profit_data = df.set_index(df[PERIOD_FIELD].astype(str))[PROFIT_FIELD].to_dict()
        revenue_data = df.set_index(df[PERIOD_FIELD].astype(str))[
            REVENUE_FIELD
        ].to_dict()

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
            print(f"[{self.code}] 未能找到可用财报数据")
            return

        try:
            current_report_year = int(target_period[:4])
            base_year = current_report_year - 1

            curr_q_cum = profit_data.get(target_period, 0)
            last_full_year = profit_data.get(f"{base_year}1231", 0)
            prev_q_cum = profit_data.get(f"{base_year}{q_map[q_num]}", 0)

            if prev_q_cum and prev_q_cum != 0:
                self.profit_growth_rate = round(
                    ((curr_q_cum - prev_q_cum) / abs(prev_q_cum)) * 100, 2
                )
            else:
                self.profit_growth_rate = 0.0

            curr_rev_cum = revenue_data.get(target_period, 0)
            prev_rev_cum = revenue_data.get(f"{base_year}{q_map[q_num]}", 0)

            self.total_revenue = round(curr_rev_cum / 1e8, 2)
            if prev_rev_cum and prev_rev_cum != 0:
                self.revenue_growth_rate = round(
                    ((curr_rev_cum - prev_rev_cum) / abs(prev_rev_cum)) * 100, 2
                )
            else:
                self.revenue_growth_rate = 0.0

            cap = self.total_cap
            profit_ttm_yuan = curr_q_cum + (last_full_year - prev_q_cum)

            if profit_ttm_yuan > 0:
                self.pe_ttm = round(cap / (profit_ttm_yuan / 1e8), 2)
            else:
                self.pe_ttm = float("nan")

            if last_full_year > 0:
                self.pe_static = round(cap / (last_full_year / 1e8), 2)
            else:
                self.pe_static = float("nan")

            if q_num > 0 and curr_q_cum > 0:
                self.pe_dynamic = round(cap / ((curr_q_cum / q_num * 4) / 1e8), 2)
            else:
                self.pe_dynamic = float("nan")

        except Exception as e:
            print(f"计算 PE 出错: {e}")

    def calculate_ps(self, financials_dict: dict):
        if not hasattr(self, "total_cap") or self.total_cap <= 0:
            return

        df = financials_dict.get(self.code)
        if df is None or df.empty:
            return

        REVENUE_FIELD = "TOT_OPERA_REV"
        PERIOD_FIELD = "REPORTING_PERIOD"
        revenue_data = df.set_index(df[PERIOD_FIELD].astype(str))[
            REVENUE_FIELD
        ].to_dict()

        now = datetime.datetime.now()
        q_map = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}
        target_period = None
        q_num = 0

        for i in range(1, 7):
            dt = now - datetime.timedelta(days=i * 90)
            for q in [4, 3, 2, 1]:
                period_key = f"{dt.year}{q_map[q]}"
                if period_key in revenue_data and not pandas.isna(
                    revenue_data[period_key]
                ):
                    target_period = period_key
                    q_num = q
                    break
            if target_period:
                break

        if not target_period:
            return

        try:
            current_report_year = int(target_period[:4])
            base_year = current_report_year - 1

            curr_rev_cum = revenue_data.get(target_period, 0)
            last_full_rev = revenue_data.get(f"{base_year}1231", 0)
            prev_rev_cum = revenue_data.get(f"{base_year}{q_map[q_num]}", 0)

            rev_ttm_yuan = curr_rev_cum + (last_full_rev - prev_rev_cum)

            if rev_ttm_yuan > 0:
                self.ps = round(self.total_cap / (rev_ttm_yuan / 1e8), 2)
            else:
                self.ps = float("nan")

        except Exception as e:
            print(f"[{self.code}] 计算 PS 出错: {e}")

    def calculate_pb(self, balance_sheet_dict: dict):
        """
        计算市净率 (PB)
        PB = 总市值 / 最新归属于母公司所有者权益(净资产)
        需要传入资产负债表字典，字段通常为 TOT_SHRHLDR_EQY_EXCL_MIN_INT (归母股东权益)
        """
        if not hasattr(self, "total_cap") or self.total_cap <= 0:
            return

        df = balance_sheet_dict.get(self.code)
        if df is None or df.empty:
            return

        EQUITY_FIELD = "TOT_SHRHLDR_EQY_EXCL_MIN_INT"
        PERIOD_FIELD = "REPORTING_PERIOD"

        if EQUITY_FIELD not in df.columns or PERIOD_FIELD not in df.columns:
            return

        df_sorted = df.sort_values(PERIOD_FIELD)
        latest_equity = df_sorted.iloc[-1][EQUITY_FIELD]

        if latest_equity and latest_equity > 0:
            self.pb = round(self.total_cap / (latest_equity / 1e8), 2)
        else:
            self.pb = 0.0

    def update_equity(self, total_share_raw, float_share_raw):
        self.total_shares = total_share_raw
        self.float_shares = float_share_raw

        if self.price > 0:
            self.total_cap = round((self.total_shares * self.price) / 10000, 2)
            self.float_cap = round((self.float_shares * self.price) / 10000, 2)

        if self.float_shares > 0:
            self.turnover = round(self.volume / (self.float_shares * 100), 2)

    def calculate_moving_averages(self, df):
        periods = [3, 5, 10, 20, 30, 60]
        df_sorted = df.sort_index()

        for p in periods:
            if len(df_sorted) >= p:
                avg = df_sorted["close"].tail(p).mean()
                self.ma_dict[f"MA{p}"] = round(avg, 2)
            else:
                self.ma_dict[f"MA{p}"] = None

    def calculate_williams(self, df, n=14):
        if len(df) < n:
            self.williams = 0.0
            return

        recent_n = df.tail(n)
        hn = recent_n["high"].max()
        ln = recent_n["low"].min()
        c = self.price

        if hn == ln:
            self.williams = 0.0
        else:
            self.williams = round((hn - c) / (hn - ln) * 100, 2)

    def calculate_bias(self):
        ma5 = self.ma_dict.get("MA5")
        if ma5 and ma5 > 0:
            self.bias = round(((self.price - ma5) / ma5) * 100, 2)
        else:
            self.bias = 0.0

    # 高级技术指标计算

    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """
        计算 MACD 指标 (DIF, DEA, MACD柱)
        建议 df 的行数 >= 35 以保证指数移动平均(EMA)收敛准确
        """
        if len(df) < slow + signal:
            return

        close = df.sort_index()["close"]
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal, adjust=False).mean()
        macd_bar = (dif - dea) * 2

        self.macd_dif = round(dif.iloc[-1], 2)
        self.macd_dea = round(dea.iloc[-1], 2)
        self.macd_hist = round(macd_bar.iloc[-1], 2)

    def calculate_rsi(self, df, period=14):
        """
        计算 N 日相对强弱指标 (RSI)
        """
        if len(df) <= period:
            return

        close = df.sort_index()["close"]
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        if not np.isnan(rsi.iloc[-1]):
            self.rsi_14 = round(rsi.iloc[-1], 2)

    def calculate_bollinger_bands(self, df, period=20, std_dev=2):
        """
        计算布林线指标 (BOLL)
        """
        if len(df) < period:
            return

        close = df.sort_index()["close"]
        mid = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()

        upper = mid + (std * std_dev)
        lower = mid - (std * std_dev)

        self.boll_mid = round(mid.iloc[-1], 2)
        self.boll_upper = round(upper.iloc[-1], 2)
        self.boll_lower = round(lower.iloc[-1], 2)

    # ================================================================

    @classmethod
    def from_dict_data(cls, name, data_dict, last_close=0.0):
        instance = cls(data_dict["code"], name)

        instance.open = data_dict["open"]
        instance.high = data_dict["high"]
        instance.low = data_dict["low"]
        instance.price = data_dict["close"]
        instance.volume = data_dict["volume"]
        instance.amount = data_dict["amount"]
        instance.update_time = data_dict["kline_time"]
        instance.last_close = last_close

        return instance

    def calculate_volume_ratio(self, df_history):
        """
        计算量比
        逻辑：当日成交量 / 过去5日平均成交量
        注意：严格意义上的量比是 (当前分钟成交量) / (过去5日每分钟平均成交量)
        在日线级别，通常用 (今日总成交量) / (过去5日均量)
        """
        if len(df_history) < 6:
            self.vol_ratio = 0.0
            return

        past_5_days = df_history.iloc[-6:-1]["volume"]
        avg_vol_5 = past_5_days.mean()

        if avg_vol_5 > 0:
            self.vol_ratio = round(self.volume / avg_vol_5, 2)

    @property
    def limit_up(self):
        """涨停价 (昨收 * 1.1)"""
        return round(self.last_close * 1.1, 2)

    @property
    def limit_down(self):
        """跌停价 (昨收 * 0.9)"""
        return round(self.last_close * 0.9, 2)

    @property
    def amplitude(self):
        """振幅 ((最高 - 最低) / 昨收 * 100)"""
        if self.last_close == 0:
            return 0.0
        return round(((self.high - self.low) / self.last_close) * 100, 2)

    @property
    def avg_price(self):
        """全天均价 (总成交额 / 总成交量)"""
        if self.volume > 0:
            return round(self.amount / self.volume, 2)
        return self.price

    def display(self):
        print(f"股票名称: {self.name} ({self.code})")
        print(f"更新时间: {self.update_time}")
        print(f"现价: {self.price:<10} 开盘: {self.open}")
        print(f"最高: {self.high:<10} 最低: {self.low}")
        print(f"涨跌: {self.change:<8} 幅度: {self.change_pct}%")

        if self.total_shares > 0:
            print(
                f"总股本: {round(self.total_shares/10000, 2)} 亿股  总市值: {self.total_cap} 亿元"
            )
            print(
                f"流通股: {round(self.float_shares/10000, 2)} 亿股  流通值: {self.float_cap} 亿元"
            )

        revenue_str = (
            f"{self.total_revenue} 亿元" if hasattr(self, "total_revenue") else "N/A"
        )
        rev_growth_str = (
            f"{self.revenue_growth_rate}%"
            if hasattr(self, "revenue_growth_rate")
            else "N/A"
        )
        print(f"营业总收入: {revenue_str:<10} (同比: {rev_growth_str})")

        if self.pe_ttm > 0:
            print(
                f"PE(TTM): {self.pe_ttm:<8} PE(静态): {self.pe_static:<8} PE(动态): {self.pe_dynamic}"
            )

        ps_val = getattr(self, "ps", 0.0)
        pb_val = getattr(self, "pb", 0.0)
        print(f"市销率(PS): {ps_val:<10} | 市净率(PB): {pb_val}")

        print(f"成交量: {int(self.volume)} 股")
        print(f"成交额: {round(self.amount / 1e8, 2)} 亿元")
        print(f"换手率: {self.turnover}%")
        print(f"量比: {self.vol_ratio}")

        print(f"涨停: {self.limit_up} 跌停: {self.limit_down}")
        print(f"均价: {self.avg_price} 振幅: {self.amplitude}%")

        if self.ma_dict:
            ma_str = " | ".join(
                [f"{k}: {v}" for k, v in self.ma_dict.items() if v is not None]
            )
            print(f"移动平均价 (MA): {ma_str}")

        print(f"威廉指标(14): {self.williams:<10} 乖离率(5): {self.bias}%")

        # 新增扩展指标的打印输出
        if self.macd_dif != 0 or self.macd_dea != 0:
            print(
                f"MACD(12,26,9): DIF: {self.macd_dif} | DEA: {self.macd_dea} | BAR: {self.macd_hist}"
            )
        if self.rsi_14 != 0:
            print(f"RSI(14): {self.rsi_14}")
        if self.boll_mid != 0:
            print(
                f"BOLL(20,2): 上轨: {self.boll_upper} | 中轨: {self.boll_mid} | 下轨: {self.boll_lower}"
            )
