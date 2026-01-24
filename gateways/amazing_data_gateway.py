from gateways.broker_gateway import BrokerGateway
from stock_detail import StockDetail
import AmazingData


class AmazingDataGateway(BrokerGateway):
    def __init__(self):
        self._is_connected = False
        self._user = ""
        self._host = ""
        self._port = 0

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
            self._is_connected = True
            return True
        except ValueError:
            print("[错误] 端口格式无效，请检查配置。")
            return False
        except Exception as e:
            print(f"[错误] 登录异常: {e}")
            return False

    def fetch_market_data(self, symbol):
        if not self._is_connected:
            raise ConnectionError("请先执行 login() 成功后再获取数据")

        stock = StockDetail(code=symbol)

        return stock

    def logout(self):
        if self._is_connected:
            AmazingData.logout(self.user)
