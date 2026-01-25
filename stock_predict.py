from dotenv import dotenv_values
from datetime import datetime, timedelta
from gateways.data_manager import DataManager
from models.constants import Interval

# 预测股价未来的表现

config = dotenv_values("private_config.txt")

dm = DataManager(provider_name="yinhe")

if dm.start(config):
    try:
        # 1. 确定获取范围：最近 7 天
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)

        symbol = "600519.SH"

        # 2. 调用 fetch_kline 获取数据
        # 注意：dm 会调用 gateway 内部的 fetch_kline
        klines = dm.get_kline(
            symbol=symbol,
            interval=Interval.DAY_1,  # 获取日线
            start_time=start_time,
            end_time=end_time,
        )

        # 3. 打印结果
        print(f"--- 股票代码: {symbol} (最近一周 K 线数据) ---")
        if not klines:
            print("未获取到数据，请检查市场是否开市或代码是否正确。")
        else:
            for k in klines:
                print(
                    f"时间: {k.trade_time} | 开: {k.open:.2f} | 高: {k.high:.2f} | 低: {k.low:.2f} | 收: {k.close:.2f} | 成交量: {k.volume}"
                )

    finally:
        dm.stop()
else:
    print("DataManager 启动失败，请检查配置或网络。")
