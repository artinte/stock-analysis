from __future__ import annotations

import datetime

import pandas

from common.constants import Interval, TEN_THOUSAND
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

    def fetch_quote(
        self,
        symbol: str,
    ) -> Quote | None:
        """
        获取股票最新行情。

        参数：
            symbol:
                股票代码，例如：

                    600519
                    600519.SH

        返回：
            Quote | None
        """

        self.gateway._ensure_started()

        code = normalize_symbol(symbol)

        try:
            now = datetime.datetime.now()

            # 最近 K 线
            klines = self.gateway.kline.fetch_kline(
                symbol=code,
                interval=Interval.DAY_1,
                start_time=(now - pandas.Timedelta(days=30)),
                end_time=now,
                limit=30,
            )

            if not klines:
                return None

            latest = klines[-1]

            previous = klines[-2] if len(klines) > 1 else None

            last_price = latest.close
            prev_close = previous.close if previous is not None else None

            open_price = latest.open
            high_price = latest.high
            low_price = latest.low

            change = None
            change_percent = None

            if last_price is not None and prev_close is not None and prev_close != 0:
                change = last_price - prev_close

                change_percent = change / prev_close * 100

            amplitude = None

            if (
                high_price is not None
                and low_price is not None
                and prev_close is not None
                and prev_close != 0
            ):
                amplitude = (high_price - low_price) / prev_close * 100

            stock_name = self.gateway.fetch_stock_name(symbol)

            # ==================================================
            # 股本
            #
            # 注意：
            # Quote 不保存 total_shares / float_shares。
            #
            # 这里只是为了计算：
            #
            #     市值
            #     流通市值
            #     换手率
            #
            # 计算完成后不进入 Quote。
            # ==================================================
            total_shares = None
            float_shares = None

            equity = self.gateway.info_data.get_equity_structure(
                [code],
                local_path=self.gateway.local_path,
                is_local=False,
            )

            if equity is not None and not equity.empty:

                if "CHANGE_DATE" in equity.columns:
                    equity = equity.sort_values("CHANGE_DATE")

                row = equity.iloc[-1]

                # 总股本
                if "TOT_SHARE" in equity.columns:

                    value = row["TOT_SHARE"]

                    if pandas.notna(value):
                        total_shares = float(value) * TEN_THOUSAND

                # 流通股本
                if "FLOAT_SHARE" in equity.columns:

                    value = row["FLOAT_SHARE"]

                    if pandas.notna(value):
                        float_shares = float(value) * TEN_THOUSAND

            # ==================================================
            # 市值
            # ==================================================

            market_cap = None

            if total_shares is not None and last_price is not None:
                market_cap = total_shares * last_price

            float_market_cap = None

            if float_shares is not None and last_price is not None:
                float_market_cap = float_shares * last_price

            # 成交量
            volume = latest.volume

            # 成交额
            amount = latest.amount

            # 成交均价 = 成交额 / 成交量
            average_price = None

            if amount is not None and volume is not None and volume != 0:
                average_price = amount / volume

            # 换手率 = volume / 流通股本 × 100%
            turnover = None

            if float_shares is not None and float_shares != 0 and volume is not None:
                turnover = volume / float_shares * 100

            # ==================================================
            # 量比
            #
            # 当前 K 线只有单日数据时，
            # 不能可靠计算标准实时量比。
            #
            # 因此这里暂时使用 None。
            #
            # 后续如果银河数据源提供量比字段，
            # 直接映射即可。
            # ==================================================
            volume_ratio = None
            if len(klines) > 1:
                volumes = [
                    k.volume
                    for k in klines[:-1][-5:]
                    if k.volume is not None and k.volume > 0
                ]

                today_volume = latest.volume

                if today_volume is not None and today_volume > 0 and volumes:
                    average_volume = sum(volumes) / len(volumes)

                    if average_volume > 0:
                        volume_ratio = today_volume / average_volume

            # 涨停 / 跌停
            limit_percent = self._get_limit_percent(code)
            limit_up = None
            limit_down = None

            if prev_close is not None and prev_close > 0 and limit_percent is not None:
                limit_up = round(
                    prev_close * (1 + limit_percent),
                    2,
                )

                limit_down = round(
                    prev_close * (1 - limit_percent),
                    2,
                )

            # 交易状态
            status = self._get_status(
                last_price=last_price,
                volume=volume,
                limit_up=limit_up,
                limit_down=limit_down,
            )

            return Quote(
                symbol=code,
                name=stock_name,
                timestamp=latest.timestamp,
                source="yinhe",
                currency="CNY",
                # ----------------------------------------------
                # 价格
                # ----------------------------------------------
                last_price=last_price,
                previous_close=prev_close,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                # ----------------------------------------------
                # 涨跌
                # ----------------------------------------------
                change=change,
                change_percent=change_percent,
                amplitude=amplitude,
                # ----------------------------------------------
                # 成交
                # ----------------------------------------------
                volume=volume,
                amount=amount,
                average_price=average_price,
                turnover=turnover,
                volume_ratio=volume_ratio,
                # ----------------------------------------------
                # 市值
                # ----------------------------------------------
                market_cap=market_cap,
                float_market_cap=float_market_cap,
                # ----------------------------------------------
                # 涨跌停
                # ----------------------------------------------
                limit_up=limit_up,
                limit_down=limit_down,
                # ----------------------------------------------
                # 状态
                # ----------------------------------------------
                status=status,
            )

        except Exception as e:

            print(f"[银河行情] 获取失败 {code}: {e}")

            return None

    @staticmethod
    def _get_limit_percent(
        symbol: str,
    ) -> float:
        """
        根据股票代码判断涨跌停幅度。

        返回：
            0.05 -> 5%
            0.10 -> 10%
            0.20 -> 20%
            0.30 -> 30%
        """

        code = symbol.split(".")[0]

        # 北交所
        if code.startswith(
            (
                "8",
                "4",
            )
        ):
            return 0.30

        # 科创板
        if code.startswith("688"):
            return 0.20

        # 创业板
        if code.startswith(
            (
                "300",
                "301",
            )
        ):
            return 0.20

        # 主板
        return 0.10

    @staticmethod
    def _get_status(
        *,
        last_price: float | None,
        volume: float | None,
        limit_up: float | None,
        limit_down: float | None,
    ) -> str:

        if last_price is None:
            return "unknown"

        if limit_up is not None and last_price >= limit_up:
            return "limit_up"

        if limit_down is not None and last_price <= limit_down:
            return "limit_down"

        if volume is not None and volume == 0:
            return "suspended"

        return "trading"
