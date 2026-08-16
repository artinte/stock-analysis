import utils.constants as constants


def add_exchange_suffix(stock_code):
    """
    根据 A 股代码规则添加交易所后缀
    逻辑：已有后缀不处理，无后缀根据前缀自动补全
    """
    if not stock_code:
        return ""

    # 1. 预处理：转大写并去空格
    code = stock_code.strip().upper()

    # 2. 如果已经有正确后缀，直接返回
    if code.endswith((".SH", ".SZ", ".BJ")):
        return code

    # 3. 提取纯数字部分，防止类似 600519.ss 的错误输入
    base_code = code.split(".")[0]

    # 4. 根据你提供的前缀常量进行判断
    # 沪市 (SH)
    if base_code.startswith(constants.SSE_MAIN_BOARD_PREFIX) or base_code.startswith(
        constants.SSE_STAR_MARKET_PREFIX
    ):
        return f"{base_code}.SH"

    # 深市 (SZ)
    if base_code.startswith(constants.SZSE_MAIN_BOARD_PREFIX) or base_code.startswith(
        constants.SZSE_CHINEXT_PREFIX
    ):
        return f"{base_code}.SZ"

    # 北交所 (BJ)
    if base_code.startswith(constants.BSE_PREFIXES):
        return f"{base_code}.BJ"

    # 5. 不匹配则返回原始 base_code
    return base_code
