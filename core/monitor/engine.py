import asyncio
from typing import List
from core.monitor.base_monitor import MonitorTask, logger

class ConcurrentMonitorEngine:
    def __init__(self):
        self.tasks: List[MonitorTask] = []
        self._running_tasks = []
        self.is_running = False

    def register_task(self, task: MonitorTask):
        """注册监控任务（支持动态添加）"""
        self.tasks.append(task)
        logger.info(f"成功注册监控任务: [{task.name}]，监控频率: {task.interval}s")

    async def _run_task_loop(self, task: MonitorTask):
        """单个任务的独立生存时间循环（并发核心）"""
        logger.info(f"任务后台循环启动: [{task.name}]")
        while self.is_running:
            start_time = asyncio.get_event_loop().time()
            try:
                # 1. 执行抓取
                data = await task.fetch()
                
                # 2. 检查条件
                if await task.check_trigger(data):
                    logger.warning(f"🚨 任务 [{task.name}] 满足触发条件！正在调度执行 Action...")
                    # 3. 异步执行动作（不阻塞当前的下一次监控）
                    asyncio.create_task(task.execute_action(data))
                
            except Exception as e:
                logger.error(f"❌ 任务 [{task.name}] 运行期异常: {e}", exc_info=True)
            
            # 精准控制间隔时间，扣除代码执行耗时，防止时间漂移
            elapsed = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0.1, task.interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def start(self):
        """启动所有并发监控任务"""
        self.is_running = True
        logger.info(">>> 正在启动高并发监控引擎...")
        
        # 为每个任务创建一个独立的 asyncio 协程，实现并行监控
        self._running_tasks = [
            asyncio.create_task(self._run_task_loop(task)) for task in self.tasks
        ]
        # 使用 gather 让它们在后台并发运行
        await asyncio.gather(*self._running_tasks, return_exceptions=True)

    async def stop(self):
        """优雅关闭引擎，确保当前正在执行的 Action 不会断电丢失"""
        logger.info(">>> 正在接收停止指令，正在优雅关闭监控引擎...")
        self.is_running = False
        for t in self._running_tasks:
            t.cancel()
        logger.info(">>> 监控引擎已安全停止。")
