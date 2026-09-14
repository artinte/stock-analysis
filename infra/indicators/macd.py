from __future__ import annotations

import pandas


def calculate_macd_commercial(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    符合国内商业软件（通达信/同花顺）标准的完整 MACD 序列计算。
    注意：传入的 df 必须已经是按时间【正序】排列（旧数据在上，新数据在下）。
    建议传入的 df 长度大于 200 根 K 线以确保 EMA 算法收敛。
    """
    # 商业生产环境通常在进入函数前保证数据合规，此处做防御性检查
    if len(df) < (slow + signal + 30):  # 适当提高阈值，提示数据不足
        raise ValueError("数据量过少，会导致 MACD 产生严重的初始截断误差！")

    close = df["close"]

    # 1. 计算快慢 EMA（adjust=False 完美对齐金融软件递推公式）
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()

    # 2. 计算 DIF
    dif = ema_fast - ema_slow

    # 3. 计算 DEA（DIF 的 EMA）
    dea = dif.ewm(span=signal, adjust=False).mean()

    # 4. 计算 MACD 柱状图（国内标准乘以 2）
    hist = (dif - dea) * 2

    # 商业化通常返回整个 DataFrame 供画线或回测，同时保留 4 位精度防后续计算漂移
    macd_df = pd.DataFrame({
        "DIF": dif,
        "DEA": dea,
        "MACD": hist
    }, index=df.index).round(4)

    return macd_df
