from __future__ import annotations

from core.models.crypto.asset import CryptoAsset
from gateways.providers.binance.gateway import BinanceGateway


"""
运行：
python -m tests.gateways.test_binance
"""

def run_asset_test() -> None:
    print()
    print("=" * 60)
    print("测试：CryptoAsset")
    print("=" * 60)

    asset = CryptoAsset(
        symbol="BTCUSDT",
        name="Bitcoin",
        base_currency="BTC",
        quote_currency="USDT",
        exchange="Binance",
    )

    asset.display()


def run_quote_test(gateway: BinanceGateway) -> None:
    print()
    print("=" * 60)
    print("测试：fetch_quote")
    print("=" * 60)

    quote = gateway.fetch_quote("BTCUSDT")
    quote.display()


def run_quotes_test(gateway: BinanceGateway) -> None:
    print()
    print("=" * 60)
    print("测试：fetch_quotes")
    print("=" * 60)

    quotes = gateway.fetch_quotes(
        [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
        ]
    )

    for quote in quotes:
        quote.display()


def run_klines_test(gateway: BinanceGateway) -> None:
    print()
    print("=" * 60)
    print("测试：fetch_klines")
    print("=" * 60)

    klines = gateway.fetch_klines(
        "BTCUSDT",
        interval="1d",
        limit=5,
    )

    for kline in klines:
        kline.display()


def run_order_book_test(gateway: BinanceGateway) -> None:
    print()
    print("=" * 60)
    print("测试：fetch_order_book")
    print("=" * 60)

    order_book = gateway.fetch_order_book(
        "BTCUSDT",
        limit=5,
    )

    print(f"    交易对: {order_book['symbol']}")
    print()

    print("    买盘:")
    for item in order_book["bids"]:
        print(
            f"        价格: {item['price']:<15} "
            f"数量: {item['quantity']}"
        )

    print()
    print("    卖盘:")
    for item in order_book["asks"]:
        print(
            f"        价格: {item['price']:<15} "
            f"数量: {item['quantity']}"
        )


def run_trades_test(gateway: BinanceGateway) -> None:
    print()
    print("=" * 60)
    print("测试：fetch_trades")
    print("=" * 60)

    trades = gateway.fetch_trades(
        "BTCUSDT",
        limit=5,
    )

    print(f"    交易笔数: {len(trades)}")
    print()

    for trade in trades:
        print(
            f"    价格: {trade['price']:<15} "
            f"数量: {trade['quantity']:<15} "
            f"时间: {trade['time']}"
        )


def main() -> None:
    gateway = BinanceGateway()

    run_asset_test()
    run_quote_test(gateway)
    run_quotes_test(gateway)
    run_klines_test(gateway)
    run_order_book_test(gateway)
    run_trades_test(gateway)


if __name__ == "__main__":
    main()

