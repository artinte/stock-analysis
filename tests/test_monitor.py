import asyncio
from engine import ConcurrentMonitorEngine
from plugins import XMonitorPlugin, ReportMonitorPlugin

async def main():
    # 1. 初始化并发引擎
    engine = ConcurrentMonitorEngine()

    # 2. 实例化各种具体的监控任务（彼此完全独立，解耦）
    # 任务一：监控 X.com，每 1.5 秒扫一次
    x_task = XMonitorPlugin(name="X_Stream_Monitor", interval=1.5)
    
    # 任务二：监控财务报告，每 3 秒扫一次
    report_task = ReportMonitorPlugin(name="Financial_Report_Monitor", interval=3.0)

    # 3. 将任务注册进引擎
    engine.register_task(x_task)
    engine.register_task(report_task)

    # 4. 启动引擎（主线程会卡在这里并发运行后台的所有监控）
    # 商业化生产环境一般会用 asyncio.create_task 跑，并配合信号捕获优雅退出
    try:
        # 模拟让它高并发跑 10 秒钟，然后自动停掉
        asyncio.create_task(engine.start())
        await asyncio.sleep(10.0) 
    finally:
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())
