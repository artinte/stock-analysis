import asyncio

from core.monitor.engine import ConcurrentMonitorEngine
from core.monitor.plugins import XMonitorPlugin, ReportMonitorPlugin


async def main():
    engine = ConcurrentMonitorEngine()

    engine.register_task(
        XMonitorPlugin(
            name="X_Stream_Monitor",
            interval=1.5,
        )
    )

    engine.register_task(
        ReportMonitorPlugin(
            name="Financial_Report_Monitor",
            interval=3.0,
        )
    )

    print("监控引擎启动...")
    print("按 Ctrl+C 停止程序")

    try:
        await engine.start()

    finally:
        print("\n正在停止监控引擎...")
        await engine.stop()
        print("监控引擎已停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
