from datetime import date

from attr import dataclass

from core.models.etf.composition_item import ETFCompositionItem


@dataclass(slots=True)
class ETFComposition:
    """ETF 成分股及申赎信息。"""

    symbol: str
    trade_date: date

    creation_unit: int | None = None
    creation_unit_cash: float | None = None

    nav: float | None = None
    estimated_cash_component: float | None = None
    cash_component: float | None = None

    items: list[ETFCompositionItem] | None = None

    def display(self) -> None:
        """显示 ETF 成分股及申赎信息。"""

        print(f"ETF代码: {self.symbol}")
        print(f"交易日期: {self.trade_date}")
        print(
            f"最小申赎单位: "
            f"{self.creation_unit if self.creation_unit is not None else '-'}"
        )
        print(
            f"最小申赎单位现金: " f"{self.creation_unit_cash:.2f}"
            if self.creation_unit_cash is not None
            else "最小申赎单位现金: -"
        )
        print(f"基金净值: {self.nav:.4f}" if self.nav is not None else "基金净值: -")
        print(
            f"预估现金差额: {self.estimated_cash_component:.2f}"
            if self.estimated_cash_component is not None
            else "预估现金差额: -"
        )
        print(
            f"现金差额: {self.cash_component:.2f}"
            if self.cash_component is not None
            else "现金差额: -"
        )

        if not self.items:
            print("成分股: 无")
            return

        print(f"成分股数量: {len(self.items)}")
        print("-" * 70)

        for item in self.items:
            item.display()
