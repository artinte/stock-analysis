from __future__ import annotations

from typing import Optional

from core.models.valuation_metrics import ValuationMetrics


class ValuationAnalyzer:
    """
    股票估值分析器。

    负责根据估值基础数据计算：

        - 总市值
        - 流通市值
        - PE（静态）
        - PE（动态）
        - PE（TTM）
        - PB
        - PS（静态）
        - PS（TTM）
        - PEG
        - 企业价值 EV
        - EV / EBITDA
        - 盈利收益率
        - 股息率

    注意：

        1. 不负责获取数据
        2. 不依赖具体数据源
        3. 不处理 DataFrame
        4. 不认识银河字段名
        5. 所有输入均为项目统一后的基础数据
    """

    def analyze(
        self,
        *,
        price: Optional[float],
        total_shares: Optional[float],
        circulating_shares: Optional[float],
        net_profit: Optional[float],
        net_profit_ttm: Optional[float],
        net_profit_forecast: Optional[float],
        revenue: Optional[float],
        revenue_ttm: Optional[float],
        total_equity: Optional[float],
        cash: Optional[float],
        debt: Optional[float],
        ebitda: Optional[float],
        dividend: Optional[float],
        profit_growth: Optional[float],
    ) -> ValuationMetrics:
        """
        根据估值基础数据计算估值指标。

        单位约定：

            price:
                元 / 股

            total_shares:
                股

            market_cap:
                元

            net_profit / revenue / equity / debt / cash / ebitda:
                元

            dividend:
                元 / 股

            profit_growth:
                百分比，例如 20.0 表示 20%
        """

        # ======================================================
        # 市值
        # ======================================================

        market_cap = self._calculate_market_cap(
            price=price,
            shares=total_shares,
        )

        circulating_market_cap = self._calculate_market_cap(
            price=price,
            shares=circulating_shares,
        )

        # ======================================================
        # PE
        # ======================================================

        pe_static = self._calculate_pe(
            market_cap=market_cap,
            profit=net_profit,
        )

        pe_ttm = self._calculate_pe(
            market_cap=market_cap,
            profit=net_profit_ttm,
        )

        pe_dynamic = self._calculate_pe(
            market_cap=market_cap,
            profit=net_profit_forecast,
        )

        # ======================================================
        # PB
        # ======================================================

        pb = self._calculate_pb(
            market_cap=market_cap,
            equity=total_equity,
        )

        # ======================================================
        # PS
        # ======================================================

        ps_static = self._calculate_ps(
            market_cap=market_cap,
            revenue=revenue,
        )

        ps_ttm = self._calculate_ps(
            market_cap=market_cap,
            revenue=revenue_ttm,
        )

        # ======================================================
        # PEG
        # ======================================================

        peg = self._calculate_peg(
            pe=pe_ttm,
            growth=profit_growth,
        )

        # ======================================================
        # 企业价值
        # ======================================================

        enterprise_value = self._calculate_enterprise_value(
            market_cap=market_cap,
            debt=debt,
            cash=cash,
        )

        # ======================================================
        # EV / EBITDA
        # ======================================================

        ev_ebitda = self._calculate_ev_ebitda(
            enterprise_value=enterprise_value,
            ebitda=ebitda,
        )

        # ======================================================
        # 盈利收益率
        # ======================================================

        earnings_yield = self._calculate_earnings_yield(
            pe_ttm=pe_ttm,
            pe_static=pe_static,
        )

        # ======================================================
        # 股息率
        # ======================================================

        dividend_yield = self._calculate_dividend_yield(
            price=price,
            dividend=dividend,
        )

        return ValuationMetrics(
            market_cap=market_cap,
            circulating_market_cap=circulating_market_cap,
            pe_static=pe_static,
            pe_dynamic=pe_dynamic,
            pe_ttm=pe_ttm,
            pb=pb,
            ps_static=ps_static,
            ps_ttm=ps_ttm,
            peg=peg,
            enterprise_value=enterprise_value,
            ev_ebitda=ev_ebitda,
            earnings_yield=earnings_yield,
            dividend_yield=dividend_yield,
        )

    # ==========================================================
    # Market Cap
    # ==========================================================

    @staticmethod
    def _calculate_market_cap(
        *,
        price: Optional[float],
        shares: Optional[float],
    ) -> Optional[float]:
        """
        市值 = 股价 × 股本。
        """

        if price is None:
            return None

        if shares is None:
            return None

        if price <= 0:
            return None

        if shares <= 0:
            return None

        return round(
            price * shares,
            2,
        )

    # ==========================================================
    # PE
    # ==========================================================

    @staticmethod
    def _calculate_pe(
        *,
        market_cap: Optional[float],
        profit: Optional[float],
    ) -> Optional[float]:
        """
        PE = 市值 / 净利润。
        """

        if market_cap is None:
            return None

        if profit is None:
            return None

        if market_cap <= 0:
            return None

        if profit <= 0:
            return None

        return round(
            market_cap / profit,
            2,
        )

    # ==========================================================
    # PB
    # ==========================================================

    @staticmethod
    def _calculate_pb(
        *,
        market_cap: Optional[float],
        equity: Optional[float],
    ) -> Optional[float]:
        """
        PB = 市值 / 归母净资产。
        """

        if market_cap is None:
            return None

        if equity is None:
            return None

        if market_cap <= 0:
            return None

        if equity <= 0:
            return None

        return round(
            market_cap / equity,
            2,
        )

    # ==========================================================
    # PS
    # ==========================================================

    @staticmethod
    def _calculate_ps(
        *,
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

        if market_cap <= 0:
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
        *,
        pe: Optional[float],
        growth: Optional[float],
    ) -> Optional[float]:
        """
        PEG = PE / 净利润增长率。

        growth 使用百分比数值。

        例如：

            PE = 20
            growth = 10

            PEG = 2
        """

        if pe is None:
            return None

        if growth is None:
            return None

        if pe <= 0:
            return None

        if growth <= 0:
            return None

        return round(
            pe / growth,
            2,
        )

    # ==========================================================
    # Enterprise Value
    # ==========================================================

    @staticmethod
    def _calculate_enterprise_value(
        *,
        market_cap: Optional[float],
        debt: Optional[float],
        cash: Optional[float],
    ) -> Optional[float]:
        """
        EV = 市值 + 债务 - 现金。

        单位：元。
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
        *,
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

        if enterprise_value <= 0:
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
        *,
        pe_ttm: Optional[float],
        pe_static: Optional[float],
    ) -> Optional[float]:
        """
        盈利收益率 = 1 / PE × 100%。

        优先使用 TTM PE。
        """

        pe = pe_ttm if pe_ttm is not None else pe_static

        if pe is None:
            return None

        if pe <= 0:
            return None

        return round(
            1 / pe * 100,
            2,
        )

    # ==========================================================
    # Dividend Yield
    # ==========================================================

    @staticmethod
    def _calculate_dividend_yield(
        *,
        price: Optional[float],
        dividend: Optional[float],
    ) -> Optional[float]:
        """
        股息率 = 每股股息 / 股价 × 100%。
        """

        if price is None:
            return None

        if dividend is None:
            return None

        if price <= 0:
            return None

        if dividend < 0:
            return None

        return round(
            dividend / price * 100,
            2,
        )
