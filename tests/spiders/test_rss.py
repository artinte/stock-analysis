from __future__ import annotations

import asyncio

from crawler.config.rss_feeds import get_enabled_feeds
from crawler.spiders.rss.rss_manager import RSSFeedManager


async def main():

    # ============================================================
    # RSS 数据源
    # ============================================================

    feeds = get_enabled_feeds()

    print()
    print(
        f"RSS 数据源: {len(feeds)} 个"
    )
    print()

    # ============================================================
    # RSS Manager
    # ============================================================

    manager = RSSFeedManager(
        feeds=feeds,
        concurrency=4,
        retries=3,
    )

    # ============================================================
    # 开始抓取
    # ============================================================

    items, results = await manager.run()

    # ============================================================
    # 抓取结果
    # ============================================================

    print()
    print("RSS 抓取完成")
    print()

    success_count = sum(
        1
        for result in results
        if result.success
    )

    failed_count = (
        len(results)
        - success_count
    )

    # ============================================================
    # 数据源结果
    # ============================================================

    for result in results:

        if result.success:

            print(
                f"✓ {result.name:<20}"
                f"{len(result.items):>4} 条 "
                f"{result.elapsed:>6.2f}s"
            )

        else:

            print(
                f"✗ {result.name:<20}"
                f"失败 "
                f"{result.elapsed:>6.2f}s"
            )

            if result.error:

                print(
                    f"    {result.error}"
                )

    # ============================================================
    # 汇总
    # ============================================================

    print()
    print(
        f"成功: {success_count}  "
        f"失败: {failed_count}"
    )

    print(
        f"新闻总数: {len(items)}"
    )

    # ============================================================
    # 新闻预览
    # ============================================================

    if not items:

        print()
        print("没有获取到新闻")
        return

    print()
    print("新闻预览")
    print("-" * 70)

    for i, item in enumerate(
        items[:20],
        1,
    ):

        print(
            f"{i}. {item.title}"
        )

        print(
            f"   来源: "
            f"{item.source_name}"
        )

        print(
            f"   时间: "
            f"{item.published_at}"
        )

        print(
            f"   分类: "
            f"{item.category}"
        )

        print(
            f"   URL: "
            f"{item.url}"
        )

        if item.summary:

            print(
                f"   摘要: "
                f"{item.summary}"
            )

        print()


if __name__ == "__main__":
    asyncio.run(main())

