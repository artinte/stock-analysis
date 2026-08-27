from typing import Dict, Any, List, AsyncGenerator
from base_storage import BaseStorage, logger
import aiosqlite

class RelationalStorage(BaseStorage):
    def __init__(self, db_type: str, connection_string: str):
        self.db_type = db_type.lower()
        self.conn_string = connection_string
        self.pool = None

    async def connect(self):
        if self.db_type == 'sqlite':
            self.pool = await aiosqlite.connect(self.conn_string)
            logger.info("已连接至本地 SQLite 数据库。")

    async def save_batch(self, table: str, items: List[Dict[str, Any]]):
        if not items: return
        columns = ", ".join(items[0].keys())
        placeholders = ", ".join([f":{k}" for k in items[0].keys()])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        await self.pool.executemany(sql, items)
        await self.pool.commit()
        logger.info(f"[SQLite] 批量写入 {len(items)} 条数据。")

    async def query_batch(self, table: str, condition: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        where = " AND ".join([f"[{k}] = :{k}" for k in condition.keys()]) if condition else "1=1"
        sql = f"SELECT * FROM {table} WHERE {where} LIMIT :limit OFFSET :offset"
        params = {**condition, "limit": limit, "offset": offset}
        self.pool.row_factory = aiosqlite.Row
        async with self.pool.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def query_stream(self, table: str, condition: Dict[str, Any], batch_size: int = 100) -> AsyncGenerator[List[Dict[str, Any]], None]:
        where = " AND ".join([f"[{k}] = :{k}" for k in condition.keys()]) if condition else "1=1"
        sql = f"SELECT * FROM {table} WHERE {where}"
        self.pool.row_factory = aiosqlite.Row
        async with self.pool.execute(sql, condition) as cursor:
            while True:
                rows = await cursor.fetchmany(batch_size)
                if not rows: break
                yield [dict(row) for row in rows]

    async def close(self):
        if self.pool: await self.pool.close()
