import datetime
import AmazingData
from dotenv import dotenv_values
from models.stock_detail import StockDetail
import mplfinance
import pandas
from matplotlib import pyplot, transforms

TARGET_CODE = "001389.SZ"
STOCK_NAME = "广合科技"

config = dotenv_values("private_config.txt")
# A. 环境登录与初始化
AmazingData.login(
    username=config["username"],
    password=config["password"],
    host=config["host"],
    port=int(config["port"]),
)
local_path = config["local_path"]

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


equity_structure = info_data_object.get_equity_structure(
    [TARGET_CODE], local_path=local_path, is_local=False
)

# 获取总市值
total_share = 0
float_share = 0
if not equity_structure.empty:
    equity_structure = equity_structure.sort_values("CHANGE_DATE")
    latest_row = equity_structure.iloc[-1]
    total_share = latest_row["TOT_SHARE"]
    float_share = latest_row["FLOAT_SHARE"]

stock_instance.update_equity(total_share, float_share)

lookback = 180
begin_date = calendar[-lookback]
kline_data = market_data_object.query_kline(
    code_list=[TARGET_CODE],
    begin_date=begin_date,
    end_date=calendar[-1],
    period=AmazingData.constant.Period.day.value,
)[TARGET_CODE]

stock_instance.calculate_moving_averages(kline_data)
stock_instance.calculate_volume_ratio(kline_data)
stock_instance.calculate_williams(kline_data, n=14)
stock_instance.calculate_bias()

stock_instance.display()


plot_df = kline_data.copy()
if "kline_time" in plot_df.columns:
    plot_df["kline_time"] = pandas.to_datetime(plot_df["kline_time"])
    plot_df.set_index("kline_time", inplace=True)
else:
    plot_df.index = pandas.to_datetime(plot_df.index)

plot_df = plot_df[["open", "high", "low", "close", "volume"]]
plot_df.columns = ["Open", "High", "Low", "Close", "Volume"]

mc = mplfinance.make_marketcolors(
    up="red", down="green", edge="inherit", wick="inherit", volume="in"
)
# s = mplfinance.make_mpf_style(marketcolors=mc, gridstyle="--", y_on_right=True)

mav_periods = (5, 10, 20, 60)

import numpy as np

# --- 1. PE-TTM 动态计算 (单位：万股/元 修正版) ---
dates = plot_df.index
pe_ttm_series = []

# 明确单位：万股 -> 还原为 股
corrected_total_share = total_share * 10000

# --- 2. 计算平均 PE ---
# 过滤掉空值计算这段时间的均值
pe_array = np.array(pe_ttm_series)
valid_pe = pe_array[~np.isnan(pe_array)]
avg_pe_val = np.mean(valid_pe) if len(valid_pe) > 0 else 0
# 构造一条水平线序列
avg_pe_series = [avg_pe_val] * len(plot_df)

# --- 3. 绘图配置 ---
# 配置副图：增加平均 PE 线 (虚线表示)
apds = [
    mplfinance.make_addplot(
        pe_ttm_series, panel=1, type="line", color="red", ylabel="PE-TTM", width=1.5
    ),
    mplfinance.make_addplot(
        avg_pe_series, panel=1, type="line", color="blue", width=1.0, linestyle="--"
    ),
]

# --- 1. 样式定义 (保留你的中文支持配置) ---
s = mplfinance.make_mpf_style(
    base_mpf_style="binance",
    marketcolors=mc,
    rc={"font.family": "SimHei", "axes.unicode_minus": False},
)

# --- 2. 最终绘图 ---
fig, axlist = mplfinance.plot(
    plot_df,
    type="candle",
    style=s,
    addplot=apds,
    # 移除内部 title，改用下方 suptitle 以获得更好位置控制
    ylabel="Price",
    datetime_format="%Y-%m-%d",
    mav=mav_periods,
    figsize=(13, 10),
    tight_layout=True,
    show_nontrading=False,
    returnfig=True,
)


# --- 3. 手动精修标题 (解决太靠上的问题) ---
# y=0.96 让标题在顶部留有呼吸感，fontsize=18 适配 14x10 的大图
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
fig.suptitle(
    f"{STOCK_NAME} ({TARGET_CODE}) PE-TTM 走势及均值分析 [{current_date}]",
    fontsize=20,
    fontweight="bold",
    y=0.9,
)

# --- 5. 在副图上标注平均 PE 数值 (增加背景框，更美观) ---
offset = transforms.ScaledTranslation(0, 10/72, fig.dpi_scale_trans)
trans = axlist[2].get_yaxis_transform() + offset

# 2. 绘制文字
axlist[2].text(
    0.01, 
    avg_pe_val, 
    f" 平均 PE: {avg_pe_val:.2f} ",
    color="white",
    fontsize=13,
    fontweight="bold",
    transform=trans,          # 使用我们定义的带偏移的变换
    va="bottom", 
    ha="left",
    bbox=dict(
        facecolor='#4169E1',  # 皇家蓝
        alpha=0.9, 
        edgecolor='none', 
        boxstyle='round,pad=0.4' # 增加 pad 让框体更圆润，也变相拉开了文字与线的距离
    )
)

# --- 6. 细节美化：主副图网格线微调 ---
for ax in [axlist[0], axlist[2]]:
    ax.grid(True, linestyle="--", alpha=0.5)

pyplot.show()
