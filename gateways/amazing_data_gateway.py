from datetime import datetime
from typing import List, Optional
from gateways.broker_gateway import BrokerGateway
from models.constants import Interval
from models.kline import Kline
from stock_detail import StockDetail
from utils import add_exchange_suffix
import AmazingData


class AmazingDataGateway(BrokerGateway):
    def __init__(self):
        self._is_connected = False
        self._user = ""
        self._host = ""
        self._port = 0

        self.info_data = None
        self.base_data = None
        self.calendar = None
        self.market_data = None

    def login(self, config: dict) -> bool:
        self.user = config.get("username")
        self.host = config.get("host")
        self.port = int(config.get("port", 0))  # 强制转为整数
        print(f"[银河网关] 尝试登录: {self.host}:{self.port} 用户: {self.user}")
        try:
            AmazingData.login(
                username=config["username"],
                password=config["password"],
                host=config["host"],
                port=int(config["port"]),
            )

            self.info_data = AmazingData.InfoData()
            self.base_data = AmazingData.BaseData()
            self.calendar = self.base_data.get_calendar()
            self.market_data = AmazingData.MarketData(self.calendar)

            self._is_connected = True
            print("登录成功")
            return True
        except ValueError:
            print("[错误] 端口格式无效，请检查配置。")
            return False
        except Exception as e:
            print(f"[错误] 登录异常: {e}")
            return False

    def fetch_kline(
        self,
        symbol: str,
        interval: Interval,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 10000,
    ) -> List[Kline]:
        """
        实现获取 K 线数据的逻辑
        """
        if not self._is_connected:
            raise ConnectionError("请先执行 login() 成功后再获取数据")

        # 1. 周期映射
        period_map = {
            Interval.MINUTE_1: AmazingData.constant.Period.min1.value,
            Interval.MINUTE_5: AmazingData.constant.Period.min5.value,
            Interval.MINUTE_15: AmazingData.constant.Period.min15.value,
            Interval.MINUTE_30: AmazingData.constant.Period.min30.value,
            Interval.HOUR_1: AmazingData.constant.Period.min60.value,
            Interval.DAY_1: AmazingData.constant.Period.day.value,
            Interval.WEEK_1: AmazingData.constant.Period.week.value,
        }
        period = period_map.get(interval, AmazingData.constant.Period.day.value)

        # 2. 代码标准化
        code = add_exchange_suffix(symbol)

        # 3. 日期处理：如果没有提供则默认取今天
        today_str = datetime.now().strftime("%Y%m%d")
        begin_str = start_time.strftime("%Y%m%d") if start_time else today_str
        end_str = end_time.strftime("%Y%m%d") if end_time else today_str

        # 5. 执行查询
        try:
            # 根据你之前的描述，query_kline 接受 list 格式的代码并返回字典
            kline_dict = self.market_data.query_kline(
                [code], period=period, begin_date=int(begin_str), end_date=int(end_str)
            )
            
            df = kline_dict.get(code)

            # 检查数据是否存在
            if df is None or (hasattr(df, 'empty') and df.empty):
                print(f"DEBUG: {code} 无返回数据")
                return []

            # --- 关键：将 DataFrame 转化为字典列表，这样 item 才是每一行的数据字典 ---
            if hasattr(df, 'to_dict'):
                raw_bars = df.to_dict('records')
            else:
                raw_bars = df

            # 如果本地有 limit 要求，进行末尾切片
            if limit and len(raw_bars) > limit:
                raw_bars = raw_bars[-limit:]

        except Exception as e:
            print(f"[数据错误] query_kline 查询失败: {e}")
            return []

        # 6. 解析数据为 Kline 对象
        klines = []
        for item in raw_bars:
            try:
                t_time = item.get("kline_time")
                if hasattr(t_time, 'to_pydatetime'):
                    t_time = t_time.to_pydatetime()
                klines.append(
                    Kline(
                        code=code,
                        trade_time=t_time,
                        open=float(item["open"]),
                        high=float(item["high"]),
                        low=float(item["low"]),
                        close=float(item["close"]),
                        volume=int(item["volume"]),
                        amount=float(item["amount"]),
                    )
                )
            except Exception as e:
                print(f"DEBUG: 转换单条 Kline 失败: {e}, 数据内容: {item}")
                continue

        return klines

    def fetch_market_data(self, symbol):
        if not self._is_connected:
            raise ConnectionError("请先执行 login() 成功后再获取数据")

        stock = StockDetail(code=symbol)
        return stock

    def logout(self):
        if self._is_connected:
            AmazingData.logout(self.user)
