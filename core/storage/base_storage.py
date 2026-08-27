class BaseStorage(ABC):
    @abstractmethod
    async def connect(self):
        """初始化数据库连接或连接池"""
        pass

    @abstractmethod
    async def save_batch(self, table_or_collection: str, items: List[Dict[str, Any]]):
        """批量保存数据 (写入优化)"""
        pass

    @abstractmethod
    async def query_batch(self, table_or_collection: str, condition: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """并发安全的分页查询 (读取优化)"""
        pass

    @abstractmethod
    async def query_stream(self, table_or_collection: str, condition: Dict[str, Any], batch_size: int = 100) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """流式读取生成器 (防内存溢出标配)"""
        pass

    @abstractmethod
    async def close(self):
        """安全关闭数据库连接"""
        pass
