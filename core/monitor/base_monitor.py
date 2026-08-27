import logging
from abc import ABC, abstractmethod
from typing import Any

# 统一日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("MonitorEngine")

class MonitorTask(ABC):
    """
    监控任务抽象基类。
    商业化设计：一个完整的监控生命周期 = 抓取数据 -> 检查条件 -> 执行动作。
    """
    def __init__(self, name: str, interval: float):
        self.name = name          # 任务名称
        self.interval = interval  # 监控间隔时间（秒）

    @abstractmethod
    async def fetch(self) -> Any:
        """
        1. 怎么监控：去哪里拿数据。
        例如：请求 X.com API、读取本地报告、抓取网页等。
        """
        pass

    @abstractmethod
    async def check_trigger(self, data: Any) -> bool:
        """
        2. 条件是什么：判断是否触发。
        传入 fetch 拿到的数据，返回 True（触发）或 False（未触发）。
        """
        pass

    @abstractmethod
    async def execute_action(self, data: Any):
        """
        3. 触发后干什么：执行相应操作。
        例如：调用您之前的交易系统下单、发送报警、写入数据库。
        """
        pass
