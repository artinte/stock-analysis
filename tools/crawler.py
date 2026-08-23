import argparse
import asyncio
import os
from datetime import datetime
import sys

from crawler.core.browser import browser_manager
from crawler.pipelines.daily_content_summary import DailyContentSummaryPipeline
from crawler.pipelines.article_summary_xueqiu import ArticleGeneratePipeline
from crawler.pipelines.content_publisher import ContentPublisherPipeline
from crawler.pipelines.content_summary import ContentSummaryPipeline
from crawler.pipelines.deduplicate import DeduplicatePipeline
from crawler.pipelines.auto_comment_xueqiu import post_comment
from crawler.spiders.cctv_finance import CCTVFinanceSpider
from crawler.spiders.eastmoney_topic import EastMoneyTopicSpider
from crawler.spiders.mofcom_policy import MOFCOMPolicySpider
from crawler.spiders.sse_announcement import SseAnnouncementSpider
from crawler.spiders.sse_regular import SseRegularReportSpider
from crawler.spiders.sse_spider import SSESpider
from crawler.spiders.szse_fixed import SzseRegularReportSpider

# 1. 获取当前文件所在目录 (crawler) 和项目根目录 (stock-analysis)
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# # 2. 将它们都加入 sys.path，确保既能引用上一级，也能引用当前级下的文件夹
# for path in [CURRENT_DIR, PROJECT_ROOT]:
#     if path not in sys.path:
#         sys.path.insert(0, path)

from crawler.common.data_printer import print_fetched_articles, save_raw_articles_to_txt
from utils.stock_mapping import StockCodeConverter


