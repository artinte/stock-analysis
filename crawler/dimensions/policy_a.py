from core.base_spider import BaseSpider
from utils.nlp import score_text
import config


class PolicySpider(BaseSpider):
    def run(self):
        print("🏛️ [维度 A] 扫描政策库中...")
        # 模拟抓取政策标题
        titles = ["关于加快新质生产力发展的意见", "2026年制造业数字化转型补贴"]
        score = score_text(" ".join(titles), config.KEYWORDS_POLICY)

        return {
            "dimension": "Policy",
            "signal": "STRONG_BUY" if score > 5 else "NEUTRAL",
            "impact_score": score,
            "evidence": titles,
        }
