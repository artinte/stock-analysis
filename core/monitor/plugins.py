import asyncio
import random
from core.monitor.base_monitor import MonitorTask, logger

class XMonitorPlugin(MonitorTask):
    """插件 A：假装这是一个 X.com 监控器"""
    async def fetch(self) -> str:
        # 实际商业开发中，这里是 aiohttp.get("https://x.com...")
        await asyncio.sleep(0.1) # 模拟网络请求耗时
        mock_tweets = ["正常推文", "包含敏感词的推文", "日常打卡"]
        return random.choice(mock_tweets)

    async def check_trigger(self, data: str) -> bool:
        # 具体条件解耦在这里：比如推文里包含某个马斯克的关键词
        return "敏感词" in data

    async def execute_action(self, data: str):
        # 具体动作解耦在这里：比如对接您前面的交易系统
        logger.info(f"▶️ [X.com 联动] 检测到敏感推文: '{data}' -> 正在联动交易系统买入 Stock！")


class ReportMonitorPlugin(MonitorTask):
    """插件 B：假装这是一个研报/财报 PDF 监控器"""
    async def fetch(self) -> float:
        # 实际开发中，这里是读取某个云盘或邮件里的新报告
        await asyncio.sleep(0.2)
        return random.uniform(10.0, 15.0)  # 模拟解析出的某个财务指标

    async def check_trigger(self, data: float) -> bool:
        # 条件解耦：指标超过 14 就拉警报
        return data > 14.0

    async def execute_action(self, data: float):
        # 动作解耦：发短信、发邮件、或者写入监控日志
        logger.info(f"▶️ [报告联动] 发现财务指标异常: {data:.2f} -> 正在向风控部门推送飞书报警！")
