from enum import Enum

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"

class StockOrderModel:
    def __init__(self, order_id: str, symbol: str, side: OrderSide, price: float, 
                 quantity: int, filled_quantity: int, filled_avg_price: float, status: OrderStatus):
        # 8个内部变量定义
        self.order_id = order_id                  # 订单唯一标识符
        self.symbol = symbol                      # 股票代码
        self.side = side                          # 交易方向（买入/卖出）
        self.price = price                        # 委托限制价格
        self.quantity = quantity                  # 计划委托的总股数
        self.filled_quantity = filled_quantity    # 目前已经成交的股数
        self.filled_avg_price = filled_avg_price  # 已成交股数的平均价格
        self.status = status                      # 订单当前所处的生命周期状态

    def display(self):
        """
        直接打印当前模型内部变量状态的展示函数
        """
        print(f"--- Stock Order Snapshot ---")
        print(f"order_id:         {self.order_id}")
        print(f"symbol:           {self.symbol}")
        print(f"side:             {self.side.value}")
        print(f"price:            {self.price}")
        print(f"quantity:         {self.quantity}")
        print(f"filled_quantity:  {self.filled_quantity}")
        print(f"filled_avg_price: {self.filled_avg_price}")
        print(f"status:           {self.status.value}")
        print(f"----------------------------")
