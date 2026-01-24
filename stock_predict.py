from dotenv import dotenv_values
from gateways.data_manager import DataManager

# 预测股价未来的表现

config = dotenv_values("private_config.txt")

dm = DataManager(provider_name="yinhe")

if dm.start(config):
    try:
        # 获取股票对象
        symbol = "600519.SH"
        stock = dm.get_stock(symbol)

        print(f"代码: {stock.code}")
        # print(f"价格: {stock.price}") # 此时取决于 fetch 内部是否填充了数据

    finally:
        dm.stop()
else:
    print("DataManager 启动失败，请检查配置或网络。")
