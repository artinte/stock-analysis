from __future__ import annotations

from datetime import datetime, timedelta

from common.constants import Interval
from gateways.data_manager import DataManager

"""
K线数据测试。

运行：

python -m tests.gateways.test_kline
"""


def run_kline_test(
    data: DataManager,
    symbol: str,
) -> None:
    """
    使用已有 DataManager 测试 K 线。

    注意：
        不负责 DataManager 的启动和关闭。

    用于：
        1. 独立测试
        2. 集成测试（多个模块共用一个 DataManager）
    """

    now = datetime.now()

    tests = [
        (
            "日 K",
            Interval.DAY_1,
            now - timedelta(days=365),
            now,
        ),
        (
            "5分钟 K",
            Interval.MINUTE_5,
            now - timedelta(days=5),
            now,
        ),
    ]

    for name, interval, start_time, end_time in tests:
        print(f"【{name}】" f"{symbol} / {interval.value}")

        try:
            klines = data.get_kline(
                symbol=symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=10,
            )

            if not klines:
                print("❌ 未获取到 K 线数据")
                continue

            print(f"✅ 获取 K 线数量：{len(klines)}")

            print()

            print("最近 5 根 K 线:")

            for kline in klines[-5:]:

                print(
                    f"  {kline.timestamp:%Y-%m-%d %H:%M:%S} "
                    f"O:{kline.open:.2f} "
                    f"H:{kline.high:.2f} "
                    f"L:{kline.low:.2f} "
                    f"C:{kline.close:.2f} "
                    f"V:{kline.volume}"
                )

            print()

            print("最新 K 线详情:")

            klines[-1].display()

        except NotImplementedError:

            print("⚠️ 当前数据源暂未实现 K 线")

        except Exception as exc:

            print(f"❌ 获取 K 线失败：{exc}")


def test_kline(
    provider_name: str,
    symbol: str,
) -> None:
    """
    独立 K 线测试入口。

    单独运行时：
        创建 DataManager
        启动数据源
        测试 K 线
        关闭数据源
    """

    print(f"【K线测试】" f"{provider_name} / {symbol}")

    data: DataManager | None = None

    try:

        data = DataManager(provider_name)

        data.start()

        run_kline_test(
            data,
            symbol,
        )

    except Exception as exc:

        print(f"❌ K线测试失败：{exc}")

    finally:

        if data is not None:

            try:

                data.stop()

                print("✅ 数据源已关闭")

            except Exception as exc:

                print(f"⚠️ 关闭数据源失败：{exc}")


def main() -> None:

    test_kline(
        provider_name="yinhe",
        symbol="600519.SH",
    )


if __name__ == "__main__":
    main()
