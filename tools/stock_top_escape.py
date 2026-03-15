import pandas
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from dotenv import dotenv_values

from gateways.data_manager import DataManager
from models.constants import Interval

"""
顶部逃离：从“冲云霄”到“滑翔降落”的逻辑重构

本脚本是底部确认逻辑的镜像版：
1. 空间背景：半年内必须有超过 30% 的显著涨幅（确保是高位）。
2. 动能过热：近期 RSI 必须触碰过 70 的超买警戒线。
3. 破位确认：价格跌破 20 日均线，标志着短期趋势反转。
4. 择机逃离：在 RSI 跌至 50-65 的强势末端及时撤退。

python -m tools.stock_top_escape
"""

STOCK_CODE = "000988.SZ"

plt.rcParams["font.sans-serif"] = [
    "SimHei",
    "Microsoft YaHei",
    "Arial Unicode MS",
]
plt.rcParams["axes.unicode_minus"] = False


def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def plot_stock_exit_analysis(df, title_suffix=""):
    """
    顶部逃离绘图函数
    """
    plot_df = df.dropna(subset=["rsi"])
    if plot_df.empty:
        print("数据不足，无法绘图。")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # 1. 绘制价格曲线
    ax1.plot(
        plot_df.index,
        plot_df["c"],
        color="blue",
        marker="o",
        markersize=2,
        label="Price",
        alpha=0.6,
    )
    ax1.plot(
        plot_df.index,
        plot_df["ma20"],
        color="gray",
        linestyle="--",
        label="MA20",
        alpha=0.8,
    )

    # 在价格图中标注逃离信号点 (向下绿色箭头)
    if "exit_signal" in plot_df.columns:
        signals = plot_df[plot_df["exit_signal"] == True]
        if not signals.empty:
            ax1.scatter(
                signals.index,
                signals["c"],
                color="green",
                marker="v",
                s=150,
                edgecolors="black",
                label="EXIT SIGNAL (Sell)",
                zorder=5,
            )

    ax1.set_title(f"{STOCK_CODE} {title_suffix} (顶部逃离检测)")
    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.5)

    # 2. 绘制 RSI 曲线
    ax2.plot(plot_df.index, plot_df["rsi"], color="red", label="RSI (14)")
    ax2.axhline(70, color="orange", linestyle="--", label="Overbought (70)")
    ax2.axhline(50, color="blue", linestyle="--", label="Mid (50)")
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("RSI Value")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    config = dotenv_values("private_config.txt")
    dm = DataManager(provider_name="yinhe")

    if dm.start(config):
        try:
            # 获取 240 天数据确保半年线计算准确
            klines = dm.get_kline(
                STOCK_CODE,
                Interval.DAY_1,
                datetime.now() - timedelta(days=240),
                datetime.now(),
            )

            df = pandas.DataFrame(
                [
                    {"o": k.open, "h": k.high, "l": k.low, "c": k.close, "v": k.volume}
                    for k in klines
                ]
            )

            security_name = dm.get_stock_name(STOCK_CODE)
            print(f"正在分析 {STOCK_CODE} ({security_name}) 的高位风险...")

            # --- 核心逃离逻辑 ---
            df["rsi"] = calculate_rsi(df["c"], 14)
            df["ma20"] = df["c"].rolling(window=20).mean()

            # 1. 涨幅背景：半年内（120天）最低点到现在最高涨幅 > 30%
            # (高 - 低) / 低 >= 30%
            df["l_6m"] = df["c"].rolling(window=120, min_periods=1).min()
            df["is_big_rise"] = (df["c"] - df["l_6m"]) / df["l_6m"] >= 0.30
            # 状态记忆：过去 60 天内有过深幅拉升，背景成立
            df["had_big_rise"] = df["is_big_rise"].rolling(window=60).max().astype(bool)

            # 2. 超买素材：记录 RSI 是否进入过强势过热区 (RSI > 70)
            df["today_is_above_70"] = df["rsi"] > 70

            # 3. 状态延伸：过去 30 天内，是否有任何一天触碰过超买线
            df["in_top_area"] = (
                df["today_is_above_70"].rolling(window=30).max().astype(bool)
            )

            # 4. 破位条件：当前跌破 20 日均线
            df["is_below_ma20"] = df["c"] < df["ma20"]

            # 5. 最终逃离组合逻辑
            df["exit_signal"] = (
                df["had_big_rise"]  # 背景：涨得够狠
                & df["in_top_area"]  # 过程：出现过过热
                & df["is_below_ma20"]  # 动作：跌破支撑
                & (df["rsi"] > 50)  # 确认：还在多空分水岭上方
                & (df["rsi"] < 65)  # 确认：动能已从极热（70+）回落
            )

            print(f"最后 5 日信号状态：\n{df['exit_signal'].tail(5)}")

            plot_stock_exit_analysis(df, security_name)

        finally:
            dm.stop()
    else:
        print("登录失败，请检查配置。")
