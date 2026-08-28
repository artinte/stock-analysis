from __future__ import annotations

from datetime import date
from typing import Optional

from core.models.stock import Stock
from utils.stock_mapping import normalize_symbol, get_exchange


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

        # 股票名称缓存
        #
        #     600519.SH -> 贵州茅台
        #     000001.SZ -> 平安银行
        #
        # 只缓存成功获取到的名称。
        self._stock_name_cache: dict[str, str] = {}

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

            if hasattr(
                stock_basic,
                "empty",
            ):
                if stock_basic is None or stock_basic.empty:
                    return None

                row = stock_basic.iloc[0]

                # 获取交易所代号
                exchange = get_exchange(code)

                stock_name = row.get("SECURITY_NAME")

                if stock_name:
                    self._stock_name_cache[code] = stock_name

                return Stock(
                    symbol=row["MARKET_CODE"],
                    name=stock_name,
                    company_name=row.get("COMP_NAME"),
                    exchange=exchange,
                    market=row.get("LISTPLATE_NAME"),
                    listing_date=row.get("LISTDATE"),
                    delisting_date=row.get("DELISTDATE"),
                    listed_status=row.get("IS_LISTED"),
                    source=self.gateway.display_name,
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

        优先从内存缓存读取。
        缓存不存在时才请求银河接口。

        注意：
            只有成功获取到的真实股票名称才会进入缓存。
        """

        self.gateway._ensure_started()
        formatted_symbol = normalize_symbol(symbol)

        # 1. 优先读取缓存
        cached_name = self._stock_name_cache.get(formatted_symbol)
        if cached_name:
            return cached_name

        # 2. 缓存不存在，请求银河接口
        try:
            stock_basic = self.gateway.info_data.get_stock_basic([formatted_symbol])

            if hasattr(stock_basic, "empty"):
                if not stock_basic.empty:
                    stock_name = stock_basic["SECURITY_NAME"].iloc[0]

                    # 3. 获取成功，写入缓存
                    self._stock_name_cache[formatted_symbol] = stock_name

                    return stock_name

            return "未知名称"

        except Exception as e:
            print(f"[银河网关] 获取股票名称失败 " f"{formatted_symbol}: {e}")
            return "获取失败"
