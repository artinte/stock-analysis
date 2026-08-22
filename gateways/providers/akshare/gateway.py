from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import akshare as ak

from gateway import StockDataGateway
from registry import GatewayRegistry

from models.constants import Interval
from models.stock import Stock
from models.quote import Quote
from models.kline import Kline
from models.valuation import Valuation
from models.financial import Financial


@GatewayRegistry.register("akshare")
class AkShareGateway(StockDataGateway):
    """
    AkShare 股票数据网关。

    AkShare 是本项目默认的数据源。

    负责将 AkShare 返回的原始数据统一转换成
    项目内部的标准 Model。

    上层业务不应该直接调用 AkShare，而应该通过：

        DataManager
            ↓
        StockDataGateway
            ↓
        AkShareGateway
            ↓
        AkShare

    这样后续可以非常方便地切换：

        AkShare
        银河证券
        通达信
        其他数据源
    """

    name = "akshare"

    display_name = "AkShare"

    def __init__(
        self,
        config: Optional[dict] = None,
    ) -> None:
        """
        初始化 AkShare 数据源。
        """

        super().__init__(config)

    # ==========================================================
    # 生命周期
    # ==========================================================

    def login(
        self,
        config: Optional[dict] = None,
    ) -> bool:
        """
        初始化 AkShare。

        AkShare 本身不需要账号登录，因此这里主要负责
        Gateway 生命周期管理。
        """

        if config:
            self.config.update(config)

        self._started = True

        return True

    def logout(self) -> None:
        """
        关闭 AkShare 数据源。
        """

        self._started = False

    def health_check(self) -> bool:
        """
        检查 AkShare 是否可以正常访问。

        使用 A 股实时行情接口进行简单探测。
        """

        try:
            self._ensure_started()

            data = ak.stock_zh_a_spot_em()
            return (
                data is not None
                and not data.empty
            )
        except Exception as exc:
            print("异常信息:", exc)
            return False

    # ==========================================================
    # 股票基础信息
    # ==========================================================

    def get_stock(
        self,
        symbol: str,
    ) -> Stock:
        """
        获取股票基础信息。
        """

        self._ensure_started()

        code = self._normalize_symbol(symbol)

        data = ak.stock_zh_a_spot_em()

        if data is None or data.empty:
            raise RuntimeError(
                "AkShare 未返回股票基础数据"
            )

        row = data[
            data["代码"].astype(str) == code
        ]

        if row.empty:
            raise ValueError(
                f"未找到股票：{symbol}"
            )

        item = row.iloc[0]

        return Stock(
            symbol=symbol,
            name=self._get_value(
                item,
                "名称",
            ),
            market=self._detect_market(code),
            industry=None,
        )

    # ==========================================================
    # 单只行情
    # ==========================================================

    def get_quote(
        self,
        symbol: str,
    ) -> Quote:
        """
        获取单只股票最新行情。
        """

        self._ensure_started()

        code = self._normalize_symbol(symbol)

        data = ak.stock_zh_a_spot_em()

        if data is None or data.empty:
            raise RuntimeError(
                "AkShare 未返回实时行情"
            )

        row = data[
            data["代码"].astype(str) == code
        ]

        if row.empty:
            raise ValueError(
                f"未找到股票：{symbol}"
            )

        return self._convert_quote(
            symbol,
            row.iloc[0],
        )

    # ==========================================================
    # 批量行情
    # ==========================================================

    def get_quotes(
        self,
        symbols: list[str],
    ) -> list[Quote]:
        """
        批量获取股票行情。

        AkShare 一次获取全市场行情，然后本地筛选。

        相比：

            for symbol in symbols:
                get_quote(symbol)

        只请求一次数据源，效率更高。
        """

        self._ensure_started()

        if not symbols:
            return []

        data = ak.stock_zh_a_spot_em()

        if data is None or data.empty:
            return []

        symbol_map = {
            self._normalize_symbol(symbol): symbol
            for symbol in symbols
        }

        result: list[Quote] = []

        for _, row in data.iterrows():

            code = str(
                row["代码"]
            )

            original_symbol = symbol_map.get(
                code
            )

            if original_symbol is None:
                continue

            result.append(
                self._convert_quote(
                    original_symbol,
                    row,
                )
            )

        return result

    # ==========================================================
    # K 线
    # ==========================================================

    def get_kline(
        self,
        symbol: str,
        interval: Interval = Interval.DAY_1,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> list[Kline]:
        """
        获取历史 K 线。

        支持日、周、月以及分钟周期。
        """

        self._ensure_started()

        code = self._normalize_symbol(symbol)

        period = self._convert_interval(
            interval
        )

        start_date = (
            start_time.strftime("%Y%m%d")
            if start_time
            else "19900101"
        )

        end_date = (
            end_time.strftime("%Y%m%d")
            if end_time
            else datetime.now().strftime("%Y%m%d")
        )

        data = ak.stock_zh_a_hist(
            symbol=code,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust="qfq",
        )

        if data is None or data.empty:
            return []

        result: list[Kline] = []

        for _, row in data.iterrows():

            result.append(
                Kline(
                    symbol=symbol,
                    timestamp=self._parse_datetime(
                        row["日期"]
                    ),
                    open=self._to_float(
                        row["开盘"]
                    ),
                    high=self._to_float(
                        row["最高"]
                    ),
                    low=self._to_float(
                        row["最低"]
                    ),
                    close=self._to_float(
                        row["收盘"]
                    ),
                    volume=self._to_float(
                        row["成交量"]
                    ),
                    amount=self._to_float(
                        row["成交额"]
                    ),
                )
            )

        result.sort(
            key=lambda item: item.timestamp
        )

        if limit > 0:
            result = result[-limit:]

        return result

    # ==========================================================
    # 估值
    # ==========================================================

    def get_valuation(
        self,
        symbol: str,
    ) -> Valuation:
        """
        获取股票估值数据。

        包括：

            当前价格
            总市值
            流通市值
            PE
            PB

        AkShare 的实时行情接口提供部分估值字段。
        """

        self._ensure_started()

        code = self._normalize_symbol(symbol)

        data = ak.stock_zh_a_spot_em()

        if data is None or data.empty:
            raise RuntimeError(
                "AkShare 未返回估值数据"
            )

        row = data[
            data["代码"].astype(str) == code
        ]

        if row.empty:
            raise ValueError(
                f"未找到股票：{symbol}"
            )

        item = row.iloc[0]

        pe_dynamic = self._get_float(
            item,
            "市盈率-动态",
        )

        return Valuation(
            symbol=symbol,
            price=self._get_float(
                item,
                "最新价",
            ),
            market_cap=self._get_float(
                item,
                "总市值",
            ),
            circulating_market_cap=self._get_float(
                item,
                "流通市值",
            ),
            pe_ttm=pe_dynamic,
            pe_dynamic=pe_dynamic,
            pe_static=None,
            pb=self._get_float(
                item,
                "市净率",
            ),
            ps=None,
        )

    # ==========================================================
    # 财务数据
    # ==========================================================

    def get_financial(
        self,
        symbol: str,
    ) -> Financial:
        """
        获取股票财务数据。

        使用 AkShare 财务分析指标接口。

        这里负责：

            AkShare 原始字段
                    ↓
            Financial 标准模型
        """

        self._ensure_started()

        code = self._normalize_symbol(symbol)

        data = ak.stock_financial_analysis_indicator(
            symbol=code
        )

        if data is None or data.empty:
            raise RuntimeError(
                f"未获取到股票财务数据：{symbol}"
            )

        row = data.iloc[0]

        return self._convert_financial(
            symbol,
            row,
        )

    # ==========================================================
    # Financial 转换
    # ==========================================================

    def _convert_financial(
        self,
        symbol: str,
        row: Any,
    ) -> Financial:
        """
        将 AkShare 财务数据转换成 Financial。

        注意：

        Financial 的具体字段必须与 models.financial
        中的定义保持一致。
        """

        values = {
            "symbol": symbol,
            "report_date": self._get_value(
                row,
                "日期",
            ),
            "roe": self._get_float(
                row,
                "净资产收益率",
            ),
            "gross_margin": self._get_float(
                row,
                "销售毛利率",
            ),
            "net_margin": self._get_float(
                row,
                "销售净利率",
            ),
            "revenue_growth": self._get_float(
                row,
                "主营业务收入增长率",
            ),
            "profit_growth": self._get_float(
                row,
                "净利润增长率",
            ),
        }

        try:
            return Financial(**values)

        except TypeError as exc:
            raise RuntimeError(
                "Financial 模型字段与 AkShareGateway "
                "的财务字段映射不一致。"
                f"当前映射字段：{list(values.keys())}"
            ) from exc

    # ==========================================================
    # 数据转换
    # ==========================================================

    @classmethod
    def _convert_quote(
        cls,
        symbol: str,
        row: Any,
    ) -> Quote:
        """
        将 AkShare 行情转换为 Quote。
        """

        return Quote(
            symbol=symbol,
            name=cls._get_value(
                row,
                "名称",
            ),
            price=cls._get_float(
                row,
                "最新价",
            ),
            change=cls._get_float(
                row,
                "涨跌额",
            ),
            change_percent=cls._get_float(
                row,
                "涨跌幅",
            ),
            open=cls._get_float(
                row,
                "今开",
            ),
            high=cls._get_float(
                row,
                "最高",
            ),
            low=cls._get_float(
                row,
                "最低",
            ),
            volume=cls._get_float(
                row,
                "成交量",
            ),
            amount=cls._get_float(
                row,
                "成交额",
            ),
            turnover_rate=cls._get_float(
                row,
                "换手率",
            ),
            market_cap=cls._get_float(
                row,
                "总市值",
            ),
        )

    # ==========================================================
    # 工具函数
    # ==========================================================

    @staticmethod
    def _normalize_symbol(
        symbol: str,
    ) -> str:
        """
        将统一证券代码转换成 AkShare 代码。

        例如：

            600519.SH → 600519
            000001.SZ → 000001
        """

        value = (
            symbol
            .strip()
            .upper()
        )

        if "." in value:
            value = value.split(
                ".",
                1,
            )[0]

        return value

    @staticmethod
    def _detect_market(
        code: str,
    ) -> str:

        if code.startswith(
            (
                "600",
                "601",
                "603",
                "605",
                "688",
                "689",
            )
        ):
            return "SH"

        if code.startswith(
            (
                "000",
                "001",
                "002",
                "003",
                "300",
                "301",
            )
        ):
            return "SZ"

        if code.startswith(
            (
                "4",
                "8",
            )
        ):
            return "BJ"

        return "UNKNOWN"

    @staticmethod
    def _convert_interval(
        interval: Interval,
    ) -> str:

        value = str(interval).lower()

        if interval == Interval.DAY_1:
            return "daily"

        if "day" in value:
            return "daily"

        if "week" in value:
            return "weekly"

        if "month" in value:
            return "monthly"

        if "60" in value:
            return "60"

        if "30" in value:
            return "30"

        if "15" in value:
            return "15"

        if "5" in value:
            return "5"

        if "1" in value:
            return "1"

        raise ValueError(
            f"AkShare 不支持的 K 线周期：{interval}"
        )

    @staticmethod
    def _get_value(
        row: Any,
        column: str,
        default: Any = None,
    ) -> Any:

        try:
            value = row[column]

            if value is None:
                return default

            return value

        except (
            KeyError,
            TypeError,
            IndexError,
        ):
            return default

    @classmethod
    def _get_float(
        cls,
        row: Any,
        column: str,
        default: Optional[float] = None,
    ) -> Optional[float]:

        value = cls._get_value(
            row,
            column,
            default,
        )

        return cls._to_float(
            value,
            default,
        )

    @staticmethod
    def _to_float(
        value: Any,
        default: Optional[float] = None,
    ) -> Optional[float]:

        if value is None:
            return default

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return default

    @staticmethod
    def _parse_datetime(
        value: Any,
    ) -> datetime:

        if isinstance(
            value,
            datetime,
        ):
            return value

        if hasattr(
            value,
            "to_pydatetime",
        ):
            return value.to_pydatetime()

        return datetime.fromisoformat(
            str(value)
        )

    def _ensure_started(self) -> None:

        if not self._started:

            raise RuntimeError(
                "AkShare 数据源尚未启动，"
                "请先调用 DataManager.start()"
            )