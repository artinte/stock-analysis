from polars import date


def fetch_etf_composition(
    self,
    symbol: str,
    trade_date: date | None = None,
):
    """
    获取 ETF 成分股列表

    :param symbol: ETF 代码
    :param trade_date: 交易日期，默认为 None，表示获取最新成分股列表
    :return: 成分股列表，包含股票代码、股票名称、持仓比例等信息
    """
    return self._fetch_etf_composition(symbol, trade_date)
