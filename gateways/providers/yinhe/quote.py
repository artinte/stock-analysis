from __future__ import annotations

import datetime
from typing import Optional

import pandas

from common.constants import Interval, TEN_THOUSAND
from common.enums.quote_level import QuoteLevel
from core.models.quote import Quote

from utils.stock_mapping import normalize_symbol


class YinheQuote:
    """
    银河证券行情模块。

    负责获取并统一转换股票最新行情：

        - 最新价格
        - 昨收
        - 开盘 / 最高 / 最低
        - 涨跌 / 涨跌幅 / 振幅
        - 成交量 / 成交额
        - 成交均价
        - 换手率
        - 量比
        - 总市值 / 流通市值
        - 涨停 / 跌停
        - 交易状态

    最终统一转换为 Quote。
    """

    def __init__(
        self,
        gateway,
    ):
        self.gateway = gateway

    # =========================================================
    # 单只股票
    # =========================================================

    def fetch_quote(
        self,
        symbol: str,
        quote_level: Optional[QuoteLevel] = None,
    ) -> Quote | None:
        """
        获取单只股票最新行情。

        fetch_quote 是 fetch_quotes 的单只特例。

        参数：
            symbol:
                股票代码，例如：

                    600519
                    600519.SH

            quote_level:
                行情级别。

        返回：
            Quote | None
        """

        quotes = self.fetch_quotes(
            symbols=[symbol],
            quote_level=quote_level,
        )

        if not quotes:
            return None

        return quotes[0]

    # =========================================================
    # 多只股票
    # =========================================================

    def fetch_quotes(
        self,
        symbols: list[str],
        quote_level: Optional[QuoteLevel] = None,
    ) -> list[Quote]:
        """
        批量获取股票最新行情。

        参数：
            symbols:
                股票代码列表，例如：

                    [
                        "600519",
                        "000001",
                        "300750",
                    ]

                也支持：

                    [
                        "600519.SH",
                        "000001.SZ",
                    ]

            quote_level:
                行情级别。

        返回：
            list[Quote]

        说明：
            1. 统一进行股票代码标准化
            2. 获取最近 K 线
            3. 获取股本
            4. 统一计算行情指标
            5. 最终构造 Quote
        """

        self.gateway._ensure_started()

        if not symbols:
            return []

        # -----------------------------------------------------
        # 1. 标准化股票代码
        # -----------------------------------------------------

        normalized_symbols = []

        for symbol in symbols:

            if not symbol:
                continue

            symbol = normalize_symbol(symbol)

            if symbol not in normalized_symbols:
                normalized_symbols.append(symbol)

        if not normalized_symbols:
            return []

        result = []

        # -----------------------------------------------------
        # 2. 批量获取
        # -----------------------------------------------------

        for symbol in normalized_symbols:

            try:

                # -------------------------------------------------
                # 最近 K 线
                #
                # 当前 Yinhe Kline 模块如果只有 fetch_kline，
                # 这里先逐只获取。
                #
                # 后续如果有 fetch_klines()，
                # 可以直接改成真正的批量请求。
                # -------------------------------------------------

                now = datetime.datetime.now()

                klines = self.gateway.kline.fetch_kline(
                    symbol=symbol,
                    interval=Interval.DAY_1,
                    start_time=(
                        now - pandas.Timedelta(days=30)
                    ),
                    end_time=now,
                    limit=30,
                )

                if not klines:
                    print(
                        f"[银河行情] 无 K 线数据：{symbol}"
                    )
                    continue

                # -------------------------------------------------
                # 2. 股本
                # -------------------------------------------------

                equity = (
                    self.gateway.info_data.get_equity_structure(
                        [symbol],
                        local_path=self.gateway.local_path,
                        is_local=False,
                    )
                )

                # -------------------------------------------------
                # 3. 构造 Quote
                # -------------------------------------------------

                quote = self._build_quote(
                    symbol=symbol,
                    klines=klines,
                    equity=equity,
                    quote_level=quote_level,
                )

                if quote is not None:
                    result.append(quote)

            except Exception as e:

                print(
                    f"[银河行情] 获取失败 {symbol}: {e}"
                )

        return result

    # =========================================================
    # Quote 构造
    # =========================================================

    def _build_quote(
        self,
        symbol: str,
        klines,
        equity,
        quote_level: Optional[QuoteLevel] = None,
    ) -> Quote | None:
        """
        根据 K 线和股本数据构造 Quote。

        这里集中处理所有行情计算。

        fetch_quote()
        fetch_quotes()

        都不应该重复这些计算。
        """

        if not klines:
            return None

        # -----------------------------------------------------
        # 最新 / 前一交易日
        # -----------------------------------------------------

        latest = klines[-1]

        previous = (
            klines[-2]
            if len(klines) > 1
            else None
        )

        # -----------------------------------------------------
        # 基础行情
        # -----------------------------------------------------

        last_price = latest.close

        prev_close = (
            previous.close
            if previous is not None
            else None
        )

        open_price = latest.open
        high_price = latest.high
        low_price = latest.low

        # -----------------------------------------------------
        # 涨跌
        # -----------------------------------------------------

        change = None
        change_percent = None

        if (
            last_price is not None
            and prev_close is not None
            and prev_close != 0
        ):

            change = last_price - prev_close

            change_percent = (
                change / prev_close * 100
            )

        # -----------------------------------------------------
        # 振幅
        # -----------------------------------------------------

        amplitude = None

        if (
            high_price is not None
            and low_price is not None
            and prev_close is not None
            and prev_close != 0
        ):

            amplitude = (
                (high_price - low_price)
                / prev_close
                * 100
            )

        # -----------------------------------------------------
        # 股票名称
        # -----------------------------------------------------

        stock_name = self.gateway.fetch_stock_name(
            symbol
        )

        # =====================================================
        # 股本
        # =====================================================

        total_shares = None
        float_shares = None

        if equity is not None and not equity.empty:

            if "CHANGE_DATE" in equity.columns:

                equity = equity.sort_values(
                    "CHANGE_DATE"
                )

            row = equity.iloc[-1]

            # -------------------------------------------------
            # 总股本
            #
            # TOT_SHARE：
            # 单位通常为万股
            # -------------------------------------------------

            if "TOT_SHARE" in equity.columns:

                value = row["TOT_SHARE"]

                if pandas.notna(value):

                    total_shares = (
                        float(value)
                        * TEN_THOUSAND
                    )

            # -------------------------------------------------
            # 流通股本
            # -------------------------------------------------

            if "FLOAT_SHARE" in equity.columns:

                value = row["FLOAT_SHARE"]

                if pandas.notna(value):

                    float_shares = (
                        float(value)
                        * TEN_THOUSAND
                    )

        # =====================================================
        # 市值
        # =====================================================

        market_cap = None

        if (
            total_shares is not None
            and last_price is not None
        ):

            market_cap = (
                total_shares
                * last_price
            )

        float_market_cap = None

        if (
            float_shares is not None
            and last_price is not None
        ):

            float_market_cap = (
                float_shares
                * last_price
            )

        # =====================================================
        # 成交量 / 成交额
        # =====================================================

        volume = latest.volume
        amount = latest.amount

        # -----------------------------------------------------
        # 成交均价
        # -----------------------------------------------------

        average_price = None

        if (
            amount is not None
            and volume is not None
            and volume != 0
        ):

            average_price = (
                amount / volume
            )

        # -----------------------------------------------------
        # 换手率
        # -----------------------------------------------------

        turnover = None

        if (
            float_shares is not None
            and float_shares != 0
            and volume is not None
        ):

            turnover = (
                volume
                / float_shares
                * 100
            )

        # =====================================================
        # 量比
        # =====================================================

        volume_ratio = None

        if len(klines) > 1:

            volumes = [
                k.volume
                for k in klines[:-1][-5:]
                if (
                    k.volume is not None
                    and k.volume > 0
                )
            ]

            today_volume = latest.volume

            if (
                today_volume is not None
                and today_volume > 0
                and volumes
            ):

                average_volume = (
                    sum(volumes)
                    / len(volumes)
                )

                if average_volume > 0:

                    volume_ratio = (
                        today_volume
                        / average_volume
                    )

        # =====================================================
        # 涨跌停
        # =====================================================

        limit_percent = (
            self._get_limit_percent(symbol)
        )

        limit_up = None
        limit_down = None

        if (
            prev_close is not None
            and prev_close > 0
            and limit_percent is not None
        ):

            limit_up = round(
                prev_close
                * (1 + limit_percent),
                2,
            )

            limit_down = round(
                prev_close
                * (1 - limit_percent),
                2,
            )

        # =====================================================
        # 交易状态
        # =====================================================

        status = self._get_status(
            last_price=last_price,
            volume=volume,
            limit_up=limit_up,
            limit_down=limit_down,
        )

        # =====================================================
        # Quote
        # =====================================================

        return Quote(
            symbol=symbol,
            name=stock_name,
            timestamp=latest.timestamp,
            source="yinhe",
            currency="CNY",

            # -------------------------
            # 价格
            # -------------------------

            last_price=last_price,
            previous_close=prev_close,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,

            # -------------------------
            # 涨跌
            # -------------------------

            change=change,
            change_percent=change_percent,
            amplitude=amplitude,

            # -------------------------
            # 成交
            # -------------------------

            volume=volume,
            amount=amount,
            average_price=average_price,

            # -------------------------
            # 交易指标
            # -------------------------

            turnover=turnover,
            volume_ratio=volume_ratio,

            # -------------------------
            # 市值
            # -------------------------

            market_cap=market_cap,
            float_market_cap=float_market_cap,

            # -------------------------
            # 涨跌停
            # -------------------------

            limit_up=limit_up,
            limit_down=limit_down,

            # -------------------------
            # 状态
            # -------------------------

            status=status,
        )

    # =========================================================
    # 涨跌停比例
    # =========================================================

    @staticmethod
    def _get_limit_percent(
        symbol: str,
    ) -> float:
        """
        获取股票涨跌停比例。

        这里保留你原来的实现。
        """

        symbol = symbol.upper()

        # -----------------------------------------------------
        # 科创板 / 创业板
        # -----------------------------------------------------

        if (
            symbol.startswith("688")
            or symbol.startswith("300")
            or symbol.startswith("301")
        ):
            return 0.20

        # -----------------------------------------------------
        # 北交所
        # -----------------------------------------------------

        if symbol.startswith("8"):

            return 0.30

        if symbol.startswith("4"):

            return 0.30

        # -----------------------------------------------------
        # ST
        #
        # 注意：
        # 这里只能根据代码判断普通涨跌停，
        # ST 应该进一步结合股票名称判断。
        # -----------------------------------------------------

        return 0.10

    # =========================================================
    # 交易状态
    # =========================================================

    @staticmethod
    def _get_status(
        last_price,
        volume,
        limit_up,
        limit_down,
    ):
        """
        判断股票交易状态。
        """

        # -----------------------------------------------------
        # 没有价格
        # -----------------------------------------------------

        if last_price is None:
            return "unknown"

        # -----------------------------------------------------
        # 停牌
        # -----------------------------------------------------

        if volume is not None and volume == 0:
            return "suspended"

        # -----------------------------------------------------
        # 涨停
        # -----------------------------------------------------

        if (
            limit_up is not None
            and last_price >= limit_up
        ):
            return "limit_up"

        # -----------------------------------------------------
        # 跌停
        # -----------------------------------------------------

        if (
            limit_down is not None
            and last_price <= limit_down
        ):
            return "limit_down"

        # -----------------------------------------------------
        # 正常交易
        # -----------------------------------------------------

        return "trading"

