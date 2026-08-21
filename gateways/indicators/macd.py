from __future__ import annotations

import pandas


def calculate_macd(
    df: pandas.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict[str, float]:
    """
    计算 MACD。

    返回：

        dif
        dea
        hist
    """

    if len(df) < slow + signal:

        return {
            "dif": 0.0,
            "dea": 0.0,
            "hist": 0.0,
        }

    close = df.sort_index()["close"]

    ema_fast = close.ewm(
        span=fast,
        adjust=False,
    ).mean()

    ema_slow = close.ewm(
        span=slow,
        adjust=False,
    ).mean()

    dif = ema_fast - ema_slow

    dea = dif.ewm(
        span=signal,
        adjust=False,
    ).mean()

    hist = (dif - dea) * 2

    return {
        "dif": round(
            dif.iloc[-1],
            2,
        ),
        "dea": round(
            dea.iloc[-1],
            2,
        ),
        "hist": round(
            hist.iloc[-1],
            2,
        ),
    }
