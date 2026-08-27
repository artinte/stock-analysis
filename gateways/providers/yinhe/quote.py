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

    # ==========================================================
    # Public
    # ==========================================================

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

            # ==================================================
            # 最近 K 线
            # ==================================================

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

            # ==================================================
            # 基础价格
            # ==================================================

            price = latest.close

            prev_close = previous.close if previous is not None else None

            open_price = latest.open
            high_price = latest.high
            low_price = latest.low

            # ==================================================
            # 涨跌
            # ==================================================

            change = None
            change_percent = None

            if price is not None and prev_close is not None and prev_close != 0:
                change = price - prev_close

                change_percent = change / prev_close * 100

            # ==================================================
            # 振幅
            # ==================================================

            amplitude = None

            if (
                high_price is not None
                and low_price is not None
                and prev_close is not None
                and prev_close != 0
            ):
                amplitude = (high_price - low_price) / prev_close * 100

            # ==================================================
            # 股票基本信息
            # ==================================================

            stock = self.gateway.fetch_stock(code)

            name = stock.name if stock is not None else None

            # ==================================================
            # 股本
            #
            # 注意：
            # Quote 不保存 total_shares /
            # circulating_shares。
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
            circulating_shares = None

            equity = self.gateway.info_data.get_equity_structure(
                [code],
                local_path=self.gateway.local_path,
                is_local=False,
            )

            if equity is not None and not equity.empty:

                if "CHANGE_DATE" in equity.columns:
                    equity = equity.sort_values("CHANGE_DATE")

                row = equity.iloc[-1]

                # ----------------------------------------------
                # 总股本
                # ----------------------------------------------

                if "TOT_SHARE" in equity.columns:

                    value = row["TOT_SHARE"]

                    if pandas.notna(value):
                        total_shares = float(value) * TEN_THOUSAND

                # ----------------------------------------------
                # 流通股本
                # ----------------------------------------------

                if "FLOAT_SHARE" in equity.columns:

                    value = row["FLOAT_SHARE"]

                    if pandas.notna(value):
                        circulating_shares = float(value) * TEN_THOUSAND

            # ==================================================
            # 市值
            # ==================================================

            market_cap = None

            if total_shares is not None and price is not None:
                market_cap = total_shares * price

            float_market_cap = None

            if circulating_shares is not None and price is not None:
                float_market_cap = circulating_shares * price

            # ==================================================
            # 成交量
            # ==================================================

            volume = latest.volume

            # ==================================================
            # 成交额
            # ==================================================

            amount = latest.amount

            # ==================================================
            # 成交均价
            #
            # 成交均价 = 成交额 / 成交量
            #
            # A 股：
            #
            #     amount -> 元
            #     volume -> 股
            #
            # ==================================================

            average_price = None

            if amount is not None and volume is not None and volume != 0:
                average_price = amount / volume

            # ==================================================
            # 换手率
            #
            # turnover =
            #
            #     volume / 流通股本 × 100%
            # ==================================================

            turnover = None

            if (
                circulating_shares is not None
                and circulating_shares != 0
                and volume is not None
            ):
                turnover = volume / circulating_shares * 100

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

            # ==================================================
            # 涨停 / 跌停
            #
            # 单纯使用 K 线无法知道交易所实际涨跌停价格，
            # 尤其需要考虑：
            #
            #     主板
            #     创业板
            #     科创板
            #     ST
            #     新股
            #
            # 因此如果数据源没有直接提供，
            # 不在这里猜测。
            # ==================================================

            limit_up = None
            limit_down = None

            # ==================================================
            # 交易状态
            # ==================================================

            status = None

            # ==================================================
            # 返回统一 Quote
            # ==================================================

            return Quote(
                symbol=code,
                name=name,
                timestamp=latest.timestamp,
                source="yinhe",
                currency="CNY",
                # ----------------------------------------------
                # 价格
                # ----------------------------------------------
                last_price=price,
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
                turnover_rate=turnover,
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
