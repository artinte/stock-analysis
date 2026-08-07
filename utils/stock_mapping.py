# -*- coding: utf-8 -*-
from typing import Optional, Union
from stock_industry_category import get_stock_industry_category

"""
==============================================================================
模块名称 (Module Name) : Stock Convenient Utilities
功能描述 (Description) : 股票代码与名称互转等实用快捷函数模块。

上海证券交易所所有股票：https://www.sse.com.cn/assortment/stock/list/share/
深证证券交易所所有股票：https://www.szse.cn/market/product/stock/list/index.html

==============================================================================
"""


def stock_code_to_name(
    code: Union[str, int], default: Optional[str] = None
) -> Optional[str]:
    """根据股票代码获取股票名称"""
    query_result = get_stock_industry_category(code)
    items = query_result.to_list()
    if items:
        return items[0].name
    return default


def stock_name_to_code(name: str, default: Optional[str] = None) -> Optional[str]:
    """根据股票名称获取股票代码"""
    query_result = get_stock_industry_category(name)
    items = query_result.to_list()
    if items:
        return items[0].code
    return default


if __name__ == "__main__":
    print("==================================================================")
    print(" 快捷 API 测试")
    print("==================================================================")
    print(f"代码 '600519' -> 名称: {stock_code_to_name('600519')}")
    print(f"代码 1 -> 名称: {stock_code_to_name(1)}")
    print(f"名称 '平安银行' -> 代码: {stock_name_to_code('平安银行')}")
    print(f"不存在股票 -> 代码: {stock_name_to_code('不存在股票', default='未查到')}")
