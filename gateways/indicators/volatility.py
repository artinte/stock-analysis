from __future__ import annotations

import pandas


def calculate_bollinger_bands(
    df: pandas.DataFrame,
    period: int = 20,
    std_dev: float = 2,
) -> dict[str, float]:
    """
    计算布林带。

    返回：

        upper
        mid
        lower
    """

    if len(df) < period:

        return {
            "upper": 0.0,
            "mid": 0.0,
            "lower": 0.0,
        }

    close = df.sort_index()["close"]

    mid = close.rolling(period).mean()

    std = close.rolling(period).std()

    upper = mid + std * std_dev
    lower = mid - std * std_dev

    return {
        "upper": round(
            upper.iloc[-1],
            2,
        ),
        "mid": round(
            mid.iloc[-1],
            2,
        ),
        "lower": round(
            lower.iloc[-1],
            2,
        ),
    }
