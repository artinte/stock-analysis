import asyncio
import os
from datetime import datetime, timedelta
from core.browser import browser_manager
from manager.ollama_manager import OllamaStatus, start_ollama
from spiders.sse_spider import SSESpider
from spiders.sse_announcement import SseAnnouncementSpider
from spiders.sse_regular import SseRegularReportSpider
from spiders.cctv_finance import CCTVFinanceSpider
from spiders.eastmoney_topic import EastMoneyTopicSpider
from spiders.mofcom_policy import MOFCOMPolicySpider
from pipelines.deduplicate import DeduplicatePipeline
from pipelines.article_summary import ArticleGeneratePipeline
from pipelines.content_summary import ContentSummaryPipeline
from pipelines.content_publisher import ContentPublisherPipeline

from utils.data_printer import print_fetched_articles, save_raw_articles_to_txt

SPIDERS = [
    # SSESpider(),
    # SseAnnouncementSpider(),
    SseRegularReportSpider(),
    # CCTVFinanceSpider(),
    # EastMoneyTopicSpider(),
    # MOFCOMPolicySpider(),
]


async def run_spider(spider, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await spider.run()


async def main():
    model_to_use = None
    status, models = start_ollama()

    match status:
        case OllamaStatus.SUCCESS:
            print(f"✅ Ollama 就绪，可用模型: {models}")
            model_to_use = models[0]  # 默认使用第一个模型

        case OllamaStatus.NO_MODELS:
            print("⚠️ Ollama 已启动，但没有下载任何模型。")
            print(
                "💡 程序切换为降级模式（如使用规则匹配、API 服务或跳过 AI 增强功能）..."
            )
            # 继续跑后面的程序...

        case OllamaStatus.NOT_INSTALLED:
            print("❌ 未安装 Ollama。")
            print("💡 跳过 Ollama 相关逻辑，继续运行后续程序...")
            # 继续跑后面的程序...

        case OllamaStatus.START_FAILED:
            print("❌ Ollama 启动超时。")
            print("💡 切换备用逻辑并继续执行后续程序...")
            # 继续跑后面的程序...

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

        # 3. 管道 2：可筛选特定来源（如商务部），或直接全量丢给 AI 总结
        # mofcom_news = [
        #     item for item in cleaned_items if item.source_name == "商务部官网"
        # ]

        # 如果抓到了商务部政策就只分析商务部，没有的话用全量新闻，避免打空包
        # target_news = mofcom_news if mofcom_news else cleaned_items
        target_news = cleaned_items

        summary_pipeline = ContentSummaryPipeline(
            concurrency_limit=5
        )  # 设置并发限制为 5
        target_news = await summary_pipeline.process_async(target_news)

        print_fetched_articles(target_news)

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        date_suffix = datetime.now().strftime("%Y%m%d")
        output_file = os.path.join(
            output_dir, f"raw_fetched_articles_{date_suffix}.txt"
        )
        save_raw_articles_to_txt(
            target_news, include_content=False, output_file=output_file
        )

        # 生成
        ai_pipeline = ArticleGeneratePipeline(
            output_filename=f"local_output_{date_suffix}.txt",
            model_name=model_to_use,
        )
        content_generated = ai_pipeline.process(target_news)

        # 发布
        publisher = ContentPublisherPipeline()

        publisher.publish(content_generated)

    finally:
        await browser_manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
