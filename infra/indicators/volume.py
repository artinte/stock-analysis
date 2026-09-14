from __future__ import annotations

import pandas


def calculate_volume_ratio(
    df: pandas.DataFrame,
) -> float:
    """
    计算日线量比。

    当前计算方式：

        当日成交量 /
        前五个交易日平均成交量
    """

    if len(df) < 6:
        return 0.0

    current_volume = df.iloc[-1]["volume"]

    average_volume = df.iloc[-6:-1]["volume"].mean()

    if average_volume <= 0:
        return 0.0

    return round(
        current_volume / average_volume,
        2,
    )


def calculate_turnover(
    volume: float,
    float_shares: float,
) -> float:
    """
    计算换手率。

    volume 和 float_shares 均按照数据源
    对应的原始股数单位传入。
    """

    if float_shares <= 0:
        return 0.0

    return round(
        volume / (float_shares * 100) * 100,
        2,
    )
