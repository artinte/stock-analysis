from attr import dataclass


@dataclass(slots=True)
class ETFCompositionItem:
    """ETF 成分证券。"""

    symbol: str
    name: str

    quantity: int | None = None
    weight: float | None = None
    price: float | None = None
    amount: float | None = None

    def display(self) -> None:
        """显示 ETF 成分证券信息。"""
        print(f"代码: {self.symbol}")
        print(f"名称: {self.name}")
        print(f"数量: {self.quantity if self.quantity is not None else '-'}")
        print(f"权重: {self.weight:.2f}%" if self.weight is not None else "权重: -")
        print(f"价格: {self.price:.2f}" if self.price is not None else "价格: -")
        print(f"金额: {self.amount:.2f}" if self.amount is not None else "金额: -")
