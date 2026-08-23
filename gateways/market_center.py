from dataclasses import dataclass, field

from models.index import Index
from models.market_statistics import MarketStatistics


@dataclass(slots=True)
class MarketCenter:
    """
    股票市场数据中心。
    """

    indices: list[Index] = field(default_factory=list)

    statistics: list[MarketStatistics] = field(default_factory=list)

    def add_index(self, index: Index) -> None:
        self.indices.append(index)

    def add_statistics(self, statistics: MarketStatistics) -> None:
        self.statistics.append(statistics)

    def get_statistics(self, market: str) -> MarketStatistics | None:
        for item in self.statistics:
            if item.market == market:
                return item

        return None

    def display(self) -> None:
        """打印市场信息。"""

        print("主要指数：")

        for index in self.indices:
            price = f"{index.price:.2f}" if index.price is not None else "-"

            change = (
                f"{index.change_percent:.2f}%"
                if index.change_percent is not None
                else "-"
            )

            print(
                f"  {index.symbol}  " f"{index.name or '-'}  " f"{price}  " f"{change}"
            )

        for statistics in self.statistics:
            print()
            statistics.display()


if __name__ == "__main__":
    market = MarketCenter()

    market.add_statistics(
        MarketStatistics(
            market="全市场",
            total_count=5000,
            advancing_count=2800,
            declining_count=1900,
            unchanged_count=300,
            limit_up_count=80,
            limit_down_count=20,
        )
    )

    market.add_statistics(
        MarketStatistics(
            market="主板",
            total_count=3000,
            advancing_count=1600,
            declining_count=1200,
            limit_up_count=50,
            limit_down_count=10,
        )
    )

    market.add_statistics(
        MarketStatistics(
            market="科创板",
            total_count=600,
            advancing_count=350,
            declining_count=220,
            limit_up_count=8,
            limit_down_count=2,
        )
    )
