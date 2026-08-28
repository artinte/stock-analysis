from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Valuation:
    """
    股票估值数据。

    用于描述股票当前估值水平：

        市值
        PE
        PB
        PS
        PEG
        EV/EBITDA
        股息率

    数据来源可能包括：

        银河证券
        腾讯行情
        Tushare
        AkShare
        第三方估值服务

    上层业务不应该依赖具体数据源。
    """

    # ==========================================================
    # 基础
    # ==========================================================

    symbol: str

    timestamp: Optional[datetime] = None

    report_date: Optional[str] = None

    # ==========================================================
    # 当前价格
    #
    # 与 Quote.price 保持兼容
    # ==========================================================

    price: Optional[float] = None

    # ==========================================================
    # 市值
    # 单位：亿元
    # ==========================================================

    market_cap: Optional[float] = None

    circulating_market_cap: Optional[float] = None

    # 股本
    # 单位：股
    #

    total_shares: Optional[float] = None

    circulating_shares: Optional[float] = None

    # ==========================================================
    # 市盈率 PE
    # ==========================================================

    # 静态PE
    pe_static: Optional[float] = None

    # 动态PE
    pe_dynamic: Optional[float] = None

    # TTM PE
    pe_ttm: Optional[float] = None

    # ==========================================================
    # PB
    # ==========================================================

    pb: Optional[float] = None

    # ==========================================================
    # PS
    # ==========================================================

    ps_static: Optional[float] = None

    ps_ttm: Optional[float] = None

    # ==========================================================
    # PEG
    # ==========================================================

    peg: Optional[float] = None

    # ==========================================================
    # 股息
    # ==========================================================

    dividend_yield: Optional[float] = None

    # ==========================================================
    # 企业价值
    # ==========================================================

    enterprise_value: Optional[float] = None

    ev_ebitda: Optional[float] = None

    # ==========================================================
    # 盈利收益率
    #
    # 商业化分析常用
    # ==========================================================

    earnings_yield: Optional[float] = None

    # ==========================================================
    # 数据来源
    #
    # 方便以后多源融合
    # ==========================================================

    source: Optional[str] = None

    # 数据质量
    #
    # realtime:
    #     实时
    #
    # delayed:
    #     延迟
    #
    # report:
    #     财报计算
    #
    data_type: Optional[str] = None
    
    def display(self) -> None:
        """
        平铺显示股票估值数据。

        显示规则：

            - 所有字段固定显示
            - 空值统一显示 "-"
            - PE / PB / PS / PEG / EV/EBITDA 保留 2 位
            - 百分比保留 2 位
            - 市值保留 2 位
            - 股本使用千分位
            - 时间统一为 YYYY-MM-DD HH:MM:SS
        """

        def fmt(value: object) -> str:
            """格式化普通字段。"""

            if value is None:
                return "-"

            if isinstance(value, str):
                value = value.strip()

                if not value:
                    return "-"

            return str(value)

        def fmt_datetime(
            value: Optional[datetime],
        ) -> str:
            """格式化时间。"""

            if value is None:
                return "-"

            return value.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        def fmt_price(
            value: Optional[float],
        ) -> str:
            """格式化价格。"""

            if value is None:
                return "-"

            return f"{value:,.2f}"

        def fmt_number(
            value: Optional[float],
        ) -> str:
            """格式化普通数值。"""

            if value is None:
                return "-"

            return f"{value:,.2f}"

        def fmt_ratio(
            value: Optional[float],
        ) -> str:
            """格式化估值倍数。"""

            if value is None:
                return "-"

            return f"{value:.2f}"

        def fmt_percent(
            value: Optional[float],
        ) -> str:
            """格式化百分比。"""

            if value is None:
                return "-"

            return f"{value:.2f}%"

        def fmt_market_cap(
            value: Optional[float],
        ) -> str:
            """
            格式化市值。

            Model 内部单位：
                亿元
            """

            if value is None:
                return "-"

            if value >= 10_000:
                return f"{value / 10_000:.2f} 万亿"

            return f"{value:,.2f} 亿"

        def fmt_shares(
            value: Optional[float],
        ) -> str:
            """格式化股本。"""

            if value is None:
                return "-"

            if value >= 100_000_000:
                return f"{value / 100_000_000:.2f} 亿股"

            if value >= 10_000:
                return f"{value / 10_000:.2f} 万股"

            return f"{value:,.0f} 股"

        # ======================================================
        # 基础
        # ======================================================

        print("📊 股票估值")

        print(f"股票代码: {fmt(self.symbol)}")
        print(f"时间: {fmt_datetime(self.timestamp)}")
        print(f"报告期: {fmt(self.report_date)}")
        print(f"数据来源: {fmt(self.source)}")
        print(f"数据类型: {fmt(self.data_type)}")

        # ======================================================
        # 当前价格
        # ======================================================

        print(f"当前价格: {fmt_price(self.price)}")

        # ======================================================
        # 市值
        # ======================================================

        print(f"总市值: {fmt_market_cap(self.market_cap)}")
        print(
            "流通市值: "
            f"{fmt_market_cap(self.circulating_market_cap)}"
        )

        # ======================================================
        # 股本
        # ======================================================

        print(
            f"总股本: "
            f"{fmt_shares(self.total_shares)}"
        )

        print(
            f"流通股本: "
            f"{fmt_shares(self.circulating_shares)}"
        )

        # ======================================================
        # PE
        # ======================================================

        print(f"静态 PE: {fmt_ratio(self.pe_static)}")
        print(f"动态 PE: {fmt_ratio(self.pe_dynamic)}")
        print(f"TTM PE: {fmt_ratio(self.pe_ttm)}")

        # ======================================================
        # PB / PS
        # ======================================================

        print(f"PB: {fmt_ratio(self.pb)}")
        print(f"静态 PS: {fmt_ratio(self.ps_static)}")
        print(f"TTM PS: {fmt_ratio(self.ps_ttm)}")

        # ======================================================
        # PEG
        # ======================================================

        print(f"PEG: {fmt_ratio(self.peg)}")

        # ======================================================
        # 股息
        # ======================================================

        print(
            f"股息率: "
            f"{fmt_percent(self.dividend_yield)}"
        )

        # ======================================================
        # EV
        # ======================================================

        print(
            f"企业价值 EV: "
            f"{fmt_market_cap(self.enterprise_value)}"
        )

        print(
            f"EV/EBITDA: "
            f"{fmt_ratio(self.ev_ebitda)}"
        )

        # ======================================================
        # 盈利收益率
        # ======================================================

        print(
            f"盈利收益率: "
            f"{fmt_percent(self.earnings_yield)}"
        )
