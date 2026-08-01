import asyncio
from core.browser import browser_manager
from pipelines.deduplicate import DeduplicatePipeline
from pipelines.summarizer import XueqiuArticlePipeline  # 导入管道
from spiders.cctv_finance import CCTVFinanceSpider
from spiders.eastmoney_topic import EastMoneyTopicSpider
from spiders.mofcom_policy import MOFCOMPolicySpider

SPIDERS = [
    CCTVFinanceSpider(),
    EastMoneyTopicSpider(),
    MOFCOMPolicySpider(),
]


async def run_spider(spider, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await spider.run()


async def main():
    await browser_manager.start()
    semaphore = asyncio.Semaphore(3)

    try:
        print("🚀 开始并行抓取任务...\n")
        tasks = [run_spider(spider, semaphore) for spider in SPIDERS]
        results = await asyncio.gather(*tasks)

        # 1. 压平抓取结果
        raw_items = [item for sublist in results for item in sublist]

        # 2. 管道 1：去重清洗
        dedup_pipeline = DeduplicatePipeline()
        cleaned_items = dedup_pipeline.process(raw_items)

        print(
            f"\n🎉 抓取与清洗完成！共获取 {len(cleaned_items)} 条有效数据（原始 {len(raw_items)} 条）\n"
        )

        # 3. 管道 2：可筛选特定来源（如商务部），或直接全量丢给 AI 总结
        # mofcom_news = [
        #     item for item in cleaned_items if item.source_name == "商务部官网"
        # ]

        # 如果抓到了商务部政策就只分析商务部，没有的话用全量新闻，避免打空包
        # target_news = mofcom_news if mofcom_news else cleaned_items
        target_news = cleaned_items
        ai_pipeline = XueqiuArticlePipeline(
            output_filename="xueqiu_local_output.txt"
        )
        ai_pipeline.process(target_news)

    finally:
        await browser_manager.stop()


if __name__ == "__main__":
    asyncio.run(main())