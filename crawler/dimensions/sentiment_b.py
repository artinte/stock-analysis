import numpy as np
from core.base_spider import BaseSpider
import config


class SentimentSpider(BaseSpider):
    def run(self):
        print("🧠 [维度 B] 计算市场情绪极值...")
        # 模拟历史 30 天热度数据
        history_pv = [100, 105, 98, 110, 102, 350]  # 最后一项是突发数据
        mean = np.mean(history_pv[:-1])
        std = np.std(history_pv[:-1])
        latest = history_pv[-1]

        # 核心逻辑：3σ 研判
        is_overheat = latest > (mean + config.SENTIMENT_THRESHOLD_SIGMA * std)

        return {
            "dimension": "Sentiment",
            "status": "OVERHEAT" if is_overheat else "NORMAL",
            "deviation": (latest - mean) / std,
        }
