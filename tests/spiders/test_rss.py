import asyncio

from crawler.config.rss_feeds import (
    get_enabled_feeds,
)

from crawler.core.browser import (
    browser_manager,
)

from crawler.spiders.rss.manager import (
    RSSFeedManager,
)


async def main():

    feeds = get_enabled_feeds()

    print()
    print(
        f"RSS 数据源: {len(feeds)} 个"
    )
    print()

    manager = RSSFeedManager(
        feeds=feeds,
        concurrency=4,
    )

    await browser_manager.start()

    try:

        async def page_factory():
            return await browser_manager.new_page()

        items, results = await manager.run(
            page_factory
        )

        print()
        print("RSS 抓取完成")
        print()

        success_count = 0
        failed_count = 0

        for result in results:

            if result.success:
                success_count += 1

                print(
                    f"✓ {result.name:<20}"
                    f"{len(result.items):>4} 条 "
                    f"{result.elapsed:>6.2f}s"
                )

            else:
                failed_count += 1

                print(
                    f"✗ {result.name:<20}"
                    f"失败 "
                    f"{result.elapsed:>6.2f}s"
                )

                if result.error:
                    print(
                        f"    {result.error}"
                    )

        print()
        print(
            f"成功: {success_count}  "
            f"失败: {failed_count}"
        )
        print(
            f"新闻总数: {len(items)}"
        )

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

            print()

    finally:

        await browser_manager.stop()


if __name__ == "__main__":
    asyncio.run(main())

