import datetime
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

        # 3. 运动指标
        # 市盈率 TTM：总市值 / 最近12个月(滚动)净利润。最贴近现状。
        self.pe_ttm = 0.0
        # 动态市盈率：总市值 / 预测全年净利润(如Q3累计利润/3*4)。反映预期。
        self.pe_dynamic = 0.0
        # 静态市盈率：总市值 / 上一年度(2024全年)净利润。反映过去。
        self.pe_static = 0.0
        
        # 市销率 TTM：总市值 / 最近12个月(滚动)营业收入
        # 专门对付那些“利润暂时很低甚至亏损，但营收规模巨大且稳定”的公司。
        self.ps = 0.0
        
        # 市净率：总市值 / 净资产（通常按每股净资产 * 总股本计算）。反映账面价值。
        self.pb = 0.0

        self.profit_growth_rate = 0.0  # 利润增长率 (%)

        self.vol_ratio = 0.0  # 量比
        self.turnover = 0.0  # 换手率 (%)
        self.amount = 0.0  # 成交额（亿元）
        self.volume = 0.0  # 成交量（手）

        # 4. 扩展维度
        self.total_revenue = 0.0  # 营业总收入（亿元）
        self.revenue_growth_rate = 0.0  # 营收增长率 (%)

        self.ma_dict = {}  # 存储不同周期的均价
        # 衡量当天收盘价在过去 N 天（通常 14 天）波动范围（最高-最低）里的相对位置
        self.williams = 0.0
        self.bias = 0.0  # 乖离率（通常看当日收盘偏离 MA5 的程度）

    @property
    def change(self):
        # 涨跌额
        return round(self.price - self.last_close, 3)

    @property
    def change_pct(self):
        # 涨跌幅度
        if self.last_close == 0:
            return 0.0
        return round((self.change / self.last_close) * 100, 2)

    def calculate_pe_from_financials(self, financials: CompanyFinancials):
        """
        根据财务数据动态回溯计算市盈率
        逻辑：自动从当前理论季度向后搜索 4 个季度，直到找到可用数据
        """
        assert self.total_cap > 0
        data = financials.financial_data
        if not data:
            return

        # 1. 获取当前时间的起始搜索点
        now = datetime.datetime.now()
        curr_year = now.year
        start_q_idx = (now.month - 1) // 3  # 当前月份对应的季度索引 (0-3)

        target_q = None
        q_num = 0

        # 2. 动态回溯逻辑：从当前季往回找最新的可用数据
        for i in range(4):
            check_idx = start_q_idx - i
            # 如果索引小于0，说明要跳到前一年
            year = curr_year if check_idx >= 0 else curr_year - 1
            # 季度只看 1, 2, 3 (因为 Q4 通常存的是全年累计，不作为单季计算起点)
            q_val = (check_idx % 4) + 1
            if q_val == 4:
                q_val = 3

            q_key = f"{year}-Q{q_val}"
            if q_key in data:
                target_q = q_key
                q_num = q_val
                break

        # 3. 提取计算 TTM 和 动态 PE 所需的三个核心值
        year_str = target_q.split("-")[0]
        prev_year = int(year_str) - 1

        curr_q_cum = data.get(target_q, {}).get(
            "operating_profit", 0
        )  # 本期累计 (如 2025-Q3)
        last_full_year = data.get(f"{prev_year}-Q4", {}).get(
            "operating_profit", 0
        )  # 去年全年 (如 2024-Q4)
        prev_q_cum = data.get(f"{prev_year}-Q{q_num}", {}).get(
            "operating_profit", 0
        )  # 去年同期 (如 2024-Q3)

        # 4. 执行计算
        # A. PE (TTM) = 市值 / (本期累计 + 去年全年 - 去年同期)
        profit_ttm = curr_q_cum + (last_full_year - prev_q_cum)
        if profit_ttm > 0:
            self.pe_ttm = round(self.total_cap / (profit_ttm / 1e8), 2)

        # B. PE (静态) = 市值 / 去年全年利润
        if last_full_year > 0:
            self.pe_static = round(self.total_cap / (last_full_year / 1e8), 2)

        # C. PE (动态) = 市值 / (本期累计 / 当前季 * 4)
        if curr_q_cum > 0 and q_num > 0:
            projected_profit = (curr_q_cum / q_num) * 4
            self.pe_dynamic = round(self.total_cap / (projected_profit / 1e8), 2)

    def calculate_pe(self, financials_dict: dict):
        """
        针对 2026年初 环境优化的 PE 计算
        自动识别最新可用季报，并寻找对应的前一年年度基准数据
        """
        if not hasattr(self, "total_cap") or self.total_cap <= 0:
            return

        df = financials_dict.get(self.code)
        if df is None or df.empty:
            return

        PROFIT_FIELD = "NET_PRO_EXCL_MIN_INT_INC"
        REVENUE_FIELD = "TOT_OPERA_REV"  # 营业总收入字段
        PERIOD_FIELD = "REPORTING_PERIOD"
        profit_data = df.set_index(df[PERIOD_FIELD].astype(str))[PROFIT_FIELD].to_dict()
        revenue_data = df.set_index(df[PERIOD_FIELD].astype(str))[
            REVENUE_FIELD
        ].to_dict()

        # 1. 动态确定搜索起点
        now = datetime.datetime.now()
        q_map = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}

        # 2. 动态回溯寻找“最新可用季报” (Target Period)
        target_period = None
        q_num = 0
        # 搜索范围扩大，确保能抓到去年的三季报或中报
        for i in range(1, 7):
            # 简单的年月回溯逻辑
            dt = now - datetime.timedelta(days=i * 90)
            # 构造可能的四个季度末
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
            # 3. 关键：确定参照年份
            # 如果 target_period 是 20250930，那么 base_year 就是 2024
            current_report_year = int(target_period[:4])

            # 只有当最新季报就是年报时(Q4)，base_year 才是前年；否则就是去年
            base_year = current_report_year - 1

            # A. 本期累计 (如 2025-Q3)
            curr_q_cum = profit_data.get(target_period, 0)

            # B. 基准年全年 (如 2024-12-31)
            # 注意：如果此时连 2024 年报都没有，逻辑会失效，所以加个保护
            last_full_year = profit_data.get(f"{base_year}1231", 0)

            # C. 基准年同期 (如 2024-Q3)
            prev_q_cum = profit_data.get(f"{base_year}{q_map[q_num]}", 0)

            # D. 计算利润增长率
            if prev_q_cum and prev_q_cum != 0:
                self.profit_growth_rate = round(
                    ((curr_q_cum - prev_q_cum) / abs(prev_q_cum)) * 100, 2
                )
            else:
                self.profit_growth_rate = 0.0

            curr_rev_cum = revenue_data.get(target_period, 0)
            prev_rev_cum = revenue_data.get(f"{base_year}{q_map[q_num]}", 0)

            # 赋值营业收入 (转换为亿元)
            self.total_revenue = round(curr_rev_cum / 1e8, 2)
            if prev_rev_cum and prev_rev_cum != 0:
                self.revenue_growth_rate = round(
                    ((curr_rev_cum - prev_rev_cum) / abs(prev_rev_cum)) * 100, 2
                )
            else:
                self.revenue_growth_rate = 0.0

            # 4. 计算指标 (单位：亿元)
            cap = self.total_cap

            # TTM 利润 = 2025Q3 + (2024全年 - 2024Q3)
            # 这代表了 2024Q4 + 2025Q1 + 2025Q2 + 2025Q3 的总和
            profit_ttm_yuan = curr_q_cum + (last_full_year - prev_q_cum)

            if profit_ttm_yuan > 0:
                self.pe_ttm = round(cap / (profit_ttm_yuan / 1e8), 2)
            else:
                self.pe_ttm = float("nan")

            # 静态 PE 依然使用基准年全年利润
            if last_full_year > 0:
                self.pe_static = round(cap / (last_full_year / 1e8), 2)
            else:
                self.pe_static = float("nan")

            # 动态 PE (按当前季度进度外推全年)
            if q_num > 0 and curr_q_cum > 0:
                self.pe_dynamic = round(cap / ((curr_q_cum / q_num * 4) / 1e8), 2)
            else:
                self.pe_dynamic = float("nan")

        except Exception as e:
            print(f"计算出错: {e}")
            
    def calculate_ps(self, financials_dict: dict):
        """
        计算市销率 (PS) 
        采用与 PE 计算一致的回溯逻辑，确保营收(Revenue)与利润(Profit)数据口径同步
        """
        if not hasattr(self, "total_cap") or self.total_cap <= 0:
            return

        df = financials_dict.get(self.code)
        if df is None or df.empty:
            return

        # 1. 定义字段（与 PE 计算保持一致）
        REVENUE_FIELD = "TOT_OPERA_REV"  # 营业总收入
        PERIOD_FIELD = "REPORTING_PERIOD"
        revenue_data = df.set_index(df[PERIOD_FIELD].astype(str))[REVENUE_FIELD].to_dict()

        # 2. 获取回溯的时间点
        now = datetime.datetime.now()
        q_map = {1: "0331", 2: "0630", 3: "0930", 4: "1231"}
        target_period = None
        q_num = 0

        # 这里复用 PE 的回溯逻辑
        for i in range(1, 7):
            dt = now - datetime.timedelta(days=i * 90)
            for q in [4, 3, 2, 1]:
                period_key = f"{dt.year}{q_map[q]}"
                if period_key in revenue_data and not pandas.isna(revenue_data[period_key]):
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
            
            # A. 提取核心营收数值
            curr_rev_cum = revenue_data.get(target_period, 0)       # 本期累计 (如 2025Q3)
            last_full_rev = revenue_data.get(f"{base_year}1231", 0) # 去年全年 (如 2024Q4)
            prev_rev_cum = revenue_data.get(f"{base_year}{q_map[q_num]}", 0) # 去年同期 (如 2024Q3)

            # B. 计算 PS (TTM)
            # TTM营收 = 本期累计营收 + (去年全年营收 - 去年同期累计营收)
            # 这种算法能剔除季节性因素，得到真实的滚动 12 个月收入
            rev_ttm_yuan = curr_rev_cum + (last_full_rev - prev_rev_cum)

            if rev_ttm_yuan > 0:
                # 市销率 = 总市值 / (TTM营收 / 1e8)
                self.ps = round(self.total_cap / (rev_ttm_yuan / 1e8), 2)
            else:
                self.ps = float("nan")

            # C. 顺带更新 StockDetail 中的静态属性（可选）
            # 如果你想增加一个 ps_static，可以使用 last_full_rev 进行计算
            # self.ps_static = round(self.total_cap / (last_full_rev / 1e8), 2)

        except Exception as e:
            print(f"[{self.code}] 计算 PS 出错: {e}")
        

    def update_equity(self, total_share_raw, float_share_raw):
        """
        更新股本的同时，自动同步计算市值
        total_share_raw: 接口返回的原始总股本 (万股)
        float_share_raw: 接口返回的原始流通股 (万股)
        """
        self.total_shares = total_share_raw
        self.float_shares = float_share_raw

        # 联动计算市值：(股本 * 价格) / 10000 = 亿元
        if self.price > 0:
            self.total_cap = round((self.total_shares * self.price) / 10000, 2)
            self.float_cap = round((self.float_shares * self.price) / 10000, 2)

        # 联动计算换手率
        # 公式: 成交量(股) / (流通股本(万股) * 10000) * 100
        if self.float_shares > 0:
            self.turnover = round(self.volume / (self.float_shares * 100), 2)

    def calculate_moving_averages(self, df):
        """
        根据传入的 K 线 DataFrame 计算移动平均线
        """
        periods = [3, 5, 10, 20, 30, 60]
        # 确保按时间升序排序
        df_sorted = df.sort_index()

        for p in periods:
            if len(df_sorted) >= p:
                # 取最后 p 天的收盘价均值
                avg = df_sorted["close"].tail(p).mean()
                self.ma_dict[f"MA{p}"] = round(avg, 2)
            else:
                self.ma_dict[f"MA{p}"] = None

    def calculate_williams(self, df, n=14):
        """
        计算 N 日威廉指标 (Williams %R)
        公式: WR = (Hn - C) / (Hn - Ln) * 100
        Hn: N日内最高价; Ln: N日内最低价; C: 当天收盘价
        """
        if len(df) < n:
            self.wr = None
            return

        recent_n = df.tail(n)
        hn = recent_n["high"].max()
        ln = recent_n["low"].min()
        c = self.price

        if hn == ln:
            self.williams = 0.0
        else:
            # 计算威廉指标
            self.williams = round((hn - c) / (hn - ln) * 100, 2)

    def calculate_bias(self):
        """
        计算乖离率: (现价 - 均价) / 均价 * 100
        反映股价偏离 5 日均线的程度
        """
        ma5 = self.ma_dict.get("MA5")
        if ma5 and ma5 > 0:
            self.bias = round(((self.price - ma5) / ma5) * 100, 2)
        else:
            self.bias = 0.0

    @classmethod
    def from_dict_data(cls, name, data_dict, last_close=0.0):
        """
        工厂方法：从解析后的字典/DataFrame 行中创建实例
        data_dict 格式类似: {'code': '600460.SH', 'open': 27.63, ...}
        """
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
        if len(df_history) < 6:  # 至少需要5天历史 + 1天今日
            self.vol_ratio = 0.0
            return

        # 排除最后一行（因为最后一行是今天），取过去5天的成交量
        past_5_days = df_history.iloc[-6:-1]["volume"]
        avg_vol_5 = past_5_days.mean()

        if avg_vol_5 > 0:
            # 计算量比
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
        # 打印美化后的股票信息
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
