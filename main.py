import AmazingData
from gateways.data_manager import DataManager
import watchlists
import utils.utils_func as utils_func
from dotenv import dotenv_values

converted_code = "603893.SH"  # 目标股票代码
DAYS_TO_FETCH = 15  # 需要获取最近 15 个交易日的数据

# 股票预测系统
# 总体要求根据输入的数据预测未来一天的股价的变化
# 输入：(最高点、最低点、收盘价)、季度营收、利润、A股指数
# 输出：未来一天的股价变化


def main():
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

    quit()

    try:
        # --- 2. 登录 AmazingData ---
        AmazingData.login(
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=int(config["port"]),
        )
        print("AmazingData 登录成功。")

        # --- 3. 准备数据查询对象和日期 ---
        base_data_object = AmazingData.BaseData()
        # 获取交易日历
        calendar = base_data_object.get_calendar()

        if len(calendar) < DAYS_TO_FETCH:
            print(f"交易日历数据不足 {DAYS_TO_FETCH} 天，无法执行策略。")
            return

        # 确定查询范围：从倒数第 15 个交易日到最新的交易日
        begin_date = calendar[-DAYS_TO_FETCH]
        end_date = calendar[-1]

        # 实例化 MarketData 对象，用于查询历史行情
        market_data_object = AmazingData.MarketData(calendar=calendar)

        # for name, code in watchlists.Watchlists.items():
        for name, code in {"瑞芯微": "001389"}.items():
            converted_code = utils_func.add_exchange_suffix(code)
            print(
                f"正在查询股票 {converted_code} 从 {begin_date} 到 {end_date} 的日线数据..."
            )

            # --- 4. 获取历史 K 线数据（日线） ---
            # 接口和参数是推测的，请根据手册确认

            kline_data = market_data_object.query_kline(
                code_list=[converted_code],
                begin_date=begin_date,
                end_date=end_date,
                period=AmazingData.constant.Period.day.value,  # 日线
            )
            if (
                not kline_data
                or converted_code not in kline_data
                or kline_data[converted_code].empty
            ):
                print(f"未能获取到股票 {converted_code} 的 K 线数据或数据为空。")
                continue

            df = kline_data[converted_code]

            if len(df) < DAYS_TO_FETCH:
                print(
                    f"获取到的数据不足 {DAYS_TO_FETCH} 个交易日，请检查查询日期范围。实际数据量: {len(df)}"
                )
                continue

            # 按日期升序排列，确保最新的数据在最后 (最新交易日即为第 15 天)
            df = df.sort_index(ascending=True)

            # --- 5. 策略逻辑实现 ---
            print(df)
            # 提取收盘价序列，假设收盘价字段名为 'CLOSE'
            close_prices = df["close"].tail(DAYS_TO_FETCH)  # 确保只使用最近 15 天的数据

            high_prices = df["high"].tail(DAYS_TO_FETCH)  # 最高价序列
            low_prices = df["low"].tail(DAYS_TO_FETCH)  # 最低价序列

            # A. 计算 15 天收盘价的平均值
            avg_15 = close_prices.mean()
            high_15 = high_prices.mean()
            low_15 = low_prices.mean()

            # B. 获取关键日的收盘价
            # T15 - 第 15 天收盘价 (当前价)
            close_t15 = close_prices.iloc[-1]

            price_change_rate = abs(close_t15 - avg_15) / avg_15
            is_price_near_average = price_change_rate <= 0.02

            if is_price_near_average:
                # E. 触发买入条件
                print("\n" + "=" * 40)
                print(f"  ⭐ 股票 {name} {converted_code} 策略分析结果 ⭐")
                print("=" * 40)
                print(f"  15 日平均收盘价: {avg_15:.2f}")
                print(f"  最新收盘价 (T15): {close_t15:.2f}")

                print("\n  ✅ **买入信号触发**")
            print("=" * 40)

    except Exception as e:
        print(f"\n[错误] 执行过程中发生错误: {e}")
    finally:
        # --- 6. 登出 API ---
        try:
            AmazingData.logout(username="11300020643")
            print("\nAmazingData 登出完成。")
        except Exception as e:
            print(f"\n[警告] 登出时发生错误: {e}")


if __name__ == "__main__":
    main()
