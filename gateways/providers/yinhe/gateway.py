from __future__ import annotations

from typing import Optional

from base import StockDataGateway
from registry import GatewayRegistry


@GatewayRegistry.register("yinhe")
class YinheGateway(StockDataGateway):
    """
    银河证券数据网关。

    该类负责将银河证券的数据接口封装成统一的
    StockDataGateway 接口。

    上层业务不应该直接调用银河证券的底层接口，
    而应该通过：

        DataManager
            ↓
        YinheGateway

    访问数据。

    这样以后更换数据源时，上层业务无需修改。
    """

    name = "yinhe"

    display_name = "银河证券"

    def __init__(
        self,
        config: Optional[dict] = None,
    ) -> None:
        """
        初始化银河数据网关。

        Parameters
        ----------
        config:
            银河数据源配置。

        当前可以包含：

            {
                "host": "...",
                "port": 1234,
                "username": "...",
                "password": "..."
            }

        后续接入真实银河接口时，可以在这里
        初始化对应的 Client。
        """

        self.config = config or {}

        self.client = None

        self._started = False

    def login(
        self,
        config: Optional[dict] = None,
    ) -> bool:
        """
        建立银河数据源连接。

        Parameters
        ----------
        config:
            启动时传入的数据源配置。

        Returns
        -------
        bool
            True 表示连接成功。
        """

        if config:
            self.config.update(config)

        # ==================================================
        # TODO:
        #
        # 这里接入真实银河证券 API。
        #
        # 例如：
        #
        # self.client = YinheClient(
        #     host=self.config.get("host"),
        #     port=self.config.get("port"),
        #     username=self.config.get("username"),
        #     password=self.config.get("password"),
        # )
        #
        # self.client.connect()
        #
        # ==================================================

        self._started = True

        return True

    def logout(self) -> None:
        """
        关闭银河数据源连接。
        """

        if self.client is not None:

            # ==================================================
            # TODO:
            #
            # 接入真实银河接口后：
            #
            # self.client.close()
            #
            # ==================================================

            self.client = None

        self._started = False

    def health_check(self) -> bool:
        """
        检查银河数据源是否可用。

        当前没有接入真实银河 API 时，
        仅返回当前连接状态。
        """

        return self._started

    def fetch_stock(
        self,
        symbol: str,
    ):
        """
        获取股票基础信息。

        Parameters
        ----------
        symbol:
            标准证券代码。

            例如：

                600519.SH
                000001.SZ

        Returns
        -------
        Stock
            标准化股票对象。
        """

        self._ensure_started()

        # ==================================================
        # TODO:
        #
        # 调用银河接口获取股票基础信息，
        # 然后转换成 models.stock.Stock。
        #
        # ==================================================

        raise NotImplementedError(
            "YinheGateway.fetch_stock() "
            "尚未接入银河证券股票基础信息接口"
        )

    def fetch_quote(
        self,
        symbol: str,
    ):
        """
        获取单只股票最新行情。
        """

        self._ensure_started()

        # ==================================================
        # TODO:
        #
        # 调用银河实时行情接口，
        # 转换成 models.quote.Quote。
        #
        # ==================================================

        raise NotImplementedError(
            "YinheGateway.fetch_quote() "
            "尚未接入银河证券实时行情接口"
        )

    def fetch_quotes(
        self,
        symbols: list[str],
    ):
        """
        批量获取股票最新行情。

        Parameters
        ----------
        symbols:
            股票代码列表。

        Returns
        -------
        list[Quote]
            标准化行情列表。
        """

        self._ensure_started()

        if not symbols:
            return []

        # ==================================================
        # TODO:
        #
        # 如果银河接口支持批量查询，
        # 应该优先使用批量接口。
        #
        # 不建议这里简单循环 fetch_quote，
        # 因为实际生产环境中性能会比较差。
        #
        # ==================================================

        raise NotImplementedError(
            "YinheGateway.fetch_quotes() "
            "尚未接入银河证券批量行情接口"
        )

    def fetch_kline(
        self,
        symbol: str,
        interval,
        start_time=None,
        end_time=None,
        limit: int = 1000,
    ):
        """
        获取历史 K 线。

        Parameters
        ----------
        symbol:
            股票代码。

        interval:
            K 线周期。

        start_time:
            开始时间。

        end_time:
            结束时间。

        limit:
            最大返回数量。

        Returns
        -------
        list[Kline]
            标准化 K 线数据。
        """

        self._ensure_started()

        # ==================================================
        # TODO:
        #
        # 调用银河历史行情接口。
        #
        # 原始数据必须转换成：
        #
        # models.kline.Kline
        #
        # ==================================================

        raise NotImplementedError(
            "YinheGateway.fetch_kline() "
            "尚未接入银河证券 K 线接口"
        )

    def fetch_valuation(
        self,
        symbol: str,
    ):
        """
        获取股票估值数据。

        包括：

            PE(TTM)
            PE(动态)
            PE(静态)
            PB
            PS
            总市值
            流通市值
            当前价格

        Returns
        -------
        Valuation
            标准化估值对象。
        """

        self._ensure_started()

        # ==================================================
        # TODO:
        #
        # 调用银河估值/行情接口。
        #
        # 转换成：
        #
        # models.valuation.Valuation
        #
        # ==================================================

        raise NotImplementedError(
            "YinheGateway.fetch_valuation() "
            "尚未接入银河证券估值接口"
        )

    def _ensure_started(self) -> None:
        """
        确保数据源已经启动。
        """

        if not self._started:

            raise RuntimeError(
                "银河数据源尚未启动，请先调用 "
                "DataManager.start()"
            )