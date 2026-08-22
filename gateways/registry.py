from typing import Type

from gateways.gateway import StockDataGateway


class GatewayRegistry:
    """
    股票数据网关注册中心。

    Gateway 通过装饰器自动注册：

        @GatewayRegistry.register("akshare")
        class AkShareGateway(...):
            ...

    注册完成后：

        GatewayRegistry.names()

    即可获得所有可用数据源。
    """

    _gateways: dict[
        str,
        Type[StockDataGateway],
    ] = {}

    @classmethod
    def register(cls, name: str):
        """
        Gateway 注册装饰器。

        用法：

            @GatewayRegistry.register("akshare")
            class AkShareGateway(StockDataGateway):
                ...

        装饰器会自动完成：

            "akshare"
                ↓
            AkShareGateway
        """

        provider_name = name.strip().lower()

        if not provider_name:
            raise ValueError("数据源名称不能为空")

        def decorator(
            gateway_class: Type[StockDataGateway],
        ) -> Type[StockDataGateway]:

            if not issubclass(
                gateway_class,
                StockDataGateway,
            ):
                raise TypeError(
                    f"{gateway_class.__name__} " f"必须继承 StockDataGateway"
                )

            if provider_name in cls._gateways:

                registered = cls._gateways[provider_name]

                if registered is not gateway_class:
                    raise ValueError(f"数据源重复注册：" f"{provider_name}")

            else:
                cls._gateways[provider_name] = gateway_class

            return gateway_class

        return decorator

    @classmethod
    def create(
        cls,
        name: str,
        config: dict | None = None,
    ) -> StockDataGateway:

        provider_name = name.strip().lower()

        gateway_class = cls._gateways.get(provider_name)

        if gateway_class is None:

            available = ", ".join(cls.names())

            raise ValueError(
                f"不支持的数据源："
                f"{provider_name!r}；"
                f"当前支持："
                f"{available or '无'}"
            )

        return gateway_class(config=config or {})

    @classmethod
    def names(cls) -> list[str]:
        """
        获取所有已经注册的数据源。
        """

        return sorted(cls._gateways.keys())

    @classmethod
    def contains(
        cls,
        name: str,
    ) -> bool:
        return name.strip().lower() in cls._gateways

    @classmethod
    def count(cls) -> int:
        return len(cls._gateways)

    @classmethod
    def get(
        cls,
        name: str,
    ) -> Type[StockDataGateway]:
        """
        获取已经注册的数据源 Gateway 类。

        注意：
            这里只获取 Gateway 类，
            不会创建实例。

        示例：

            gateway_class = GatewayRegistry.get("akshare")

            print(gateway_class)
            print(gateway_class.display_name)
        """

        provider_name = name.strip().lower()

        gateway_class = cls._gateways.get(provider_name)

        if gateway_class is None:

            available = ", ".join(cls.names())

            raise ValueError(
                f"不支持的数据源："
                f"{provider_name!r}；"
                f"当前支持："
                f"{available or '无'}"
            )

        return gateway_class
