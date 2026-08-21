from __future__ import annotations

import numpy
import pandas


def calculate_williams(
    df: pandas.DataFrame,
    price: float | None = None,
    period: int = 14,
) -> float:
    """
    计算 Williams %R。
    """

    if len(df) < period:
        return 0.0

    recent = df.tail(period)

    highest = recent["high"].max()
    lowest = recent["low"].min()

    if price is None:
        price = float(df["close"].iloc[-1])

    if highest == lowest:
        return 0.0

    return round(
        (highest - price) / (highest - lowest) * 100,
        2,
    )


def calculate_rsi(
    df: pandas.DataFrame,
    period: int = 14,
) -> float:
    """
    计算 RSI。
    """

    if len(df) <= period:
        return 0.0

    close = df.sort_index()["close"]

    delta = close.diff()

    gain = delta.where(delta > 0, 0).rolling(period).mean()

    loss = -delta.where(delta < 0, 0).rolling(period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    value = rsi.iloc[-1]

    if numpy.isnan(value):
        return 0.0

    return round(
        value,
        2,
    )
