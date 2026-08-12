import AmazingData
from models.stock_detail import StockDetail
import pandas as pd
import mplfinance as mpf


TARGET_CODE = "603658.SH"
STOCK_NAME = "安图生物"

AmazingData.login(
    username="",
    password="",
    host="",
    port=0,
)

local_path = r"C:\Users\admin\AmazingData"
info_data_object = AmazingData.InfoData()
base_data_object = AmazingData.BaseData()
calendar = base_data_object.get_calendar()
market_data_object = AmazingData.MarketData(calendar)

kline_dict = market_data_object.query_kline(
    code_list=[TARGET_CODE],
    begin_date=calendar[-2],
    end_date=calendar[-1],
    period=AmazingData.constant.Period.day.value,  # 日线
)

df = kline_dict[TARGET_CODE]
if len(df) >= 2:
    prev_close = df.iloc[-2]["close"]
    today_data = df.iloc[-1].to_dict()
    stock_instance = StockDetail.from_dict_data(
        STOCK_NAME, today_data, last_close=prev_close
    )
else:
    print("警告：数据行数不足，无法获取昨收价。")
    stock_instance = StockDetail.from_dict_data(STOCK_NAME, df.iloc[-1].to_dict())

lookback = 100
begin_date = calendar[-lookback]
kline_data = market_data_object.query_kline(
    code_list=[stock_instance.code],
    begin_date=begin_date,
    end_date=calendar[-1],
    period=AmazingData.constant.Period.day.value,
)[stock_instance.code]


# 1. 数据预处理
# 将返回的 list 转换为 DataFrame 并规范列名
df_plot = pd.DataFrame(kline_data)
# 确保列名符合 mplfinance 的要求 (Open, High, Low, Close, Volume)
df_plot.rename(
    columns={
        "kline_time": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    },
    inplace=True,
)

# 将 Date 转为 DatetimeIndex (这是绘制 K 线图的必要条件)
df_plot["Date"] = pd.to_datetime(df_plot["Date"])
df_plot.set_index("Date", inplace=True)

# 2. 设置绘图样式 (符合 A 股红涨绿跌习惯)
my_color = mpf.make_marketcolors(
    up="red",  # 上涨为红
    down="green",  # 下跌为绿
    edge="inherit",  # 边缘继承颜色
    wick="inherit",  # 影线继承颜色
    volume="inherit",  # 成交量颜色继承
)
my_style = mpf.make_mpf_style(
    marketcolors=my_color, gridstyle="--", y_on_right=True  # 坐标轴放在右侧
)

# 3. 绘制详细特征图
# 包含：K线、成交量(Volume)、移动平均线(MA5, MA10, MA20)
print(f"正在生成 {STOCK_NAME} ({TARGET_CODE}) 的详细特征图...")

mpf.plot(
    df_plot,
    type="candle",  # 蜡烛图
    style=my_style,  # 应用自定义样式
    title=f"({TARGET_CODE}) Daily K-Line",
    ylabel="Price (RMB)",
    ylabel_lower="Volume",
    volume=True,  # 显示成交量
    mav=(5, 10, 20),  # 绘制 5/10/20 日移动平均线
    figratio=(12, 8),  # 图表比例
    figscale=1.2,  # 图表缩放
    tight_layout=True,
    show_nontrading=False,  # 自动隐藏非交易日（周末/节假日）的空白
)
