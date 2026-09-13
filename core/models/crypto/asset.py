from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CryptoAsset:
    """加密货币资产。"""

    symbol: str
    name: str

    base_currency: str
    quote_currency: str

    exchange: str = ""
    asset_type: str = "crypto"

    market: str = "spot"
    status: str = "TRADING"

    website: str = ""
    description: str = ""

    def display(self) -> None:
        print()
        print("=" * 60)
        print(f"{self.symbol} 资产")
        print("=" * 60)

        print(f"    交易对:     {self.symbol}")
        print(f"    名称:       {self.name}")
        print(f"    基础资产:   {self.base_currency}")
        print(f"    计价资产:   {self.quote_currency}")
        print(f"    交易所:     {self.exchange}")
        print(f"    资产类型:   {self.asset_type}")
        print(f"    市场:       {self.market}")
        print(f"    状态:       {self.status}")
