def calculate_precise_rsi(prices, target_index=-1, period=14, warm_up=150):
    """精准计算某一天（或最新一天）的标准 RSI，完美对齐商业行情软件。

    :param prices: List[float], 完整的历史收盘价列表（时间从远到近）。
                   为了保证精准度，列表长度建议大于 150 天。
    :param target_index: int, 你想要获取哪一天的 RSI。
                         默认 -1 代表计算最新（今天）的 RSI；
                         如果要计算倒数第二天，传 -2。
    :param period: int, RSI 的计算周期，标准为 14 天。
    :param warm_up: int, 预热天数。默认 150 天，用来让“套娃公式”的历史回音收敛稳定。
    :return: float, 目标日期的精确 RSI 值。如果数据不足则返回 None。
    """
    # 将负数索引转换为绝对索引位置
    if target_index < 0:
        target_index = len(prices) + target_index

    # 核心安全检查：计算目标日之前，必须有足够的历史数据供“预热 + 基础周期”消耗
    required_days = period + warm_up
    if target_index < required_days - 1:
        # 数据严重不足，强行计算会导致严重偏差，直接截断
        print(f"警告: 目标日之前只有 {target_index + 1} 天数据，少于建议的预热要求 {required_days} 天。")
        if target_index < period:
            return None

    # 1. 截取从“最远历史起点”到“目标日”的数据片段（切片是左闭右开，所以 +1）
    start_index = max(0, target_index - required_days + 1)
    sub_prices = prices[start_index : target_index + 1]

    if len(sub_prices) <= period:
        return None

    # 2. 计算第一阶段（最早期）的简单平均数作为算法启动资金
    total_gain = 0.0
    total_loss = 0.0
    for i in range(1, period + 1):
        change = sub_prices[i] - sub_prices[i - 1]
        if change > 0:
            total_gain += change
        else:
            total_loss += abs(change)

    avg_gain = total_gain / period
    avg_loss = total_loss / period

    # 3. 开始漫长的“滚雪球/套娃”预热迭代，直到滚到目标日期
    for i in range(period + 1, len(sub_prices)):
        change = sub_prices[i] - sub_prices[i - 1]
        current_gain = change if change > 0 else 0.0
        current_loss = abs(change) if change < 0 else 0.0

        # 标准 Wilder 平滑移动平均公式，让时间不断稀释早期的误差
        avg_gain = (avg_gain * (period - 1) + current_gain) / period
        avg_loss = (avg_loss * (period - 1) + current_loss) / period

    # 4. 滚到了最后一天（即目标日），计算最终的精准 RSI
    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    precise_rsi = 100.0 - (100.0 / (1.0 + rs))

    return round(precise_rsi, 4)
