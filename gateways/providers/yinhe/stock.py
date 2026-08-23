from __future__ import annotations

from typing import Optional

from gateways.models.stock import Stock
from utils.stock_mapping import normalize_symbol


class YinheStock:
    """
    银河证券股票基础信息适配器。

    负责：
        AmazingData.get_stock_basic()

    转换：

        DataFrame
            ↓
        Stock Model

    注意：
        不包含其它数据源逻辑。
    """

    def __init__(
        self,
        gateway,
    ):
        """
        gateway:
            YinheGateway 实例

        通过组合方式访问：
            login 状态
            AmazingData 对象
            工具方法
        """

        self.gateway = gateway

    def fetch_stock(
        self,
        symbol: str,
    ) -> Optional[Stock]:
        """
        获取股票基础信息。
        """

        self.gateway._ensure_started()

        code = normalize_symbol(symbol)

        try:

            stock_basic = self.gateway.info_data.get_stock_basic([code])

            if stock_basic is None:
                return None

            # ==================================================
            # DataFrame
            # ==================================================

            if hasattr(
                stock_basic,
                "empty",
            ):
                if stock_basic is None or stock_basic.empty:
                    return None

                row = stock_basic.iloc[0]

                return Stock(
                    symbol=row["MARKET_CODE"],
                    name=row["SECURITY_NAME"],
                    company_name=row.get("COMP_NAME"),
                    market=row.get("LISTPLATE_NAME"),
                    listing_date=str(row.get("LISTDATE")),
                    delisting_date=str(row.get("DELISTDATE")),
                    listed_status=row.get("IS_LISTED"),
                    source="yinhe",
                )
            return None

        except Exception as e:

            print(f"[银河网关] 获取股票信息失败 " f"{code}: {e}")

            return None

    def fetch_stock_name(
        self,
        symbol: str,
    ) -> str:
        """
        获取股票名称。

        内部辅助接口。
        """

        self._ensure_started()

        formatted_symbol = normalize_symbol(symbol)

        try:
            stock_basic = self.info_data.get_stock_basic([formatted_symbol])

            # DataFrame
            if hasattr(stock_basic, "empty"):

                if not stock_basic.empty:
                    return stock_basic["SECURITY_NAME"].iloc[0]

            # List[Dict]
            elif isinstance(stock_basic, list):

                if stock_basic:
                    return stock_basic[0].get(
                        "SECURITY_NAME",
                        "未知名称",
                    )

            return "未知名称"

        except Exception as e:

            print(f"[银河网关] 获取股票名称失败 " f"{formatted_symbol}: {e}")

            return "获取失败"
