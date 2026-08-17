class YinheClient:
    """
    银河证券底层客户端。

    这里放原来的：

        登录
        socket/http 连接
        API 调用
        原始数据解析

    不负责 StockDetail。
    """

    def __init__(
        self,
        config: dict | None = None,
    ):
        self.config = config or {}

    def login(self) -> bool:
        # 原来的登录代码
        ...

    def fetch_market_data(
        self,
        symbol: str,
    ):
        # 原来的银河行情代码
        ...

    def logout(self) -> None:
        # 原来的退出代码
        ...