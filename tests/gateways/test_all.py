from gateways.manager import DataManager

from tests.gateways.test_quote import run_quote_test
from tests.gateways.test_stock import run_stock_test
from tests.gateways.test_kline import run_kline_test
from tests.gateways.test_valuation import run_valuation_test


def main():

    provider_name = "yinhe"
    symbol = "600519.SH"

    data_manager = DataManager(provider_name)

    try:
        data_manager.start()

        print("=" * 80)
        run_stock_test(data_manager, symbol)

        print("=" * 80)
        run_kline_test(data_manager, symbol)

        print("=" * 80)
        run_quote_test(data_manager, symbol)
        
        print("=" * 80)
        

        print("=" * 80)
        run_valuation_test(data_manager, symbol)

    finally:

        data_manager.stop()


if __name__ == "__main__":
    main()
