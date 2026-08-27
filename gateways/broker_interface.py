from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger("trading_system")

class BaseBroker(ABC):
    """交易提供方抽象基类。后续接入新券商只需继承并实现这两个方法。"""
    @abstractmethod
    async def place_order(self, symbol: str, action: str, order_type: str, quantity: float, price: float = None) -> Dict[str, Any]:
        """向券商下单"""
        pass

    @abstractmethod
    async def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        """获取券商侧最新的订单状态"""
        pass

# --- 模拟券商实现 (Mock Broker) ---
class MockBroker(BaseBroker):
    async def place_order(self, symbol: str, action: str, order_type: str, quantity: float, price: float = None) -> Dict[str, Any]:
        logger.info(f"[Broker] 向模拟柜台投递订单: {action} {quantity} 股 {symbol}")
        # 模拟券商返回的标准网关响应
        return {
            "broker_order_id": f"BRK_{int(asyncio.get_event_loop().time() * 1000)}",
            "status": "FILLED",  # 商业环境通常先是 PENDING/SUBMITTED，此处模拟直接成交
            "executed_price": price or 150.0,
            "executed_quantity": quantity,
            "fee": 1.5  # 模拟佣金
        }

    async def get_order_status(self, broker_order_id: str) -> Dict[str, Any]:
        return {"broker_order_id": broker_order_id, "status": "FILLED"}

# --- 券商工厂 (Broker Factory) ---
class BrokerFactory:
    @staticmethod
    def get_broker(provider_name: str, config: Dict[str, Any]) -> BaseBroker:
        if provider_name.lower() in ["mock", "webull", "futu"]:
            return MockBroker()  # MVP 阶段统一指向 Mock，后续在这里扩展：return WebullBroker(config)
        else:
            raise ValueError(f"未知的交易提供方: {provider_name}")
