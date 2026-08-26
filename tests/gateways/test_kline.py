from datetime import datetime, timedelta

from common.constants import Interval
from gateways.manager import DataManager

"""
python -m tests.gateways.test_kline
"""


def test_kline(
    provider_name: str,
    symbol: str,
) -> None:

    print(f"【K线数据】{provider_name} / {symbol}")

    data = None

    try:
        data = DataManager(provider_name)

        data.start()

        klines = data.get_kline(
            symbol=symbol,
            interval=Interval.DAY_1,
            start_time=datetime.now() - timedelta(days=365),
            end_time=datetime.now(),
            limit=10,
        )

        if not klines:
            print("❌ 未获取到 K 线数据")
            return

        print(f"✅ 获取数量：{len(klines)}")

        print()
        print("最近 K 线：")

        for kline in klines[-5:]:

            print(
                f"  {kline.timestamp:%Y-%m-%d} "
                f"O:{kline.open:.2f} "
                f"H:{kline.high:.2f} "
                f"L:{kline.low:.2f} "
                f"C:{kline.close:.2f} "
                f"V:{kline.volume}"
            )

        print()

        print("最新 K 线详情：")

        klines[-1].display()

    except NotImplementedError:
        print("⚠️ 当前数据源暂未实现 K 线")

    except Exception as exc:
        print(f"❌ 获取 K 线失败：{exc}")

    finally:

        if data is not None:
            try:
                data.stop()
            except Exception:
                pass


def main() -> None:

    test_kline(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
