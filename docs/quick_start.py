import sys
import mplfinance as mpf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 核心修复：配置 matplotlib 支持中文
# ---------------------------------------------------------
plt.rcParams["font.sans-serif"] = [
    "SimHei",
    "Microsoft YaHei",
    "Arial Unicode MS",
]  # 适配 Windows/Mac/Linux
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示为方块的问题


def generate_simulate_kline_data(
    days: int = 60, start_price: float = 100.0
) -> pd.DataFrame:
    """
    构造模拟的股票K线数据
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    np.random.seed(42)
    # 模拟价格走势
    price_changes = np.random.normal(0, 1.5, days + 1)
    close_prices = start_price + np.cumsum(price_changes)

    # 构造OHLC
    open_prices = close_prices[:-1] + np.random.uniform(-0.5, 0.5, days)
    high_prices = np.maximum(open_prices, close_prices[1:]) + np.random.uniform(
        0, 1, days
    )
    low_prices = np.minimum(open_prices, close_prices[1:]) - np.random.uniform(
        0, 1, days
    )
    close_prices = close_prices[1:]

    volume = np.random.randint(1000000, 50000000, days)

    kline_data = pd.DataFrame(
        {
            "Open": open_prices,
            "High": high_prices,
            "Low": low_prices,
            "Close": close_prices,
            "Volume": volume,
        },
        index=dates[1:],
    )

    return kline_data.astype(
        {"Open": float, "High": float, "Low": float, "Close": float, "Volume": int}
    )


def plot_kline(kline_data: pd.DataFrame, stock_code: str = "SIMULATE-001") -> None:
    """
    绘制K线图
    """
    # 自定义 A 股风格：红涨绿跌 (up='red', down='green')
    # base_mpf_style 可以选择 'binance', 'blueskies', 'charles' 等
    mc = mpf.make_marketcolors(
        up="red", down="green", edge="inherit", wick="inherit", volume="inherit"
    )

    # 这里的 rc 参数是解决中文的关键之一
    s = mpf.make_mpf_style(
        base_mpf_style="charles",
        marketcolors=mc,
        gridaxis="both",
        gridstyle="--",
        y_on_right=False,
        rc={
            "font.sans-serif": ["SimHei"],  # 再次确保样式内应用中文字体
            "axes.unicode_minus": False,
        },
    )

    # 绘制
    mpf.plot(
        kline_data,
        type="candle",
        volume=True,
        title=f"\n{stock_code} 日K线图（模拟数据）",
        ylabel="价格 (元)",
        ylabel_lower="成交量",
        style=s,
        figratio=(12, 7),
        figscale=1.1,
        show_nontrading=False,
        datetime_format="%Y-%m-%d",  # x轴日期格式
        xrotation=15,  # 日期标签旋转角度
    )


if __name__ == "__main__":
    print(f"Python 版本: {sys.version}")

    # 1. 生成数据
    data = generate_simulate_kline_data(days=60)

    # 2. 绘图
    plot_kline(data, stock_code="联化科技 (002250.SZ)")
