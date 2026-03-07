# 全局配置
KEYWORDS_POLICY = ["新质生产力", "半导体", "低空经济", "反垄断"]
SENTIMENT_THRESHOLD_SIGMA = 3.0  # 情绪过热触发阈值
DB_PATH = "./intelligence_factory.db"

# 目标源列表
URL_MAP = {
    "GOV_POLICY": "http://example-gov.cn/zhengce",
    "SOCIAL_SENTIMENT": "http://example-social.com/hot-rank",
    "BIDDING_PLATFORM": "http://example-bidding.com/api",
}
