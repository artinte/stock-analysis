from __future__ import annotations

import datetime
from typing import Optional

import pandas


class ValuationAnalyzer:
    """
    股票估值分析器。

    负责根据股票市值和财务数据计算：

    - PE(TTM)
    - PE(静态)
    - PE(动态)
    - PS
    - PB
    """

    Q_MAP = {
        1: "0331",
        2: "0630",
        3: "0930",
        4: "1231",
    }

    def calculate_pe(
        self,
        df: pandas.DataFrame,
        market_cap: float,
        pe_type: str = "TTM",
    ) -> float:
        """
        计算 PE。
        """

        profit_field = "NET_PRO_EXCL_MIN_INT_INC"

        period_field = "REPORTING_PERIOD"

        if profit_field not in df.columns or period_field not in df.columns:
            return float("nan")

        profit_data = df.set_index(df[period_field].astype(str))[profit_field].to_dict()

        target_period, quarter = self._find_latest_period(profit_data)

        if not target_period:
            return float("nan")

        year = int(target_period[:4])

        previous_year = year - 1

        current_profit = profit_data.get(
            target_period,
            0,
        )

        previous_profit = profit_data.get(
            f"{previous_year}" f"{self.Q_MAP[quarter]}",
            0,
        )

        last_year_profit = profit_data.get(
            f"{previous_year}1231",
            0,
        )

        pe_type = pe_type.upper()

        if pe_type == "TTM":

            profit_ttm = current_profit + (last_year_profit - previous_profit)

            if profit_ttm > 0:
                return round(
                    market_cap / (profit_ttm / 1e8),
                    2,
                )

        elif pe_type in (
            "STATIC",
            "LYR",
        ):

            if last_year_profit > 0:
                return round(
                    market_cap / (last_year_profit / 1e8),
                    2,
                )

        elif pe_type in (
            "DYNAMIC",
            "FORWARD",
        ):

            if quarter > 0 and current_profit > 0:

                annual_profit = current_profit / quarter * 4

                return round(
                    market_cap / (annual_profit / 1e8),
                    2,
                )

        return float("nan")

    def calculate_ps(
        self,
        df: pandas.DataFrame,
        market_cap: float,
    ) -> float:
        """
        计算 PS(TTM)。
        """

        revenue_field = "TOT_OPERA_REV"
        period_field = "REPORTING_PERIOD"

        if revenue_field not in df.columns or period_field not in df.columns:
            return float("nan")

        revenue_data = df.set_index(df[period_field].astype(str))[
            revenue_field
        ].to_dict()

        target_period, quarter = self._find_latest_period(revenue_data)

        if not target_period:
            return float("nan")

        year = int(target_period[:4])

        previous_year = year - 1

        current_revenue = revenue_data.get(
            target_period,
            0,
        )

        last_year_revenue = revenue_data.get(
            f"{previous_year}1231",
            0,
        )

        previous_revenue = revenue_data.get(
            f"{previous_year}" f"{self.Q_MAP[quarter]}",
            0,
        )

        revenue_ttm = current_revenue + (last_year_revenue - previous_revenue)

        if revenue_ttm <= 0:
            return float("nan")

        return round(
            market_cap / (revenue_ttm / 1e8),
            2,
        )

    def calculate_pb(
        self,
        df: pandas.DataFrame,
        market_cap: float,
    ) -> float:
        """
        计算 PB。
        """

        equity_field = "TOT_SHRHLDR_EQY_EXCL_MIN_INT"

        period_field = "REPORTING_PERIOD"

        if equity_field not in df.columns or period_field not in df.columns:
            return float("nan")

        df = df.sort_values(period_field)

        equity = df.iloc[-1][equity_field]

        if pandas.isna(equity) or equity <= 0:
            return float("nan")

        return round(
            market_cap / (equity / 1e8),
            2,
        )

    def _find_latest_period(
        self,
        data: dict,
    ) -> tuple[
        Optional[str],
        int,
    ]:

        now = datetime.datetime.now()

        for i in range(1, 7):

            dt = now - datetime.timedelta(days=i * 90)

            for quarter in (
                4,
                3,
                2,
                1,
            ):

                period = f"{dt.year}" f"{self.Q_MAP[quarter]}"

                if period in data and not pandas.isna(data[period]):

                    return (
                        period,
                        quarter,
                    )

        return (
            None,
            0,
        )
