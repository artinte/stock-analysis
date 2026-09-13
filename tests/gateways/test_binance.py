from __future__ import annotations

from core.models.crypto.asset import CryptoAsset
from gateways.data_manager import DataManager

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
        symbol="BTC/USDT",
        name="Bitcoin",
        base_currency="BTC",
        quote_currency="USDT",
        exchange="Binance",
    )

    asset.display()


def run_quote_test(manager: DataManager) -> None:
    print()
    print("=" * 60)
    print("测试：get_crypto_quote")
    print("=" * 60)

    quote = manager.get_crypto_quote("BTC/USDT")

    quote.display()


def run_quotes_test(manager: DataManager) -> None:
    print()
    print("=" * 60)
    print("测试：get_crypto_quotes")
    print("=" * 60)

    quotes = manager.get_crypto_quotes(
        [
            "BTC/USDT",
            "ETH/USDT",
            "BNB/USDT",
        ]
    )

    for quote in quotes:
        quote.display()


def run_klines_test(manager: DataManager) -> None:
    print()
    print("=" * 60)
    print("测试：get_crypto_klines")
    print("=" * 60)

    klines = manager.get_crypto_klines(
        symbol="BTC/USDT",
        interval="1d",
        limit=5,
    )

    for kline in klines:
        kline.display()


def run_order_book_test(manager: DataManager) -> None:
    print()
    print("=" * 60)
    print("测试：get_crypto_order_book")
    print("=" * 60)

    order_book = manager.get_crypto_order_book(
        symbol="BTC/USDT",
        limit=5,
    )

    print(f"    交易对: {order_book['symbol']}")
    print()

    print("    买盘:")
    for item in order_book["bids"]:
        print(f"        价格: {item['price']:<15} " f"数量: {item['quantity']}")

    print()
    print("    卖盘:")
    for item in order_book["asks"]:
        print(f"        价格: {item['price']:<15} " f"数量: {item['quantity']}")


def run_trades_test(manager: DataManager) -> None:
    print()
    print("=" * 60)
    print("测试：get_crypto_trades")
    print("=" * 60)

    trades = manager.get_crypto_trades(
        symbol="BTC/USDT",
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
    manager = DataManager()

    try:
        manager.start()

        run_asset_test()
        run_quote_test(manager)
        run_quotes_test(manager)
        run_klines_test(manager)
        run_order_book_test(manager)
        run_trades_test(manager)

    finally:
        manager.stop()


if __name__ == "__main__":
    main()
