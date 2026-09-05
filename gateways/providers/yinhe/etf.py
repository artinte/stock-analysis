from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from core.models.etf.composition import ETFComposition
from core.models.etf.composition_item import ETFCompositionItem


class YinheETF:
    """
    银河证券 ETF 数据适配器。

    负责：
        AmazingData.get_etf_pcf()

    转换：

        etf_pcf_info
            ↓
        ETFComposition

        etf_pcf_constituent
            ↓
        ETFCompositionItem
    """

    def __init__(self, gateway):
        self.gateway = gateway

    def fetch_etf_composition(
        self,
        symbol: str,
        trade_date: Optional[date] = None,
    ) -> Optional[ETFComposition]:
        self.gateway._ensure_started()

        try:
            return self._fetch_etf_composition(symbol)
        except Exception as e:
            print(f"[银河网关] 获取 ETF 成分股失败 {symbol}: {e}")
            return None

    def _fetch_etf_composition(
        self,
        symbol: str,
    ) -> Optional[ETFComposition]:

        etf_pcf_info, etf_pcf_constituent = self.gateway.base_data.get_etf_pcf([symbol])

        if etf_pcf_info is None or etf_pcf_info.empty:
            return None

        # ETF 代码在 index
        row = etf_pcf_info.loc[symbol]

        trade_date = self._parse_date(row.get("trading_day"))

        items = self._parse_constituents(etf_pcf_constituent.get(symbol))

        return ETFComposition(
            symbol=symbol,
            trade_date=trade_date,
            creation_unit=self._to_int(row.get("creation_redemption_unit")),
            nav=self._to_float(row.get("nav")),
            estimated_cash_component=self._to_float(row.get("estimate_cash_component")),
            cash_component=self._to_float(row.get("cash_component")),
            items=items,
        )

    @staticmethod
    def _parse_constituents(
        df,
    ) -> list[ETFCompositionItem]:

        if df is None or df.empty:
            return []

        items: list[ETFCompositionItem] = []

        for _, row in df.iterrows():

            items.append(
                ETFCompositionItem(
                    symbol=str(row.get("underlying_symbol") or ""),
                    name="",
                    quantity=YinheETF._to_int(row.get("component_share")),
                )
            )

        return items

    @staticmethod
    def _parse_date(value) -> date:
        if isinstance(value, date):
            return value

        value = str(value)

        return datetime.strptime(
            value,
            "%Y%m%d",
        ).date()

    @staticmethod
    def _to_int(value) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float(value) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
