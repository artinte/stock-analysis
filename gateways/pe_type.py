from enum import Enum


class PEType(Enum):
    STATIC = "static"  # 静态市盈率：市值 / 上年净利润
    TTM = "ttm"  # 滚动市盈率：市值 / 最近四个季度的净利润总和
    DYNAMIC = "dynamic"  # 动态市盈率：市值 / 预测全年利润（通常按最新季报等比例折算）
