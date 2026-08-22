"""
股票数据源 Provider 包。

具体数据源位于：

    providers.akshare
    providers.yinhe
    providers.tdx

Provider 的注册由各自的 gateway.py
通过 GatewayRegistry 装饰器自动完成。
"""

"""
内置股票数据源。

导入各个 Gateway，使其注册装饰器自动执行。
"""

from .akshare.gateway import AkShareGateway
from .yinhe.gateway import YinheGateway

__all__ = [
    "AkShareGateway",
    "YinheGateway",
]