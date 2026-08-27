class MongoStorage(BaseStorage):
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    async def connect(self):
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.db_name]
            logger.info("成功连接到线上/本地 MongoDB 数据库。")
        except ImportError:
            logger.error("未检测到 motor 库，请执行: pip install motor")
            raise

    async def save_batch(self, collection: str, items: List[Dict[str, Any]]):
        if not items: return
        try:
            # 商业化高并发核心：Bulk Write 批量写入，极大提升吞吐量
            await self.db[collection].insert_many(items)
            logger.info(f"[Mongo] 成功批量插入 {len(items)} 条数据至集合: {collection}")
        except Exception as e:
            logger.error(f"[Mongo] 批量插入失败: {e}")

    async def query_batch(self, collection: str, condition: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            cursor = self.db[collection].find(condition).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            for doc in results:
                if "_id" in doc: doc["_id"] = str(doc["_id"])  # 序列化友好
            return results
        except Exception as e:
            logger.error(f"[Mongo] 分页读取失败: {e}")
            return []

    async def query_stream(self, collection: str, condition: Dict[str, Any], batch_size: int = 100) -> AsyncGenerator[List[Dict[str, Any]], None]:
        try:
            cursor = self.db[collection].find(condition)
            batch = []
            async for doc in cursor:
                if "_id" in doc: doc["_id"] = str(doc["_id"])
                batch.append(doc)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch
        except Exception as e:
            logger.error(f"[Mongo] 流式读取失败: {e}")


    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB 连接已安全关闭。")
