import datetime

from typing import Optional

import AmazingData

from common.constants import Interval
from core.models.kline import Kline

from utils.stock_mapping import normalize_symbol


class YinheKline:
    """
    银河证券K线模块。


    负责：

        - 日K
        - 周K
        - 分钟K

    转换：

        AmazingData DataFrame

                ↓

        list[Kline]
    """

    def __init__(
        self,
        gateway,
    ):

        self.gateway = gateway

    def fetch_kline(
        self,
        symbol: str,
        interval: Interval = Interval.DAY_1,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 1000,
    ) -> list[Kline]:

        self.gateway._ensure_started()

        # ------------------------------------------------------
        # 1. 周期映射
        # ------------------------------------------------------

        period_map = {
            Interval.MINUTE_1: AmazingData.constant.Period.min1.value,
            Interval.MINUTE_5: AmazingData.constant.Period.min5.value,
            Interval.MINUTE_15: AmazingData.constant.Period.min15.value,
            Interval.MINUTE_30: AmazingData.constant.Period.min30.value,
            Interval.MINUTE_60: AmazingData.constant.Period.min60.value,
            Interval.DAY_1: AmazingData.constant.Period.day.value,
            Interval.WEEK_1: AmazingData.constant.Period.week.value,
        }

        period = period_map.get(
            interval,
            AmazingData.constant.Period.day.value,
        )

        # ------------------------------------------------------
        # 2. 股票代码标准化
        # ------------------------------------------------------

        symbol = normalize_symbol(symbol)

        # ------------------------------------------------------
        # 3. 日期处理
        # ------------------------------------------------------

        today_str = datetime.datetime.now().strftime("%Y%m%d")

        begin_str = start_time.strftime("%Y%m%d") if start_time else today_str

        end_str = end_time.strftime("%Y%m%d") if end_time else today_str

        # ------------------------------------------------------
        # 4. 查询数据
        # ------------------------------------------------------

        try:

            kline_dict = self.gateway.market_data.query_kline(
                [symbol],
                period=period,
                begin_date=int(begin_str),
                end_date=int(end_str),
            )

            if kline_dict is None:
                return []

            df = kline_dict.get(symbol)

            if df is None:

                print(f"[银河网关] {symbol} 无返回数据")

                return []

            if hasattr(df, "empty") and df.empty:

                print(f"[银河网关] {symbol} 返回数据为空")

                return []

            # --------------------------------------------------
            # DataFrame → List[Dict]
            # --------------------------------------------------

            if hasattr(df, "to_dict"):

                raw_bars = df.to_dict("records")

            else:

                raw_bars = df

            # --------------------------------------------------
            # limit
            # --------------------------------------------------

            if limit and len(raw_bars) > limit:

                raw_bars = raw_bars[-limit:]

        except Exception as e:

            print(f"[银河网关] query_kline 查询失败: {e}")

            return []

        # ------------------------------------------------------
        # 5. 转换成统一 Kline
        # ------------------------------------------------------

        klines: list[Kline] = []

        for item in raw_bars:

            try:

                kline_time = item.get("kline_time")
                
                if kline_time is None:
                    print("❌ 缺少 kline_time")
                    print(item)
                    continue

                if hasattr(kline_time, "to_pydatetime"):
                    kline_time = kline_time.to_pydatetime()

                klines.append(
                    Kline(
                        symbol=symbol,
                        timestamp=kline_time,
                        interval=interval,
                        open=float(item["open"]),
                        high=float(item["high"]),
                        low=float(item["low"]),
                        close=float(item["close"]),
                        volume=int(item["volume"]),
                        amount=float(item["amount"]),
                    )
                )

            except Exception as e:

                print(f"[银河网关] 转换 Kline 失败: {e}")

                print(f"    原始数据: {item}")

                continue

        return klines
