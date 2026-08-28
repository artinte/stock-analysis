from gateways.manager import DataManager

from tests.gateways.test_quote import run_quote_test
from tests.gateways.test_stock import run_stock_test
from tests.gateways.test_kline import run_kline_test


def main():

    provider_name = "yinhe"
    symbol = "600519.SH"

    data = DataManager(provider_name)

    try:

        data.start()

        print("=" * 80)
        run_stock_test(data, symbol)

        print("=" * 80)
        run_kline_test(data, symbol)

        print("=" * 80)
        run_quote_test(data, symbol)

        print("=" * 80)

    finally:

        data.stop()


if __name__ == "__main__":
    main()
