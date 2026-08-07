import asyncio
import os
import requests
import subprocess
import time
from datetime import datetime
from core.browser import browser_manager
from spiders.sse_spider import SSESpider
from spiders.cctv_finance import CCTVFinanceSpider
from spiders.eastmoney_topic import EastMoneyTopicSpider
from spiders.mofcom_policy import MOFCOMPolicySpider
from pipelines.deduplicate import DeduplicatePipeline
from pipelines.article_summary import ArticleGeneratePipeline
from pipelines.content_summary import ContentSummaryPipeline
from pipelines.content_publisher import ContentPublisherPipeline

from utils.data_printer import print_fetched_articles, save_raw_articles_to_txt

SPIDERS = [
    SSESpider(),
    CCTVFinanceSpider(),
    EastMoneyTopicSpider(),
    MOFCOMPolicySpider(),
]


def start_ollama(timeout=30):
    url = "http://127.0.0.1:11434/api/tags"

    # 已启动
    try:
        requests.get(url, timeout=1)
        print("✅ Ollama 已启动")
        return True
    except requests.RequestException:
        pass

    print("🚀 正在启动 Ollama...")

    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("❌ 启动失败：未找到 'ollama' 命令，请确认 Ollama 已安装并加入 PATH。")
        return False
    except Exception as e:
        print(f"❌ 启动 Ollama 失败：{e}")
        return False

    # 等待服务启动
    for _ in range(timeout):
        try:
            requests.get(url, timeout=1)
            print("✅ Ollama 启动成功")
            return True
        except requests.RequestException:
            time.sleep(1)

    print("❌ Ollama 启动超时，请检查：")
    print("   1. Ollama 是否已正确安装")
    print("   2. 是否能在终端执行：ollama serve")
    print("   3. 11434 端口是否被占用")

    return False


async def run_spider(spider, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await spider.run()


async def main():
    start_ollama()  # 启动 Ollama 本地服务

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
        save_raw_articles_to_txt(target_news, output_file=output_file)
        
        # 生成
        ai_pipeline = ArticleGeneratePipeline(
            output_filename=f"local_output_{date_suffix}.txt"
        )
        content_generated = ai_pipeline.process(target_news)

        # 发布
        publisher = ContentPublisherPipeline()

        publisher.publish(content_generated)

    finally:
        await browser_manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
