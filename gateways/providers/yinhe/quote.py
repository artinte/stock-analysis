from __future__ import annotations

import datetime
import pandas

from common.constants import Interval, TEN_THOUSAND
from gateways.models.quote import Quote

from utils.stock_mapping import normalize_symbol


class YinheQuote:
    """
    银河证券行情模块。

    负责：

        - 最新价格
        - 涨跌幅
        - 成交量
        - 市值
        - 换手率
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

        self.gateway._ensure_started()

        code = normalize_symbol(symbol)

        try:

            # -----------------------------
            # 最近K线
            # -----------------------------

            klines = self.gateway.kline.fetch_kline(
                symbol=code,
                interval=Interval.DAY_1,
                start_time=(datetime.datetime.now() - pandas.Timedelta(days=30)),
                end_time=datetime.datetime.now(),
                limit=2,
            )

            if not klines:

                return None

            latest = klines[-1]

            previous = klines[-2] if len(klines) > 1 else None

            price = latest.close

            prev_close = previous.close if previous else None

            change = None
            change_percent = None

            if prev_close:

                change = price - prev_close

                change_percent = change / prev_close * 100

            # -----------------------------
            # 股票名称
            # -----------------------------

            stock = self.gateway.fetch_stock(code)

            name = stock.name if stock else None

            # -----------------------------
            # 股本
            # -----------------------------

            total_shares = None
            circulating_shares = None

            equity = self.gateway.info_data.get_equity_structure(
                [code],
                local_path=self.gateway.local_path,
                is_local=False,
            )

            if equity is not None and not equity.empty:

                equity = equity.sort_values("CHANGE_DATE")

                row = equity.iloc[-1]

                if "TOT_SHARE" in equity.columns:

                    total_shares = float(row["TOT_SHARE"]) * TEN_THOUSAND

                if "FLOAT_SHARE" in equity.columns:

                    circulating_shares = float(row["FLOAT_SHARE"]) * TEN_THOUSAND

            # -----------------------------
            # 市值
            # -----------------------------

            market_cap = None

            if total_shares:

                market_cap = total_shares * price

            circulating_market_cap = None

            if circulating_shares:

                circulating_market_cap = circulating_shares * price

            # -----------------------------
            # 换手率
            # -----------------------------

            turnover = None

            if circulating_shares and latest.volume:

                turnover = latest.volume / circulating_shares * 100

            return Quote(
                symbol=code,
                name=name,
                timestamp=latest.timestamp,
                price=price,
                prev_close=prev_close,
                open=latest.open,
                high=latest.high,
                low=latest.low,
                change=change,
                change_percent=change_percent,
                volume=latest.volume,
                amount=latest.amount,
                turnover=turnover,
                total_shares=total_shares,
                circulating_shares=circulating_shares,
                market_cap=market_cap,
                circulating_market_cap=circulating_market_cap,
            )

        except Exception as e:

            print(f"[银河行情] 获取失败 {code}: {e}")

            return None
