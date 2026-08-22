"""
股票数据源 Provider 包。

具体数据源位于：

    providers.akshare
    providers.yinhe
    providers.tdx

Provider 的注册由各自的 gateway.py
通过 GatewayRegistry 装饰器自动完成。
"""

from providers.yinhe.gateway import YinheGateway
from providers.akshare.gateway import AkShareGateway