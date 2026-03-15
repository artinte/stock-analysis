import pandas

from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from dotenv import dotenv_values

from gateways.data_manager import DataManager
from models.constants import Interval


"""
底部确认：从“接飞刀”到“顺风车”的逻辑重构
文章链接：https://artinte.github.io/stock-analysis/stock_bottom_comfirm.html

在投资的世界里，底部确认信号一直是投资者们追逐的热点话题。
它不仅关系到投资者的资金安全，更直接影响到投资回报率。
然而，市场上关于底部确认的讨论往往充斥着各种各样的观点和方法，让人眼花缭乱。
那么，什么是真正有效的底部确认信号呢？
本文将从“接飞刀”到“顺风车”的逻辑重构，深入探讨底部确认的核心要素和实战应用。

本脚本是为了配合文章《底部确认：从“接飞刀”到“顺风车”的逻辑重构》而编写的工具脚本。
它的主要功能是帮助投资者理解和应用文章中提到的底部确认信号的概念和方法。
通过这个脚本，投资者可以更好地识别市场中的底部确认信号，从而做出更明智的投资决策。

python -m tools.stock_bottom_comfirm
"""


STOCK_CODE = "000988.SZ"

# 计算 RSI 指标的函数
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # 使用 RMA (Relative Moving Average) 算法，这是 RSI 的标准计算法
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def plot_stock_analysis(df, title_suffix=""):
    """
    通用的绘图复用函数
    :param df: 必须包含 'c', 'rsi', 'buy_signal' 列的 DataFrame
    """
    # 剔除 NaN 保证绘图连续性
    plot_df = df.dropna(subset=["rsi"])
    
    if plot_df.empty:
        print("数据量不足以计算 RSI，无法绘图。")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # 1. 绘制价格曲线
    ax1.plot(plot_df.index, plot_df["c"], color="blue", marker="o", markersize=4, label="Price (Close)", alpha=0.6)
    
    # 仅在价格图中标注买入信号点
    if 'buy_signal' in plot_df.columns:
        signals = plot_df[plot_df['buy_signal'] == True]
        if not signals.empty:
            ax1.scatter(signals.index, signals['c'], color="red", marker="^", s=150, 
                        edgecolors='black', label="BUY SIGNAL", zorder=5)

    ax1.set_title(f"{STOCK_CODE} {title_suffix} (Ref: 2026-03)")
    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.5)

    # 2. 绘制 RSI 曲线（纯净版，不带标记）
    ax2.plot(plot_df.index, plot_df["rsi"], color="red", label="RSI (14)")
    ax2.axhline(30, color="green", linestyle="--", label="Oversold (30)")
    ax2.axhline(70, color="orange", linestyle="--", label="Overbought (70)")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("RSI Value")
    ax2.set_title("RSI Indicator (Bottom Confirmation)")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    config = dotenv_values("private_config.txt")
    dm = DataManager(provider_name="yinhe")

    if dm.start(config):
        try:
            # 1. 获取 10 年数据
            klines = dm.get_kline(
                STOCK_CODE,
                Interval.DAY_1,
                datetime.now() - timedelta(days=180),
                datetime.now(),
            )

            # 2. 特征工程 & 查杀 NaN
            df = pandas.DataFrame(
                [
                    {"o": k.open, "h": k.high, "l": k.low, "c": k.close, "v": k.volume}
                    for k in klines
                ]
            )

            print(df["c"].to_list())
            
            # --- 核心逻辑计算 ---
            df['rsi'] = calculate_rsi(df["c"], 14)
            df['ma20'] = df['c'].rolling(window=20).mean()

            # 1. 探底素材：今天是否跌破 42
            df['today_is_below_42'] = df['rsi'] < 42

            # 2. 状态延伸：过去 20 天内，是否有任何一天跌破过 42？
            # 解决你担心的“今天不是底”的问题，只要近期探过底就行
            df['in_bottom_area'] = df['today_is_below_42'].rolling(window=30).max().astype(bool)
            
            # 3. 计算双底结构 (识别两个独立的探底动作)
            # 只有当 RSI 从 >42 掉到 <42 的那一瞬间，才算一次“探底脉冲”
            df['bottom_pulse'] = (df['today_is_below_42'] & (df['today_is_below_42'].shift(1) == False))
            # 统计过去 60 天内这种脉冲出现了几次
            df['bottom_count'] = df['bottom_pulse'].rolling(window=60).sum()

            # 4. 顺风车条件：当前站上 20 日均线
            df['is_above_ma20'] = df['c'] > df['ma20']
            
            # 5. 最终组合逻辑
            # 条件：1.近期探过底 + 2.有双底背景 + 3.今天站上均线 + 4.动能回升(RSI>45)
            df['buy_signal'] = (
                df['in_bottom_area'] & 
                df['is_above_ma20'] &
                (df['rsi'] < 50)
            )
            print(df['buy_signal'])

            plot_stock_analysis(df, "Live Data")
        finally:
            dm.stop()
    else:
        # 如果没有登录成功，就用假数据演示一下
        print("登录失败，使用假数据演示。")
        # 60 天的数据
        close_prices = [
            29.64,
            29.48,
            29.58,
            29.82,
            28.89,
            28.93,
            29.45,
            30.67,
            30.59,
            30.51,
            31.53,
            31.15,
            31.66,
            30.68,
            32.02,
            34.0,
            33.55,
            33.39,
            30.69,
            31.0,
            30.4,
            31.12,
            30.18,
            31.63,
            31.02,
            30.56,
            32.27,
            31.76,
            32.02,
            32.49,
            32.55,
            32.19,
            31.13,
            28.73,
            28.43,
            28.93,
            28.88,
        ]
        
        dates = pandas.date_range(end=datetime.now(), periods=len(close_prices))
        df = pandas.DataFrame({"c": close_prices}, index=dates)
        df["rsi"] = calculate_rsi(df["c"], 14)
        print(df[["c", "rsi"]].to_string())
        plot_df = df.dropna(subset=["rsi"])
        
        
        
