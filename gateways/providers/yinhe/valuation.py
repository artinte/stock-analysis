from __future__ import annotations

import datetime
from typing import Optional

import pandas

from common.constants import Interval, TEN_THOUSAND
from core.models.valuation import Valuation

from utils.stock_mapping import normalize_symbol


class YinheValuation:
    """
    银河证券估值模块。

    负责：

        - 当前价格
        - 总股本 / 流通股本
        - 总市值 / 流通市值
        - 静态 PE
        - 动态 PE
        - TTM PE
        - PB
        - 静态 PS
        - TTM PS
        - PEG
        - 股息率
        - 企业价值 EV
        - EV / EBITDA
        - 盈利收益率

    注意：

        Valuation 只是数据模型。

        所有数据获取和计算逻辑都在本模块完成。

        PE 的计算逻辑保持原有实现，不在这里修改。
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
        """
        获取完整估值数据。
        """

        self.gateway._ensure_started()

        formatted_symbol = normalize_symbol(symbol)

        print(f"[{formatted_symbol}] " f"正在获取估值数据...")

        try:

            # --------------------------------------------------
            # 1. 获取最近 K 线
            # --------------------------------------------------

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
                    source=self.gateway.display_name,
                    data_type="realtime",
                )

            current_price = klines[-1].close

            # --------------------------------------------------
            # 2. 获取股本
            # --------------------------------------------------

            total_shares = None
            circulating_shares = None
            equity_report_date = None

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
                        # 银河原始数据：万股
                        total_shares = float(latest_row["TOT_SHARE"]) * TEN_THOUSAND

                    # ------------------------------------------
                    # 流通股本
                    # ------------------------------------------

                    if "FLOAT_SHARE" in equity_structure.columns:

                        value = latest_row["FLOAT_SHARE"]

                        if pandas.notna(value):

                            circulating_shares = float(value) * TEN_THOUSAND

                    elif "CIRC_SHARE" in equity_structure.columns:

                        value = latest_row["CIRC_SHARE"]

                        if pandas.notna(value):

                            circulating_shares = float(value) * TEN_THOUSAND

                    # ------------------------------------------
                    # 股本变更日期
                    # ------------------------------------------

                    if "CHANGE_DATE" in equity_structure.columns:

                        value = latest_row["CHANGE_DATE"]

                        if pandas.notna(value):

                            equity_report_date = str(value)

            except Exception as e:
                print(f"[银河估值] 获取股本失败 " f"{formatted_symbol}: {e}")

            # --------------------------------------------------
            # 3. 总市值
            # --------------------------------------------------

            market_cap = None

            if total_shares is not None:
                market_cap = total_shares * current_price

            # --------------------------------------------------
            # 4. 流通市值
            # --------------------------------------------------

            circulating_market_cap = None

            if circulating_shares is not None:
                circulating_market_cap = circulating_shares * current_price

            # 5. PE
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

            # TODO: 获取财务数据
            # financial = self.gateway.fetch_financial(symbol)
            financial = {
                "net_assets": None,
                "revenue": None,
                "revenue_ttm": None,
                "profit_growth": None,
                "cash": None,
                "debt": None,
                "ebitda": None,
                "dividend": None,
                "report_date": None,
            }

            # --------------------------------------------------
            # 7. PB
            # --------------------------------------------------

            pb = self._calculate_pb(
                market_cap=market_cap,
                net_assets=financial.get("net_assets"),
            )

            # --------------------------------------------------
            # 8. PS
            # --------------------------------------------------

            ps_static = self._calculate_ps(
                market_cap=market_cap,
                revenue=financial.get("revenue"),
            )

            ps_ttm = self._calculate_ps(
                market_cap=market_cap,
                revenue=financial.get("revenue_ttm"),
            )

            # --------------------------------------------------
            # 9. PEG
            # --------------------------------------------------

            peg = self._calculate_peg(
                pe=pe_ttm,
                growth=financial.get("profit_growth"),
            )

            # --------------------------------------------------
            # 10. 股息率
            # --------------------------------------------------

            dividend_yield = self._calculate_dividend_yield(
                price=current_price,
                dividend=financial.get("dividend"),
            )

            # --------------------------------------------------
            # 11. 企业价值 EV
            # --------------------------------------------------

            enterprise_value = self._calculate_enterprise_value(
                market_cap=market_cap,
                debt=financial.get("debt"),
                cash=financial.get("cash"),
            )

            # --------------------------------------------------
            # 12. EV / EBITDA
            # --------------------------------------------------

            ev_ebitda = self._calculate_ev_ebitda(
                enterprise_value=enterprise_value,
                ebitda=financial.get("ebitda"),
            )

            # --------------------------------------------------
            # 13. 盈利收益率
            # --------------------------------------------------

            earnings_yield = self._calculate_earnings_yield(
                pe_ttm=pe_ttm,
                pe_static=pe_static,
            )

            # --------------------------------------------------
            # 14. 报告期
            # --------------------------------------------------

            report_date = financial.get("report_date") or equity_report_date

            # --------------------------------------------------
            # 15. 返回 Valuation
            # --------------------------------------------------
            print("返回数据")
            return Valuation(
                symbol=formatted_symbol,
                timestamp=datetime.datetime.now(),
                report_date=report_date,
                # 当前价格
                price=current_price,
                # 市值
                market_cap=market_cap,
                circulating_market_cap=(circulating_market_cap),
                # 股本
                total_shares=total_shares,
                circulating_shares=circulating_shares,
                # PE
                pe_static=pe_static,
                pe_dynamic=pe_dynamic,
                pe_ttm=pe_ttm,
                # PB
                pb=pb,
                # PS
                ps_static=ps_static,
                ps_ttm=ps_ttm,
                # PEG
                peg=peg,
                # 股息率
                dividend_yield=dividend_yield,
                # EV
                enterprise_value=enterprise_value,
                ev_ebitda=ev_ebitda,
                # 盈利收益率
                earnings_yield=earnings_yield,
                # 来源
                source=self.gateway.display_name,
                data_type="report",
            )

        except Exception as e:
            print(f"[银河估值] 获取失败 " f"{formatted_symbol}: {e}")
            return None

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

    # ==========================================================
    # PB
    # ==========================================================

    @staticmethod
    def _calculate_pb(
        market_cap: Optional[float],
        net_assets: Optional[float],
    ) -> Optional[float]:
        """
        PB = 市值 / 净资产。
        """

        if market_cap is None:
            return None

        if net_assets is None:
            return None

        if net_assets <= 0:
            return None

        return round(
            market_cap / net_assets,
            2,
        )

    # ==========================================================
    # PS
    # ==========================================================

    @staticmethod
    def _calculate_ps(
        market_cap: Optional[float],
        revenue: Optional[float],
    ) -> Optional[float]:
        """
        PS = 市值 / 营业收入。
        """

        if market_cap is None:
            return None

        if revenue is None:
            return None

        if revenue <= 0:
            return None

        return round(
            market_cap / revenue,
            2,
        )

    # ==========================================================
    # PEG
    # ==========================================================

    @staticmethod
    def _calculate_peg(
        pe: Optional[float],
        growth: Optional[float],
    ) -> Optional[float]:
        """
        PEG = PE / 净利润增长率。

        growth 使用百分比数值。

        例如：

            PE = 20
            增长率 = 10%

            PEG = 20 / 10 = 2
        """

        if pe is None:
            return None

        if pandas.isna(pe):
            return None

        if growth is None:
            return None

        if growth <= 0:
            return None

        return round(
            pe / growth,
            2,
        )

    # ==========================================================
    # Dividend Yield
    # ==========================================================

    @staticmethod
    def _calculate_dividend_yield(
        price: Optional[float],
        dividend: Optional[float],
    ) -> Optional[float]:
        """
        股息率 = 每股股息 / 当前价格 × 100%。

        dividend：

            每股股息，单位：元。
        """

        if price is None:
            return None

        if price <= 0:
            return None

        if dividend is None:
            return None

        return round(
            dividend / price * 100,
            2,
        )

    # ==========================================================
    # Enterprise Value
    # ==========================================================

    @staticmethod
    def _calculate_enterprise_value(
        market_cap: Optional[float],
        debt: Optional[float],
        cash: Optional[float],
    ) -> Optional[float]:
        """
        EV = 市值 + 有息债务 - 现金。

        单位：

            亿元
        """

        if market_cap is None:
            return None

        if debt is None:
            return None

        if cash is None:
            return None

        return round(
            market_cap + debt - cash,
            2,
        )

    # ==========================================================
    # EV / EBITDA
    # ==========================================================

    @staticmethod
    def _calculate_ev_ebitda(
        enterprise_value: Optional[float],
        ebitda: Optional[float],
    ) -> Optional[float]:
        """
        EV / EBITDA。
        """

        if enterprise_value is None:
            return None

        if ebitda is None:
            return None

        if ebitda <= 0:
            return None

        return round(
            enterprise_value / ebitda,
            2,
        )

    # ==========================================================
    # Earnings Yield
    # ==========================================================

    @staticmethod
    def _calculate_earnings_yield(
        pe_ttm: Optional[float],
        pe_static: Optional[float],
    ) -> Optional[float]:
        """
        盈利收益率 = 1 / PE × 100%。

        优先使用 TTM PE。
        """

        pe = pe_ttm if pe_ttm is not None and not pandas.isna(pe_ttm) else pe_static

        if pe is None:
            return None

        if pandas.isna(pe):
            return None

        if pe <= 0:
            return None

        return round(
            1 / pe * 100,
            2,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _find_latest_report(
        df: pandas.DataFrame,
    ) -> tuple[
        Optional[str],
        int,
    ]:
        """
        从利润表中找到最新报告期。

        返回：

            report_date
            quarter
        """

        if df is None or df.empty:
            return None, 0

        period_field = "REPORTING_PERIOD"

        if period_field not in df.columns:
            return None, 0

        quarter_map = {
            "0331": 1,
            "0630": 2,
            "0930": 3,
            "1231": 4,
        }

        periods = df[period_field].astype(str).tolist()

        valid_periods = []

        for period in periods:

            if len(period) != 8:
                continue

            quarter = quarter_map.get(period[4:])

            if quarter is None:
                continue

            valid_periods.append((period, quarter))

        if not valid_periods:
            return None, 0

        valid_periods.sort(key=lambda x: x[0])

        return valid_periods[-1]

    @staticmethod
    def _quarter_code(
        quarter: int,
    ) -> str:
        """
        季度 -> 报告期。
        """

        return {
            1: "0331",
            2: "0630",
            3: "0930",
            4: "1231",
        }.get(
            quarter,
            "1231",
        )

    @staticmethod
    def _find_column(
        df: pandas.DataFrame,
        candidates: list[str],
    ) -> Optional[str]:
        """
        从 DataFrame 中寻找第一个存在的字段。
        """

        if df is None:
            return None

        for column in candidates:

            if column in df.columns:
                return column

        return None

    @staticmethod
    def _safe_float(
        value,
    ) -> Optional[float]:
        """
        安全转换 float。
        """

        if value is None:
            return None

        try:

            if pandas.isna(value):
                return None

            return float(value)

        except Exception:
            return None
