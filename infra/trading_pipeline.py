import asyncio
import time
from typing import Dict, Any, List
from base_storage import BaseStorage, logger
from rel_storage import RelationalStorage
from broker_interface import BrokerFactory

class TradingPipeline:
    def __init__(self, db_config: Dict[str, Any], broker_config: Dict[str, Any]):
        # 初始化底层异步存储器（沿用前面的架构设计）
        self.storage = RelationalStorage(db_config["engine"], db_config["connection_string"])
        # 初始化底层券商网关
        self.broker = BrokerFactory.get_broker(broker_config["active_provider"], broker_config)
        
        self.queue = asyncio.Queue(maxsize=5000)
        self.is_running = False
        self.consumer_task = None

    async def start(self):
        await self.storage.connect()
        self.is_running = True
        self.consumer_task = asyncio.create_task(self._db_consumer_loop())
        logger.info("交易订单存储管道启动成功。")

    # ------------------ 核心业务：下单、高并发异步入库 ------------------
    async def execute_and_record_order(self, symbol: str, action: str, quantity: float, price: float) -> Dict[str, Any]:
        """
        面向策略端的标准下单 API。
        执行流程：1. 异步请求券商柜台 -> 2. 拿到结果立即返回策略 -> 3. 订单流水异步推入入库队列（流量削峰，不阻塞主交易线程）
        """
        # 1. 投递到券商
        broker_res = await self.broker.place_order(symbol, action, "LIMIT", quantity, price)
        
        # 2. 构造标准订单数据模型 (您的 Model 后续可以在这里校验/反序列化)
        order_record = {
            "order_id": f"ORD_{int(time.time() * 1000)}",
            "broker_order_id": broker_res["broker_order_id"],
            "symbol": symbol.upper(),
            "action": action.upper(),
            "quantity": broker_res["executed_quantity"],
            "price": broker_res["executed_price"],
            "fee": broker_res["fee"],
            "status": broker_res["status"],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        }

        # 3. 异步推入队列，由后台消费者批量写入 DB
        await self.queue.put(("orders", order_record))
        return order_record

    async def _db_consumer_loop(self):
        """后台攒批写入循环（商业化高并发降压核心）"""
        while self.is_running or not self.queue.empty():
            batch_orders = []
            start_time = asyncio.get_event_loop().time()
            
            while len(batch_orders) < 20: # 每凑满20笔订单或过去0.5秒就批量刷入数据库
                rem = 0.5 - (asyncio.get_event_loop().time() - start_time)
                if rem <= 0: break
                try:
                    _, item = await asyncio.wait_for(self.queue.get(), timeout=max(0.05, rem))
                    batch_orders.append(item)
                    self.queue.task_done()
                except asyncio.TimeoutError: break
            
            if batch_orders:
                await self.storage.save_batch("orders", batch_orders)

    # ------------------ 核心业务：订单拉取 ------------------
    async def get_symbol_orders(self, symbol: str) -> List[Dict[str, Any]]:
        """获取指定标的的所有历史订单（用于盈亏计算）"""
        return await self.storage.query_batch("orders", condition={"symbol": symbol.upper()}, limit=1000)

    async def stop(self):
        self.is_running = False
        if self.consumer_task: await self.consumer_task
        await self.storage.close()
        logger.info("交易系统安全停止。")
