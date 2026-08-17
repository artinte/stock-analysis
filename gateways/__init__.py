"""
股票数据网关模块。

负责：

    1. 暴露 DataManager
    2. 暴露 GatewayRegistry
    3. 加载内置数据源
    4. 自动完成数据源注册
"""

from .manager import DataManager
from .registry import GatewayRegistry

# ============================================================
# 加载内置 Gateway
#
# 这里非常重要。
#
# Gateway 的注册代码位于各自的 gateway.py。
# 必须 import 它们，装饰器才会执行。
# ============================================================

from .providers.akshare.gateway import AkShareGateway
from .providers.yinhe.gateway import YinheGateway

__all__ = [
    "DataManager",
    "GatewayRegistry",
    "AkShareGateway",
    "YinheGateway",
    "TdxGateway",
]