import asyncio
from typing import Dict, Any, List, AsyncGenerator
from base_storage import BaseStorage, logger
from mongo_storage import MongoStorage
from rel_storage import RelationalStorage

class DataPipeline:
    def __init__(self, config: Dict[str, Any], batch_size: int = 50, flush_interval: float = 1.0):
        engine = config.get("engine", "sqlite").lower()
        if engine == "mongodb":
            self.storage = MongoStorage(uri=config["uri"], db_name=config["db_name"])
        else:
            self.storage = RelationalStorage(db_type=engine, connection_string=config["connection_string"])
        
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue = asyncio.Queue(maxsize=10000)
        self.consumer_task = None
        self.is_running = False

    async def start(self):
        await self.storage.connect()
        self.is_running = True
        self.consumer_task = asyncio.create_task(self._consume_loop())

    async def save_item(self, table_or_collection: str, item: Dict[str, Any]):
        await self.queue.put((table_or_collection, item))

    async def _consume_loop(self):
        while self.is_running or not self.queue.empty():
            batch_data = {}
            start_time = asyncio.get_event_loop().time()
            count = 0
            while count < self.batch_size:
                rem = self.flush_interval - (asyncio.get_event_loop().time() - start_time)
                if rem <= 0: break
                try:
                    target, item = await asyncio.wait_for(self.queue.get(), timeout=max(0.1, rem))
                    batch_data.setdefault(target, []).append(item)
                    count += 1
                    self.queue.task_done()
                except asyncio.TimeoutError: break
            for target, items in batch_data.items():
                if items: await self.storage.save_batch(target, items)

    async def get_items(self, table: str, condition: Dict[str, Any] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return await self.storage.query_batch(table, condition or {}, limit, offset)

    async def stream_items(self, table: str, condition: Dict[str, Any] = None, batch_size: int = 100) -> AsyncGenerator[List[Dict[str, Any]], None]:
        async for batch in self.storage.query_stream(table, condition or {}, batch_size): yield batch

    async def stop(self):
        self.is_running = False
        if self.consumer_task: await self.consumer_task
        await self.storage.close()
        logger.info("数据管道已安全停止。")
