from __future__ import annotations

import datetime
from typing import Optional

import pandas

from common.constants import TEN_THOUSAND, Interval
from core.models.valuation import Valuation

from utils.stock_mapping import normalize_symbol


class YinheValuation:
    """
    银河证券估值模块。

    负责：

        - 市盈率 PE
        - 市值计算
        - 估值模型转换
    """

    def __init__(
        self,
        gateway,
    ):

        self.gateway = gateway

    def fetch_valuation(
        self,
        symbol: str,
    ) -> Valuation:

        self.gateway._ensure_started()

        formatted_symbol = normalize_symbol(symbol)

        print(f"[{formatted_symbol}] " f"正在获取估值数据...")

        # ------------------------------------------------------
        # 获取最近 K 线
        # ------------------------------------------------------

        klines = self.gateway.fetch_kline(
            symbol=formatted_symbol,
            interval=Interval.DAY_1,
            start_time=(datetime.datetime.now() - pandas.Timedelta(days=30)),
            end_time=datetime.datetime.now(),
            limit=30,
        )

        if not klines:

            return Valuation(
                symbol=formatted_symbol,
                timestamp=datetime.datetime.now(),
            )

        current_price = klines[-1].close

        # ------------------------------------------------------
        # 获取总市值
        # ------------------------------------------------------

        total_shares = None
        circulating_shares = None
        try:
            equity_structure = self.gateway.info_data.get_equity_structure(
                [formatted_symbol],
                local_path=self.gateway.local_path,
                is_local=False,
            )

            if equity_structure is not None and not equity_structure.empty:
                equity_structure = equity_structure.sort_values("CHANGE_DATE")
                latest_row = equity_structure.iloc[-1]

                if "TOT_SHARE" in equity_structure.columns:
                    # 原始数据是万为单位
                    total_shares = float(latest_row["TOT_SHARE"]) * TEN_THOUSAND

                # 如果存在流通股字段，根据实际字段读取。
                if "FLOAT_SHARE" in equity_structure.columns:
                    circulating_shares = float(latest_row["FLOAT_SHARE"]) * TEN_THOUSAND
                elif "CIRC_SHARE" in equity_structure.columns:
                    circulating_shares = float(latest_row["CIRC_SHARE"]) * TEN_THOUSAND
        except Exception as e:
            print(f"[银河网关] 获取股本失败 " f"{formatted_symbol}: {e}")

        # 总市值计算：
        # 总市值 = 总股本 × 当前股价
        # 单位：亿元（取决于 total_shares 和 current_price 的单位）
        market_cap = None

        # 流通市值计算：
        # 流通市值 = 流通股本 × 当前股价
        # 单位：亿元（取决于 circulating_shares 和 current_price 的单位）
        circulating_market_cap = None

        if total_shares is not None:
            market_cap = total_shares * current_price

        if circulating_shares is not None:
            circulating_market_cap = circulating_shares * current_price

        # ------------------------------------------------------
        # 计算 PE
        # ------------------------------------------------------

        pe_ttm = self._calculate_pe(
            formatted_symbol,
            "TTM",
            market_cap,
        )

        pe_static = self._calculate_pe(
            formatted_symbol,
            "STATIC",
            market_cap,
        )

        pe_dynamic = self._calculate_pe(
            formatted_symbol,
            "DYNAMIC",
            market_cap,
        )

        # ------------------------------------------------------
        # 统一成 Valuation
        # ------------------------------------------------------

        return Valuation(
            symbol=formatted_symbol,
            timestamp=datetime.datetime.now(),
            price=current_price,
            market_cap=market_cap,
            circulating_market_cap=circulating_market_cap,
            pe_static=pe_static,
            pe_dynamic=pe_dynamic,
            pe_ttm=pe_ttm,
        )

    def _calculate_pe(
        self,
        symbol: str,
        pe_type: str,
        market_cap: Optional[float] = None,
    ) -> float:
        """
        计算 PE。

        支持：

            TTM
            STATIC
            DYNAMIC
        """

        formatted_symbol = normalize_symbol(symbol)

        try:

            print(f"[{formatted_symbol}] " f"正在计算 PE({pe_type})...")

            # --------------------------------------------------
            # 1. 获取利润表
            # --------------------------------------------------

            financials_dict = self.gateway.info_data.get_income(
                code_list=[formatted_symbol],
                local_path=self.gateway.local_path,
                is_local=False,
                begin_date="20220101",
                end_date=self.gateway.calendar[-1],
            )

            if financials_dict is None:
                return float("nan")

            df = financials_dict.get(formatted_symbol)

            if df is None or df.empty:

                print(f"[{formatted_symbol}] " f"未能获取有效利润表")

                return float("nan")

            profit_field = "NET_PRO_EXCL_MIN_INT_INC"

            period_field = "REPORTING_PERIOD"

            profit_data = df.set_index(df[period_field].astype(str))[
                profit_field
            ].to_dict()

            # --------------------------------------------------
            # 2. 获取总股本
            # --------------------------------------------------

            equity_structure = self.gateway.info_data.get_equity_structure(
                [formatted_symbol],
                local_path=self.gateway.local_path,
                is_local=False,
            )

            total_share = 0

            if equity_structure is not None and not equity_structure.empty:

                equity_structure = equity_structure.sort_values("CHANGE_DATE")

                latest_row = equity_structure.iloc[-1]

                total_share = float(latest_row["TOT_SHARE"])

            # --------------------------------------------------
            # 3. 如果没有传入市值，则自己计算
            # --------------------------------------------------

            if market_cap is None:

                klines = self.fetch_kline(
                    symbol=formatted_symbol,
                    interval=Interval.DAY_1,
                    start_time=(datetime.datetime.now() - pandas.Timedelta(days=30)),
                    end_time=datetime.datetime.now(),
                    limit=30,
                )

                if not klines:
                    return float("nan")

                current_price = klines[-1].close

                market_cap = total_share * current_price / 10000

            # --------------------------------------------------
            # 4. 找到最新可用财报
            # --------------------------------------------------

            now = datetime.datetime.now()

            q_map = {
                1: "0331",
                2: "0630",
                3: "0930",
                4: "1231",
            }

            target_period = None
            q_num = 0

            for i in range(1, 7):

                dt = now - datetime.timedelta(days=i * 90)

                for q in [4, 3, 2, 1]:

                    period_key = f"{dt.year}" f"{q_map[q]}"

                    if period_key in profit_data and not pandas.isna(
                        profit_data[period_key]
                    ):

                        target_period = period_key

                        q_num = q

                        break

                if target_period:
                    break

            if not target_period:
                return float("nan")

            # --------------------------------------------------
            # 5. 计算
            # --------------------------------------------------

            current_report_year = int(target_period[:4])

            base_year = current_report_year - 1

            curr_q_cum = profit_data.get(
                target_period,
                0,
            )

            last_full_year = profit_data.get(
                f"{base_year}1231",
                0,
            )

            prev_q_cum = profit_data.get(
                f"{base_year}" f"{q_map[q_num]}",
                0,
            )

            requested_type = pe_type.upper()

            # --------------------------------------------------
            # TTM PE
            # --------------------------------------------------

            if requested_type == "TTM":

                profit_ttm = curr_q_cum + (last_full_year - prev_q_cum)

                if profit_ttm > 0:

                    return round(
                        market_cap / profit_ttm,
                        2,
                    )

            # --------------------------------------------------
            # 静态 PE
            # --------------------------------------------------

            elif requested_type in (
                "STATIC",
                "LYR",
            ):

                if last_full_year > 0:

                    return round(
                        market_cap / last_full_year,
                        2,
                    )

            # --------------------------------------------------
            # 动态 PE
            # --------------------------------------------------

            elif requested_type in (
                "DYNAMIC",
                "FORWARD",
            ):

                if q_num > 0 and curr_q_cum > 0:

                    annual_profit = curr_q_cum / q_num * 4

                    return round(
                        market_cap / annual_profit,
                        2,
                    )

            return float("nan")

        except Exception as e:

            print(f"[{formatted_symbol}] " f"计算 PE({pe_type}) 出错: {e}")

            return float("nan")
