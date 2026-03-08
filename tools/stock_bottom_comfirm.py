from matplotlib import pyplot as plt
import pandas
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

STOCK_CODE = "600460.SH"

# 计算 RSI 指标的函数
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    
    # 使用 RMA (Relative Moving Average) 算法，这是 RSI 的标准计算法
    avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

if __name__ == "__main__":
    config = dotenv_values("private_config.txt")
    dm = DataManager(provider_name="yinhe")

    if dm.start(config):
        try:
            # 1. 获取 10 年数据
            klines = dm.get_kline(
                STOCK_CODE,
                Interval.DAY_1,
                datetime.now() - timedelta(days=60),
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
    
            # 3. 计算 RSI (注意传入 df["c"])
            df["rsi"] = calculate_rsi(df["c"], 14)
            
            # --- 关键：剔除 NaN 方便绘图 ---
            plot_df = df.dropna(subset=["rsi"])

            # 4. 绘图：确保所有 Key 都叫 "c" 和 "rsi"
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

            # 绘制价格 (用你的 "c")
            ax1.plot(plot_df.index, plot_df['c'], color='blue', marker='o', label='Price (Close)')
            ax1.set_title(f'{STOCK_CODE} Price Trend (2026-03-06)')
            ax1.legend()
            ax1.grid(True, linestyle='--', alpha=0.5)

            # 绘制 RSI
            ax2.plot(plot_df.index, plot_df['rsi'], color='red', label='RSI (14)')
            ax2.axhline(30, color='green', linestyle='--', label='Oversold (30)') 
            ax2.axhline(70, color='orange', linestyle='--', label='Overbought (70)')
            ax2.set_title('RSI Indicator')
            ax2.legend()
            ax2.grid(True, linestyle='--', alpha=0.5)

            plt.tight_layout()
            
            # 5. 在 VS Code 中保存并显示
            # plt.savefig("rsi_result.png")
            # print("\n>>> 图片已保存为 rsi_result.png，请在左侧文件栏查看！")
            plt.show()
        finally:
            dm.stop()
