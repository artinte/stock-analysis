import datetime
import os
from dotenv import load_dotenv
import pandas
from gateways.analysis.valuation import ValuationAnalyzer
from gateways.data_manager import DataManager
from gateways.providers.yinhe.gateway import YinheGateway
from gateways.indicators.volatility import calculate_bollinger_bands
from gateways.indicators.macd import calculate_macd
from gateways.indicators.moving_average import calculate_moving_averages
from gateways.indicators.momentum import calculate_rsi, calculate_williams

if __name__ == "__main__":
    load_dotenv()

    config = {
        "username": os.getenv(
            "amazing_username",
            "",
        ),
        "password": os.getenv(
            "amazing_password",
            "",
        ),
        "host": os.getenv(
            "amazing_host",
            "",
        ),
        "port": int(
            os.getenv(
                "amazing_port",
                "0",
            )
        ),
        "local_path": os.getenv(
            "local_path",
            os.path.curdir,
        ),
    }

    manager = DataManager(provider_name="yinhe", config=config)

    print("\n股票数据与技术指标测试")

    if not manager.start():
        raise RuntimeError("数据源启动失败")

    symbol = "600519"

    try:
        # 1. 基础数据
        print(f"\n[1] 股票基础数据：{symbol}")

        stock = manager.get_stock(symbol)
        print(stock)

        # 2. K 线
        print("\n[2] 日 K 线")

        end_time = datetime.datetime.now()

        start_time = end_time - datetime.timedelta(days=720)

        klines = manager.get_kline(
            symbol=symbol,
            interval=Interval.DAY_1,
            start_time=start_time,
            end_time=end_time,
            limit=720,
        )

        print(f"共获取 {len(klines)} 条 K 线")

        # 3. 构建 DataFrame
        df = pandas.DataFrame(
            [
                {
                    "timestamp": item.timestamp,
                    "open": item.open,
                    "high": item.high,
                    "low": item.low,
                    "close": item.close,
                    "volume": item.volume,
                    "amount": item.amount,
                }
                for item in klines
            ]
        )

        # 按时间排序，并将 timestamp 作为索引
        df["timestamp"] = pandas.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        df = df.set_index("timestamp")

        # 4. 技术指标
        print("\n[3] 计算技术指标")

        ma = calculate_moving_averages(df)
        macd = calculate_macd(df)
        rsi = calculate_rsi(df, 12)
        williams = calculate_williams(df)
        boll = calculate_bollinger_bands(df)

        def fmt(value) -> str:
            """格式化指标数值。"""
            if value is None:
                return "--"

            return f"{float(value):.2f}"

        print("✓ MA")
        print(
            f"  MA3  = {fmt(ma.get('MA3'))}    "
            f"MA5  = {fmt(ma.get('MA5'))}    "
            f"MA10 = {fmt(ma.get('MA10'))}"
        )
        print(
            f"  MA20 = {fmt(ma.get('MA20'))}    "
            f"MA30 = {fmt(ma.get('MA30'))}    "
            f"MA60 = {fmt(ma.get('MA60'))}"
        )

        print("✓ MACD")
        print(
            f"  DIF  = {fmt(macd.get('DIF'))}    "
            f"DEA  = {fmt(macd.get('DEA'))}    "
            f"MACD = {fmt(macd.get('MACD'))}"
        )

        print("✓ RSI")
        print(f"  RSI12  = {fmt(rsi)}")

        print("✓ Williams")
        print(f"  Williams = {fmt(williams)}")

        print("✓ Bollinger Bands")
        print(
            f"  Upper  = {fmt(boll.get('upper'))}    "
            f"Middle = {fmt(boll.get('middle'))}    "
            f"Lower  = {fmt(boll.get('lower'))}"
        )

        # 5. 合并所有技术指标
        print("\n[4] 技术指标结果")

        indicators = pandas.concat(
            [
                ma,
                macd,
                rsi,
                williams,
                boll,
            ],
            axis=1,
        )

        print(indicators.to_string(index=False))

        # 6. 财务数据
        print("\n[5] 财务数据")

        financial = manager.get_financial(symbol)
        print(financial)

        # 7. 估值
        print("\n[6] 估值分析")

        valuation = ValuationAnalyzer()
        print(valuation)

        print("\n测试完成")

    finally:
        manager.stop()
        print("数据源已停止")
