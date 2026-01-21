import constants


def add_exchange_suffix_with_bse(stock_code):
    """根据A股代码规则添加交易所后缀 (包含北交所)"""

    # 沪市 (SH)
    if stock_code.startswith(constants.SSE_MAIN_BOARD_PREFIX) or stock_code.startswith(
        constants.SSE_STAR_MARKET_PREFIX
    ):
        return f"{stock_code}.SH"
    # 深市 (SZ)
    elif stock_code.startswith(
        constants.SZSE_MAIN_BOARD_PREFIX
    ) or stock_code.startswith(constants.SZSE_CHINEXT_PREFIX):
        return f"{stock_code}.SZ"
    # 北交所 (BJ)
    for prefix in constants.BSE_PREFIXES:
        if stock_code.startswith(prefix):
            return f"{stock_code}.BJ"
    else:
        return stock_code
