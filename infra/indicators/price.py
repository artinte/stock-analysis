from __future__ import annotations


def calculate_change(
    price: float,
    last_close: float,
) -> float:
    """计算涨跌额。"""

    return round(
        price - last_close,
        3,
    )


def calculate_change_pct(
    price: float,
    last_close: float,
) -> float:
    """计算涨跌幅。"""

    if last_close == 0:
        return 0.0

    return round(
        (price - last_close) / last_close * 100,
        2,
    )


def calculate_amplitude(
    high: float,
    low: float,
    last_close: float,
) -> float:
    """计算振幅。"""

    if last_close == 0:
        return 0.0

    return round(
        (high - low) / last_close * 100,
        2,
    )


def calculate_average_price(
    amount: float,
    volume: float,
    price: float,
) -> float:
    """计算成交均价。"""

    if volume <= 0:
        return price

    return round(
        amount / volume,
        2,
    )


def calculate_limit_prices(
    last_close: float,
    limit_rate: float = 0.10,
) -> tuple[float, float]:
    """
    计算涨停价和跌停价。

    注意：
    不同市场和板块存在不同涨跌停规则。
    这里仅提供通用百分比计算。
    """

    limit_up = round(
        last_close * (1 + limit_rate),
        2,
    )

    limit_down = round(
        last_close * (1 - limit_rate),
        2,
    )

    return limit_up, limit_down
