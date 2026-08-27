import asyncio
import aiosqlite
from pipeline import DataPipeline
from base_storage import logger

# 本地 SQLite 配置
SQLITE_CONFIG = {
    "engine": "sqlite",
    "connection_string": "local_cache.db"
}

# 线上 MongoDB 配置
MONGO_CONFIG = {
    "engine": "mongodb",
    "uri": os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/"),
    "db_name": "crawler_platform"
}

# 核心开关：切换此处即可改变全盘存储策略
CURRENT_CONFIG = SQLITE_CONFIG

async def mock_spider(spider_id: int, pipeline: DataPipeline, total: int):
    for i in range(total):
        await pipeline.save_item("spider_results", {"spider_id": spider_id, "index": i, "payload": f"数据_{i}"})
        await asyncio.sleep(0.002)

async def init_db():
    if CURRENT_CONFIG["engine"] == "sqlite":
        async with aiosqlite.connect(CURRENT_CONFIG["connection_string"]) as conn:
            await conn.execute("CREATE TABLE IF NOT EXISTS spider_results (spider_id INT, [index] INT, payload TEXT)")
            await conn.commit()

async def main():
    await init_db()
    pipeline = DataPipeline(CURRENT_CONFIG, batch_size=50, flush_interval=1.0)
    await pipeline.start()

    logger.info(">>> 启动高并发爬虫写入测试...")
    await asyncio.gather(*[mock_spider(id, pipeline, 100) for id in range(3)])
    await pipeline.stop()

    logger.info("\n>>> 启动高并发与流式读取测试...")
    await pipeline.start() # 重新打开连接用于读取演示
    
    # 1. 测试并发条件读取
    res = await pipeline.get_items("spider_results", condition={"spider_id": 1}, limit=3)
    logger.info(f"[分页读取结果]: {res}")

    # 2. 测试流式大数据读取 (防 OOM 核心)
    async for batch in pipeline.stream_items("spider_results", batch_size=50):
        logger.info(f"[流式拉取成功] 本批次收到: {len(batch)} 条数据。")

    await pipeline.stop()

if __name__ == "__main__":
    asyncio.run(main())
