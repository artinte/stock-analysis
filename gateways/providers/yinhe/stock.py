from typing import Optional


class YinheStock:
    """
    银河证券股票基础信息适配器。

    负责：

        - 获取股票基本信息
        - 股票名称查询

    数据流：

        AmazingData
             |
             ↓
        DataFrame / List[Dict]
             |
             ↓
        Stock Model

    注意：

        本类不是独立数据源。
        它属于 YinheGateway 内部功能模块，
        通过组合方式被 YinheGateway 使用。
    """

    def __init__(
        self,
        gateway,
    ):
        """
        保存银河主网关引用。

        通过 gateway 可以访问：

            gateway.info_data
            gateway._ensure_started()
            gateway._normalize_symbol()

        """

        self.gateway = gateway

    # ==========================================================
    # 股票基础信息
    # ==========================================================

    def fetch_stock(
        self,
        symbol: str,
    ):
        """
        获取股票基础信息。

        返回：

            {
                "symbol": "600519.SH",
                "name": "贵州茅台"
            }

        """

        self.gateway._ensure_started()

        code = self.gateway._normalize_symbol(symbol)

        try:

            stock_basic = self.gateway.info_data.get_stock_basic([code])

            if stock_basic is None:
                return None

            # ----------------------------------------------
            # DataFrame
            # ----------------------------------------------

            if hasattr(
                stock_basic,
                "empty",
            ):

                if stock_basic.empty:
                    return None

                row = stock_basic.iloc[0]

                return {
                    "symbol": code,
                    "name": row.get("SECURITY_NAME"),
                }

            # ----------------------------------------------
            # List[Dict]
            # ----------------------------------------------

            if isinstance(
                stock_basic,
                list,
            ):

                if not stock_basic:
                    return None

                item = stock_basic[0]

                return {
                    "symbol": code,
                    "name": item.get("SECURITY_NAME"),
                }

            return None

        except Exception as e:

            print(f"[银河网关] 获取股票信息失败 " f"{code}: {e}")

            return None

    # ==========================================================
    # 股票名称
    # ==========================================================

    def fetch_stock_name(
        self,
        symbol: str,
    ) -> str:
        """
        获取股票名称。

        内部辅助方法。
        """

        self.gateway._ensure_started()

        code = self.gateway._normalize_symbol(symbol)

        try:

            stock_basic = self.gateway.info_data.get_stock_basic([code])

            # DataFrame

            if hasattr(
                stock_basic,
                "empty",
            ):

                if not stock_basic.empty:

                    return stock_basic["SECURITY_NAME"].iloc[0]

            # List[Dict]

            elif isinstance(
                stock_basic,
                list,
            ):

                if stock_basic:

                    return stock_basic[0].get(
                        "SECURITY_NAME",
                        "未知名称",
                    )

            return "未知名称"

        except Exception as e:

            print(f"[银河网关] 获取股票名称失败 " f"{code}: {e}")

            return "获取失败"
