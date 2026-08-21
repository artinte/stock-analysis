from __future__ import annotations

from typing import Optional

import pandas


def calculate_moving_averages(
    df: pandas.DataFrame,
    periods: Optional[list[int]] = None,
) -> dict[str, Optional[float]]:
    """
    计算移动平均线。

    默认：

    MA3
    MA5
    MA10
    MA20
    MA30
    MA60
    """

    periods = periods or [
        3,
        5,
        10,
        20,
        30,
        60,
    ]

    result: dict[str, Optional[float]] = {}

    df = df.sort_index()

    for period in periods:

        if len(df) >= period:

            result[f"MA{period}"] = round(
                df["close"]
                .tail(period)
                .mean(),
                2,
            )

        else:

            result[f"MA{period}"] = None

    return result


def calculate_bias(
    price: float,
    ma5: Optional[float],
) -> float:
    """
    计算 MA5 乖离率。

    BIAS = (当前价格 - MA5) / MA5 × 100%
    """

    if not ma5 or ma5 <= 0:
        return 0.0

    return round(
        (price - ma5)
        / ma5
        * 100,
        2,
    )