async def run_spider(spider, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await spider.run()


# ==========================================
#  0. 爬虫注册与预设映射表
# ==========================================

SPIDER_REGISTRY = {
    "sse": SSESpider,
    "sse_announce": SseAnnouncementSpider,
    "sse_regular": SseRegularReportSpider,
    "szse_fixed": SzseRegularReportSpider,
    "cctv_finance": CCTVFinanceSpider,
    "eastmoney": EastMoneyTopicSpider,
    "mofcom": MOFCOMPolicySpider,
}

SPIDER_PRESETS = {
    "all": list(SPIDER_REGISTRY.keys()),
    "sse_all": ["sse", "sse_announce", "sse_regular"],
    # 抓取公司的季度报告
    "regular_reports": ["sse_regular", "szse_fixed"],
    "regular": ["sse_regular"],
    "daily_news": ["cctv_finance", "eastmoney"],
}


def get_selected_spiders(spider_args: list) -> list:
    """解析参数并动态实例化爬虫"""
    spider_keys = set()
    for item in spider_args:
        if item in SPIDER_PRESETS:
            spider_keys.update(SPIDER_PRESETS[item])
        elif item in SPIDER_REGISTRY:
            spider_keys.add(item)

    return [SPIDER_REGISTRY[key]() for key in spider_keys if key in SPIDER_REGISTRY]


# ==========================================
#  2. 任务管道 (Task Pipelines)
# ==========================================


async def task_crawl_and_comment(spiders: list = None, **kwargs):
    """通用爬取与评论任务 (爬取 -> 去重 -> 摘要 -> 评论)"""
    if not spiders:
        print("⚠️ 未提供爬虫实例，取消执行。")
        return

    await browser_manager.start()
    semaphore = asyncio.Semaphore(3)

    try:
        print("🚀 开始运行爬取与评论任务...\n")
        tasks = [run_spider(spider, semaphore) for spider in spiders]
        results = await asyncio.gather(*tasks)

        # 1. 压平数据
        raw_items = [item for sublist in results for item in sublist]

        # 2. 去重
        dedup_pipeline = DeduplicatePipeline()
        cleaned_items = dedup_pipeline.process(raw_items)

        total = len(cleaned_items)
        for idx, item in enumerate(cleaned_items, 1):
            company = item.related_companies[0] if item.related_companies else None
            xueqiu_url = (
                StockCodeConverter.get_xueqiu_url(company) if company else "N/A"
            )

            if not xueqiu_url or xueqiu_url == "N/A":
                print(
                    f"[{idx}/{total}] ⚠️ 无法识别公司 [{company}] 的股票代码，跳过发帖。"
                )
                continue

            # 3. 组装标题和链接为评论内容
            title = getattr(item, "title", "").strip()
            url = getattr(item, "url", "").strip()

            # 根据实际情况格式化文本（支持只有标题或只有链接的兜底）
            if title and url:
                comment_content = f"{title}\n{url}"
            elif title:
                comment_content = title
            elif url:
                comment_content = url
            else:
                comment_content = "关注后续动态。"

            print(f"\n[{idx}/{total}] 正在给 [{company}] 发帖: {xueqiu_url}")
            print(f"评论内容: {comment_content}")

            post_comment(xueqiu_url, comment_content)

    finally:
        await browser_manager.stop()


async def task_crawl_and_ai_analysis(spiders: list = None, **kwargs):
    """通用全流程 (爬取 -> 去重 -> 摘要 -> AI生成 -> 发布)"""
    if not spiders:
        print("⚠️ 未提供爬虫实例，取消执行。")
        return

    await browser_manager.start()
    semaphore = asyncio.Semaphore(3)

    try:
        print("🚀 开始运行全流程抓取与发布任务...\n")
        tasks = [run_spider(spider, semaphore) for spider in spiders]
        results = await asyncio.gather(*tasks)

        # 1. 压平数据
        raw_items = [item for sublist in results for item in sublist]
        print(f"✅ 共抓取到 {len(raw_items)} 条原生内容，准备进入去重与摘要阶段...")

        # 2. 去重
        dedup_pipeline = DeduplicatePipeline()
        cleaned_items = dedup_pipeline.process(raw_items)
        print(f"✅ 去重后剩余 {len(cleaned_items)} 条有效内容，准备进入摘要阶段...")

        # 3. 摘要
        summary_pipeline = ContentSummaryPipeline(model_name="qwen3:8b", concurrency_limit=5)
        target_news = await summary_pipeline.process_async(cleaned_items)

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


        pipeline = DailyContentSummaryPipeline(
            output_filename=f"ai_summary_output_{date_suffix}.txt",
            model_name="qwen3:8b",
        )

        daily_summary = pipeline.process(target_news)

        # 4. AI 生成与发布
        # ai_pipeline = ArticleGeneratePipeline(
        #     output_filename=
        #     model_name="qwen3:8b",
        # )
        # content_generated = ai_pipeline.process(target_news)
        # publisher = ContentPublisherPipeline()
        # publisher.publish(content_generated)

    finally:
        await browser_manager.stop()


async def task_crawl_only(spiders: list = None, **kwargs):
    """通用仅爬取任务 (爬取 -> 去重 -> 保存文本)"""
    if not spiders:
        print("⚠️ 未提供爬虫实例，取消执行。")
        return

    await browser_manager.start()
    semaphore = asyncio.Semaphore(3)

    try:
        print("🔍 开始仅爬取模式...\n")
        tasks = [run_spider(spider, semaphore) for spider in spiders]
        results = await asyncio.gather(*tasks)

        raw_items = [item for sublist in results for item in sublist]

        dedup_pipeline = DeduplicatePipeline()
        cleaned_items = dedup_pipeline.process(raw_items)

        print_fetched_articles(cleaned_items)

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        date_suffix = datetime.now().strftime("%Y%m%d")
        output_file = os.path.join(output_dir, f"crawl_only_{date_suffix}.txt")
        save_raw_articles_to_txt(
            cleaned_items, include_content=True, output_file=output_file
        )
        print(f"✅ 抓取完成，结果已保存至: {output_file}")

    finally:
        await browser_manager.stop()


async def task_sse_regular(spiders: list = None, **kwargs):
    """定向快捷任务：若外部未强制指定爬虫，默认绑定运行上交所定期报告"""
    target_spiders = spiders if spiders else get_selected_spiders(["regular"])
    await task_crawl_and_comment(spiders=target_spiders, **kwargs)


# ==========================================
#  3. 任务映射表 (TASK_MAP)
# ==========================================

TASK_MAP = {
    "ai_analysis": task_crawl_and_ai_analysis,
    "crawl_only": task_crawl_only,
    "sse_regular": task_sse_regular,  # 快捷任务模式
}


# ==========================================
#  4. 主入口函数
# ==========================================


async def main():
    parser = argparse.ArgumentParser(description="新闻/公告抓取与处理工作流系统")

    # 选择不同的爬虫
    parser.add_argument(
        "-s",
        "--spiders",
        nargs="+",
        default=["regular_reports"],
        help="选择爬虫或预设: regular, sse_all, all, cctv 等",
    )

    # 选择不同的任务模式
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="sse_regular",
        choices=list(TASK_MAP.keys()),
        help="任务模式: full(全流程), crawl_only(仅爬取), sse_regular(定向定期报告快捷模式), ai_analysis(AI分析模式)",
    )

    args = parser.parse_args()

    # 1. 获取选定的任务处理函数
    task_func = TASK_MAP.get(args.mode)

    if not task_func:
        print(f"❌ 未知的任务模式: {args.mode}")
        return

    # 2. 从映射表解析爬虫实例列表
    spiders_to_run = get_selected_spiders(args.spiders)

    if not spiders_to_run:
        print(f"❌ 未找到匹配的爬虫: {args.spiders}")
        return

    print(
        f"🎯 当前运行模式: [{args.mode}] | 目标爬虫: {[s.__class__.__name__ for s in spiders_to_run]}"
    )

    # 3. 统一将解析好的 spiders 作为参数传递给对应的任务函数
    await task_func(spiders=spiders_to_run)


if __name__ == "__main__":
    asyncio.run(main())
