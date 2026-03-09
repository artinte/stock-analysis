import sys
import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

"""
使用构造的数据绘制 K 线图。
功能说明：
1. 构造模拟的股票K线数据（包含日期、开盘、最高、最低、收盘、成交量）
2. 使用mplfinance绘制专业的蜡烛图（K线图）
3. 支持自定义股票代码、时间范围、数据波动幅度
"""

def generate_simulate_kline_data(days: int = 60, start_price: float = 100.0) -> pd.DataFrame:
    """
    构造模拟的股票K线数据
    :param days: 生成多少天的K线数据
    :param start_price: 起始价格
    :return: 包含OHLCV的DataFrame（日期为索引）
    """
    # 生成日期序列（从当前日期往前推days天）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 生成模拟的价格数据（加入随机波动）
    np.random.seed(42)  # 固定随机种子，保证结果可复现
    price_changes = np.random.normal(0, 2, days+1)  # 日价格波动（正态分布）
    close_prices = start_price + np.cumsum(price_changes)  # 收盘价
    
    # 构造OHLC（开盘/最高/最低/收盘）数据
    open_prices = close_prices[:-1] + np.random.uniform(-1, 1, days)  # 开盘价=前一日收盘价±随机值
    high_prices = np.maximum(open_prices, close_prices[1:]) + np.random.uniform(0, 3, days)  # 最高价
    low_prices = np.minimum(open_prices, close_prices[1:]) - np.random.uniform(0, 3, days)   # 最低价
    close_prices = close_prices[1:]  # 收盘价（去掉第一个值，匹配天数）
    
    # 生成成交量数据（随机整数）
    volume = np.random.randint(1000000, 50000000, days)
    
    # 构造DataFrame
    kline_data = pd.DataFrame({
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volume
    }, index=dates[1:])  # 索引为日期
    
    # 确保数据类型正确
    kline_data = kline_data.astype({
        'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int
    })
    
    return kline_data

def plot_kline(kline_data: pd.DataFrame, stock_code: str = "SIMULATE-001") -> None:
    """
    绘制K线图
    :param kline_data: 包含OHLCV的DataFrame
    :param stock_code: 股票代码（用于图表标题）
    """
    # 设置K线图样式（经典yahoo样式，红色涨/绿色跌）
    mc = mpf.make_marketcolors(up='red', down='green', edge='inherit', wick='inherit')
    s = mpf.make_mpf_style(marketcolors=mc, gridaxis='both', gridstyle='--', y_on_right=False)
    
    # 绘制K线图（包含成交量子图）
    mpf.plot(
        kline_data,
        type='candle',        # 蜡烛图（K线）
        volume=True,          # 显示成交量
        title=f'{stock_code} 日K线图（模拟数据）',
        ylabel='价格 (元)',
        ylabel_lower='成交量',
        style=s,              # 自定义样式
        figratio=(16, 9),     # 图表比例
        figscale=1.2,         # 图表缩放
        show_nontrading=False # 隐藏非交易日
    )

if __name__ == "__main__":
    # 打印Python版本
    print(f"Python 版本: {sys.version}")
    print("-" * 50)
    
    # 1. 生成模拟K线数据（60天，起始价格100元）
    print("正在生成模拟K线数据...")
    kline_data = generate_simulate_kline_data(days=60, start_price=100.0)
    # 打印前5行数据预览
    print("模拟K线数据预览：")
    print(kline_data.head())
    
    # 2. 绘制K线图
    print("\n正在绘制K线图...")
    plot_kline(kline_data, stock_code="SIMULATE-001")
    
    print("\nK线图绘制完成！")
