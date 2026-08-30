from __future__ import annotations

import datetime
from typing import Optional

import pandas

from gateways.analysis.valuation import ValuationAnalyzer
from common.constants import Interval, TEN_THOUSAND
from core.models.valuation import Valuation
from utils.stock_mapping import normalize_symbol


class YinheValuation:
    """
    银河证券估值模块。

    负责：

        - 获取估值所需基础数据
        - 将银河原始数据转换为项目统一字段
        - 调用 ValuationAnalyzer
        - 组装 Valuation

    不负责：

        - PE 计算
        - PB 计算
        - PS 计算
        - PEG 计算
        - EV 计算
        - 股息率计算

    所有估值计算统一由 ValuationAnalyzer 完成。
    """

    def __init__(
        self,
        gateway,
    ) -> None:
        self.gateway = gateway
        self.analyzer = ValuationAnalyzer()

    # ==========================================================
    # Public API
    # ==========================================================

    def fetch_valuation(
        self,
        symbol: str,
    ) -> Valuation | None:
        """
        获取完整估值数据。
        """

        self.gateway._ensure_started()

        symbol = normalize_symbol(symbol)

        print(
            f"[{symbol}] 正在获取估值数据..."
        )

        try:
            # ==================================================
            # 1. 当前价格
            # ==================================================

            price = self._get_current_price(
                symbol
            )

            if price is None:
                print(
                    f"[银河估值] 未获取到当前价格: "
                    f"{symbol}"
                )
                return None

            # ==================================================
            # 2. 股本
            # ==================================================

            (
                total_shares,
                circulating_shares,
                equity_report_date,
            ) = self._get_equity_structure(
                symbol
            )

            # ==================================================
            # 3. 财务基础数据
            # ==================================================

            base = self._get_financial_base(
                symbol
            )

            # ==================================================
            # 4. 计算估值指标
            #
            # 注意：
            # 这里传入的已经全部是统一后的基础数据，
            # ValuationAnalyzer 不接触 DataFrame。
            # ==================================================

            metrics = self.analyzer.analyze(
                price=price,

                total_shares=total_shares,

                circulating_shares=circulating_shares,

                net_profit=base["net_profit"],

                net_profit_ttm=base["net_profit_ttm"],

                net_profit_forecast=(
                    base["net_profit_forecast"]
                ),

                revenue=base["revenue"],

                revenue_ttm=base["revenue_ttm"],

                total_equity=base["total_equity"],

                cash=base["cash"],

                debt=base["debt"],

                ebitda=base["ebitda"],

                dividend=base["dividend"],

                profit_growth=base["profit_growth"],
            )

            # ==================================================
            # 5. 报告期
            # ==================================================

            report_date = (
                base["report_date"]
                or equity_report_date
            )

            # ==================================================
            # 6. 返回 Valuation
            # ==================================================

            return Valuation(
                symbol=symbol,

                timestamp=datetime.datetime.now(),

                report_date=report_date,

                # --------------------------------------------------
                # 基础数据
                # --------------------------------------------------

                price=price,

                total_shares=total_shares,

                circulating_shares=circulating_shares,

                net_profit=base["net_profit"],

                net_profit_ttm=(
                    base["net_profit_ttm"]
                ),

                net_profit_forecast=(
                    base["net_profit_forecast"]
                ),

                revenue=base["revenue"],

                revenue_ttm=(
                    base["revenue_ttm"]
                ),

                total_equity=(
                    base["total_equity"]
                ),

                book_value_per_share=(
                    base["book_value_per_share"]
                ),

                cash=base["cash"],

                debt=base["debt"],

                ebitda=base["ebitda"],

                dividend=base["dividend"],

                # --------------------------------------------------
                # 计算结果
                # --------------------------------------------------

                metrics=metrics,

                # --------------------------------------------------
                # 来源
                # --------------------------------------------------

                source=self.gateway.display_name,

                data_type="report",
            )

        except Exception as exc:
            print(
                f"[银河估值] 获取失败 "
                f"{symbol}: {exc}"
            )

            return None

    # ==========================================================
    # Price
    # ==========================================================

    def _get_current_price(
        self,
        symbol: str,
    ) -> Optional[float]:
        """
        使用最近交易日 K 线收盘价作为当前价格。
        """

        klines = self.gateway.fetch_kline(
            symbol=symbol,
            interval=Interval.DAY_1,
            start_time=(
                datetime.datetime.now()
                - datetime.timedelta(days=30)
            ),
            end_time=datetime.datetime.now(),
            limit=30,
        )

        if not klines:
            return None

        return klines[-1].close

    # ==========================================================
    # Equity Structure
    # ==========================================================

    def _get_equity_structure(
        self,
        symbol: str,
    ) -> tuple[
        Optional[float],
        Optional[float],
        Optional[str],
    ]:
        """
        获取总股本和流通股本。

        银河原始单位：

            万股

        标准模型：

            股
        """

        total_shares = None
        circulating_shares = None
        report_date = None

        try:
            equity_structure = (
                self.gateway.info_data.get_equity_structure(
                    [symbol],
                    local_path=self.gateway.local_path,
                    is_local=False,
                )
            )

            if (
                equity_structure is None
                or equity_structure.empty
            ):
                return None, None, None

            if "CHANGE_DATE" in equity_structure.columns:
                equity_structure = (
                    equity_structure.sort_values(
                        "CHANGE_DATE"
                    )
                )

            row = equity_structure.iloc[-1]

            # --------------------------------------------------
            # 总股本
            # --------------------------------------------------

            value = row.get("TOT_SHARE")

            if pandas.notna(value):
                total_shares = (
                    float(value)
                    * TEN_THOUSAND
                )

            # --------------------------------------------------
            # 流通股本
            # --------------------------------------------------

            for field in (
                "FLOAT_SHARE",
                "CIRC_SHARE",
            ):
                if field not in row.index:
                    continue

                value = row.get(field)

                if pandas.notna(value):
                    circulating_shares = (
                        float(value)
                        * TEN_THOUSAND
                    )
                    break

            # --------------------------------------------------
            # 股本变更日期
            # --------------------------------------------------

            value = row.get("CHANGE_DATE")

            if pandas.notna(value):
                report_date = str(value)

        except Exception as exc:
            print(
                f"[银河估值] 获取股本失败 "
                f"{symbol}: {exc}"
            )

        return (
            total_shares,
            circulating_shares,
            report_date,
        )

    # ==========================================================
    # Financial Base
    # ==========================================================

    def _get_financial_base(
        self,
        symbol: str,
    ) -> dict:
        """
        获取估值所需基础数据。

        这里负责：

            银河财务数据
                ↓
            项目统一基础数据

        不负责估值计算。
        """

        result = {
            "net_profit": None,
            "net_profit_ttm": None,
            "net_profit_forecast": None,

            "revenue": None,
            "revenue_ttm": None,

            "total_equity": None,
            "book_value_per_share": None,

            "cash": None,
            "debt": None,
            "ebitda": None,

            "dividend": None,

            "profit_growth": None,

            "report_date": None,
        }

        # ======================================================
        # 获取完整财务数据
        # ======================================================

        financial = self.gateway.fetch_financial(
            symbol
        )

        if financial is None:
            return result

        result["report_date"] = (
            financial.report_date
        )

        # ======================================================
        # 利润表
        # ======================================================

        income = financial.income

        if income is not None:

            # --------------------------------------------------
            # 归母净利润优先
            # --------------------------------------------------

            result["net_profit"] = (
                income.net_profit_attributable
                if income.net_profit_attributable
                is not None
                else income.net_profit
            )

            result["revenue"] = income.revenue

            result["ebitda"] = income.ebitda

        # ======================================================
        # 资产负债表
        # ======================================================

        balance = financial.balance

        if balance is not None:

            result["total_equity"] = (
                balance.shareholders_equity
            )

            result["cash"] = balance.cash

            # --------------------------------------------------
            # 有息债务
            # --------------------------------------------------

            debt = 0.0
            has_debt = False

            for value in (
                balance.short_term_debt,
                balance.long_term_debt,
                balance.bonds_payable,
            ):
                if value is not None:
                    debt += value
                    has_debt = True

            if has_debt:
                result["debt"] = debt

            # --------------------------------------------------
            # 每股净资产
            # 后面再用股本计算
            # --------------------------------------------------

        # ======================================================
        # 财务指标
        # ======================================================

        indicators = financial.indicators

        if indicators is not None:

            if hasattr(
                indicators,
                "net_profit_yoy",
            ):
                result["profit_growth"] = (
                    indicators.net_profit_yoy
                )

        return result