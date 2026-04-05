from datetime import datetime, timedelta

from dotenv import dotenv_values
from gateways.data_manager import DataManager
from models.constants import Interval
import requests
import pandas as pd
from io import BytesIO

"""

本ETF主要研究中证A500指数，它从各行业选取市值较大、流动性较好的500只证券作为指数样本，以反映各行业最具代表性上市公司证券的整体表现。
中证A500指数：https://www.csindex.com.cn/#/indices/family/detail?indexCode=000510

行业（一级行业）大致分布如下：
工业: 23.2%
信息技术: 16.91%
原材料: 13.61%
金融: 11.89%
通信服务: 9.39%
可选消费: 7.06%
医药卫生: 6.46%
主要消费: 5.78%
公共事业: 2.57%
能源: 2.44%
房地产: 0.69%

从2026年3月27日来看，中证A500不是一只适合长期定投的ETF，近五年的年化收益为 -0.44%，意味着你五年前的今天投进去100万，至今仍然亏损 4400 元。
这就是股票市场的残酷现实，你不仅没挣钱，还要承担有些时间 20% 以上的损失。

所以必须要改变策略，要学会低吸高抛，在价格较低的时候买入，在价格较高的时候卖出，才能在这个市场中生存下来。以下是基于低吸高抛的动态底仓与高频网格实战策略的详细介绍。


中证 A500 指数：动态底仓与高频网格实战策略

一、 市场真相：为什么要改变策略？

参考指数：
该指数选取了各行业市值大、流动性好的 500 只龙头，反映中国核心资产的整体表现。
残酷数据：截至 2026 年 3 月 27 日，中证 A500 近五年的年化收益率为 -0.44%。
扎心现实：五年前投入 100 万，今天依然亏损 4400 元。你不仅没赚到钱，还在这五年间承担了多次超过 20% 的大幅回撤压力。
结论：A 股核心资产不是简单的“定投天堂”。 如果只会死拿，你就在拿真金白银去忍受毫无回报的波动。必须改变策略，变“死拿”为“低吸高抛”。

二、 核心实战模型：15k - 150k 动态防御系统

我们要利用 A500 每日频繁的“电梯行情”，通过高频小单持续收割利润。

1. 仓位控制（生命线）
为了确保“涨有票卖、跌有钱买”，设定严格的底仓运行区间：
最低底仓 (15,000 股)：持仓市值的下限。无论市场涨多高，永远保留 1.5 万的筹码，确保不踏空，保留对未来牛市的参与权。
最高持仓 (150,000 股)：持仓市值的上限。在极端下跌行情中，允许通过网格不断加仓至 15 万（包含预留资金），这是防御深度的极限，防止单边下跌导致无限接盘。
动态核心：让持仓市值在 1.5 万至 15 万 之间随波动灵活伸缩，形成一个“不倒翁”结构。


2. 网格参数设定
执行标的：中证 A500 ETF（如易方达 (159361)、广发等流动性极佳的品种）。
单笔金额：4,000 股（以目前 1.2 元单价来看，大概要投入 4,800 元，小步慢跑，降低单次博弈风险）。
买入间距：0.56%（下跌触发）。
卖出间距：0.59%（上涨触发）。
实战频率：目标日均成交 4 次（2 买 2 卖）。

动态策略最忌讳的是单边暴跌或者单边暴涨，如果处于这种行情，请即使关闭网格，等待震荡再开。因为单边暴跌会让你过快打满 15 万的上限，单边暴涨则会让你过早触及 1.5 万的下限。


三、 收益预测与逻辑对冲

1. 波动增厚 vs 银行利息
单日目标：2 次卖出成功，产生利润约 56 元。
年化预估：56 元 × 240 交易日 ≈ 13,440 元。
对冲价值：即便指数价格一年内一分钱不涨，这 5.5% 的额外收益也足以秒杀 2.5% 的银行定期利息，并有效覆盖指数回撤带来的心理压力。

2. 策略优势
自动去弱留强：A500 指数每半年自动剔除像“海格通信”这类财务恶化的个股，换入绩优龙头。你无需操心个股爆雷，只需专注于指数波动。
科学避坑：通过 4,800 元的小额切分，避开了 2021 年宁德时代 100 倍 PE 时的那种盲目梭哈，用“时间的玫瑰”换成“波动的收割”。


四、 策略优化：通道识别与动态应对（核心进阶）

虽然单笔 4,800 元固定，但执行节奏应根据通道经验进行微调，以应对不同行情：

1. 震荡行情（无明显趋势）
特征：价格在水平区间波动，RSI 在 30-70 之间。

对策：严格执行 0.56% / 0.59%。这是网格最肥美的时期，无需干预，让系统自动刷单。

2. 上升通道（多头占优）
特征：均线向上，高点不断创新高。

优化逻辑：“缓买快卖”。
调大买入间距（如 0.8%）：防止回撤过小时过早补仓，保留子弹。
调小卖出间距（如 0.4%）：在上涨中更频繁地止盈，把浮盈变成现金。

目的：在上升趋势中不断提高底仓的安全性。

3. 下降通道（空头占优）
特征：阴线多于阳线，重心下移。

优化逻辑：“慎买缓卖”。
调大买入间距（如 1.2% - 1.5%）：防止在单边下跌中由于网格过密而过快打满 15 万股上限。
调大卖出间距：不急于反弹一点就跑，等待更厚实的价差出现。
目的：拉长补仓距离，增加抗跌深度，应对像 2021 年宁德时代那种“估值回归”的杀伤力。


五、 结语

“死拿是信仰，网格是生意。”
在 A 股这种“牛短熊长”的环境里，价格是虚的，只有落袋的波动利润才是实的。10 万资金分成 50 份，在 1.5 万到 15 万的区间里反复“摩擦”，这才是应对中证 A500 最理性的生存方式。

"""


