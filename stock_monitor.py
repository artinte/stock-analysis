import AmazingData
from dotenv import dotenv_values
from stock_detail import StockDetail
from company_financials import AllCompanyFinancials

TARGET_CODE = "002371.SZ"
STOCK_NAME = "北方华创"
# TARGET_CODE = "600460.SH"
# STOCK_NAME = "士兰微"

config = dotenv_values("private_config.txt")
AmazingData.login(
    username=config["username"],
    password=config["password"],
    host=config["host"],
    port=int(config["port"]),
)

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
    [TARGET_CODE], local_path=config["local_path"], is_local=False
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

# 计算静态市盈率、动态市盈率、市盈 (TTM)
# fin_obj = next(
#     (f for f in AllCompanyFinancials if f.ticker and f.ticker in stock_instance.code),
#     None,
# )
# if fin_obj:
#     stock_instance.calculate_pe_from_financials(fin_obj)

raw_income_dict = info_data_object.get_income(
    code_list=[TARGET_CODE],
    local_path=config["local_path"],
    is_local=False,
    begin_date="20220101",
    end_date=calendar[-1],
)
stock_instance.calculate_pe(raw_income_dict)
stock_instance.calculate_ps(raw_income_dict)

# 计算 60日，30日，20日，10日，5日，3日股价均值
lookback = 100
begin_date = calendar[-lookback]
kline_data = market_data_object.query_kline(
    code_list=[stock_instance.code],
    begin_date=begin_date,
    end_date=calendar[-1],
    period=AmazingData.constant.Period.day.value,
)[stock_instance.code]

stock_instance.calculate_moving_averages(kline_data)
stock_instance.calculate_volume_ratio(kline_data)
stock_instance.calculate_williams(kline_data, n=14)
stock_instance.calculate_bias()

stock_instance.display()
