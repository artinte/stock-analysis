from dimensions.policy_a import PolicySpider
from dimensions.sentiment_b import SentimentSpider

# ... 导入其他维度


def generate_report():
    print("🚀 Sentinel-Scraper 情报工厂正在全量运行...\n")

    # 初始化各维度执行器
    factory_line = [
        PolicySpider(),
        SentimentSpider(),
        # MicroSpider(),
        # GlobalSpider()
    ]

    final_intelligence = {}

    for machine in factory_line:
        result = machine.run()
        final_intelligence[result["dimension"]] = result

    # 交叉验证逻辑示例
    print("=" * 40)
    print("📑 哨兵自动化研判总结报告")
    print("=" * 40)

    # 策略联动：政策强 + 情绪不热 = 绝佳买点
    p_stat = final_intelligence.get("Policy", {})
    s_stat = final_intelligence.get("Sentiment", {})

    if p_stat.get("signal") == "STRONG_BUY" and s_stat.get("status") == "NORMAL":
        print("✅ 结论：检测到‘政策超预期’且‘市场未察觉’，建议加仓。")
    elif s_stat.get("status") == "OVERHEAT":
        print("❌ 结论：情绪指标偏离均值 3σ，警惕诱多，建议减持。")
    else:
        print("⚖️ 结论：多空信号对冲，保持观望。")


if __name__ == "__main__":
    generate_report()