A500_CLOSE_WEIGHT_URL = "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/closeweight/000510closeweight.xls"


def get_a500_components(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 1. 直接从网络读取到内存
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        file_content = BytesIO(response.content)

        # 2. 常规读取逻辑：先尝试 Excel，失败则尝试 HTML
        try:
            df = pd.read_excel(file_content)
        except Exception:
            # 中证官网文件经常是 HTML 伪装的 .xls
            df = pd.read_html(file_content)[0]

        # 3. 标准化清洗 (提取核心列)
        # 注意：中证文件的列名通常是：'成份券代码', '成份券名称', '权重(%)'
        # 或者是英文：'Constituent Code', 'Constituent Name', 'Weight(%)'

        # 自动识别列名（取包含代码、名称、权重的列）
        target_cols = {
            "code": [
                c
                for c in df.columns
                if "成份券代码" in str(c) or "Constituent Code" in str(c)
            ][0],
            "name": [
                c
                for c in df.columns
                if "成份券名称" in str(c) or "Constituent Name" in str(c)
            ][0],
            "weight": [c for c in df.columns if "权重" in str(c) or "Weight" in str(c)][
                0
            ],
        }

        result = df[
            [target_cols["code"], target_cols["name"], target_cols["weight"]]
        ].copy()
        result.columns = ["Stock_Code", "Stock_Name", "Weight_Percent"]

        # 4. 代码补全 (如 1 变为 000001)
        result["Stock_Code"] = result["Stock_Code"].astype(str).str.zfill(6)

        return result

    except Exception as e:
        print(f"提取失败: {e}")
        return None


MIN_HOLDING = 15000  # 最低底仓
MAX_HOLDING = 150000  # 最高持仓上限
GRID_SIZE = 4000  # 单笔网格大小
BUY_THRESHOLD = 0.0056  # 买入间距 0.56%
SELL_THRESHOLD = 0.0059  # 卖出间距 0.59%


def run_high_freq_backtest(df, initial_pos=32000):
    current_pos = initial_pos
    cash_balance = 0
    # 基准价随动：初始取第一行的开盘价
    last_executed_price = df.iloc[0]["open"]
    
    trade_log = []

    for _, row in df.iterrows():
        p_high = row["high"]
        p_low = row["low"]
        p_time = row["time"]
        
        executed = False
        
        # 1. 检查卖出逻辑 (向上看)
        target_sell = last_executed_price * (1 + SELL_THRESHOLD)
        if p_high >= target_sell:
            if current_pos >= (MIN_HOLDING + GRID_SIZE):
                # 触发倍投卖出判定
                if p_high >= last_executed_price * (1 + SELL_THRESHOLD * 2):
                    sell_size = GRID_SIZE * 2
                    actual_price = last_executed_price * (1 + SELL_THRESHOLD * 2)
                else:
                    sell_size = GRID_SIZE
                    actual_price = target_sell
                
                sell_size = min(sell_size, current_pos - MIN_HOLDING)
                if sell_size > 0:
                    current_pos -= sell_size
                    cash_balance += sell_size * actual_price
                    last_executed_price = actual_price # 基点随动更新
                    trade_log.append({
                        "time": p_time, "type": "SELL", "price": round(actual_price, 4), 
                        "pos": current_pos, "size": sell_size
                    })
                    executed = True

        # 2. 如果没卖出，检查买入逻辑 (向下看)
        if not executed:
            target_buy = last_executed_price * (1 - BUY_THRESHOLD)
            if p_low <= target_buy:
                if current_pos <= (MAX_HOLDING - GRID_SIZE):
                    # 触发倍投买入判定
                    if p_low <= last_executed_price * (1 - BUY_THRESHOLD * 2):
                        buy_size = GRID_SIZE * 2
                        actual_price = last_executed_price * (1 - BUY_THRESHOLD * 2)
                    else:
                        buy_size = GRID_SIZE
                        actual_price = target_buy
                    
                    buy_size = min(buy_size, MAX_HOLDING - current_pos)
                    if buy_size > 0:
                        current_pos += buy_size
                        cash_balance -= buy_size * actual_price
                        last_executed_price = actual_price # 基点随动更新
                        trade_log.append({
                            "time": p_time, "type": "BUY", "price": round(actual_price, 4), 
                            "pos": current_pos, "size": buy_size
                        })

    # --- 结算逻辑 (关键修改点) ---
    final_price = df.iloc[-1]["close"]
    start_price = df.iloc[0]["open"]
    
    # A. 初始投入总额 (基准)
    initial_value = initial_pos * start_price
    
    # B. 方案1：死拿不动 (Benchmark)
    hold_final_value = initial_pos * final_price
    hold_pnl = hold_final_value - initial_value  # <-- 返回值 5: h_pnl
    
    # C. 方案2：网格策略
    strategy_final_value = cash_balance + (current_pos * final_price) # <-- 返回值 2: final_val
    strategy_pnl = strategy_final_value - initial_value             # <-- 返回值 4: s_pnl
    
    # D. 超额收益 (Alpha)
    extra_profit = strategy_final_value - hold_final_value          # <-- 返回值 3: extra

    # 严格按顺序返回 5 个值
    return pd.DataFrame(trade_log), strategy_final_value, extra_profit, strategy_pnl, hold_pnl


def main():
    config = dotenv_values("private_config.txt")
    dm = DataManager(provider_name="yinhe")

    if dm.start(config):
        try:
            a500_df = get_a500_components(A500_CLOSE_WEIGHT_URL)
            
            print("\n正在分段拉取 1 分钟线数据进行回测...")
            all_dfs = []
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
            
            curr_dt = start_dt
            while curr_dt <= end_dt:
                if curr_dt.weekday() < 5:
                    day_start = curr_dt.replace(hour=9, minute=0, second=0, microsecond=0)
                    day_end = curr_dt.replace(hour=15, minute=5, second=0, microsecond=0)
                    
                    result = dm.get_kline("159361.SZ", Interval.MINUTE_1, day_start, day_end)
                    klines, _ = result if isinstance(result, tuple) else (result, "OK")
                    
                    if klines and isinstance(klines, list):
                        # --- 核心改进：直接在这里处理时间戳，避免后面变 NaT ---
                        data_list = []
                        for k in klines:
                            # 尝试获取时间戳，如果 k.datetime 不行，尝试 k.date_time 或转字符串
                            t = getattr(k, 'datetime', None)
                            if t is None: t = getattr(k, 'date_time', None)
                            
                            data_list.append({
                                "time": t,
                                "open": k.open, 
                                "high": k.high, 
                                "low": k.low, 
                                "close": k.close
                            })
                        
                        day_df = pd.DataFrame(data_list)
                        if not day_df.empty:
                            all_dfs.append(day_df)
                            print(f"日期 {curr_dt.date()} 数据抓取成功: {len(day_df)} 行")
                
                curr_dt += timedelta(days=1)

            # --- 关键修正：鲁棒性合并逻辑 ---
            if not all_dfs:
                print("未能获取到任何数据。")
                return

            # 1. 先纵向拼接所有数据
            full_df = pd.concat(all_dfs, ignore_index=True)
            
            # 2. 检查 time 列是否有数据。如果是 None，尝试填充一个模拟时间防止去重失败
            if full_df['time'].isnull().all():
                print("⚠️ 警告：无法从接口获取 time 字段，正在生成模拟时间序列...")
                # 仅作为保底逻辑：如果接口没给时间，我们按行生成
                full_df['time'] = pd.date_range(start=start_dt, periods=len(full_df), freq='min')
            else:
                # 3. 强制转换并过滤掉无法转换的坏行
                full_df['time'] = pd.to_datetime(full_df['time'], errors='coerce')
                full_df = full_df.dropna(subset=['time']) 

            # 4. 执行去重和排序
            full_df = full_df.drop_duplicates(subset=['time']).sort_values('time').reset_index(drop=True)
            
            print(f"\n✅ 全量数据拼装成功，共 {len(full_df)} 行")
            
            if len(full_df) < 100:
                print("数据量依然异常，请检查接口返回的对象属性：", full_df.head())
                return

            if not full_df.empty:
                # --- 计算市场实际跌幅 ---
                p_start = full_df.iloc[0]["open"]
                p_end = full_df.iloc[-1]["close"]
                market_change_pct = (p_end - p_start) / p_start * 100
                hold_pnl = 32000 * (p_end - p_start)

                # --- 运行回测 ---
                trades, final_val, extra, s_pnl, h_pnl = run_high_freq_backtest(full_df, initial_pos=32000)

                print("\n" + "="*45)
                print("【中证A500 市场真实数据分析】")
                print(f"统计区间: {start_dt.date()} -> {end_dt.date()}")
                print(f"实际统计天数：{len(full_df) // 242} 天 (每个交易日约 242 分钟线数据)")
                print(f"期初价格: {p_start:.4f} | 期末价格: {p_end:.4f}")
                print(f"📉 市场实际涨跌: {market_change_pct:.2f}%")
                print(f"💡 如果死拿不动，你会亏损: {hold_pnl:.2f} 元")
                
                print("\n【网格成交详细统计】")
                if not trades.empty:
                    buy_count = len(trades[trades['type'] == 'BUY'])
                    sell_count = len(trades[trades['type'] == 'SELL'])
                    print(f"✅ 总计成交: {len(trades)} 次")
                    print(f"   - 买入 (补仓): {buy_count} 次")
                    print(f"   - 卖出 (止盈): {sell_count} 次")
                    print(f"期初持仓股数: 32000 股")
                    print(f"期末持仓股数: {trades.iloc[-1]['pos']} 股")
                else:
                    print("❌ 警告：回测期间 [成交次数为 0]！")
                    print(f"原因分析：A500 波动太小，从未达到你设置的 {BUY_THRESHOLD*100:.2f}% 阈值。")
                    
                print("\n【策略盈亏对比】")
                print(f"网格策略总盈亏: {s_pnl:.2f} 元")
                print(f"网格超额贡献: {extra:.2f} 元")
                print("="*45)

        except Exception as e:
            print(f"运行异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            dm.stop()

if __name__ == "__main__":
    main()
