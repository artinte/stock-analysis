import os
from typing import List, Any


def print_fetched_articles(
    articles: List[Any], max_content_len: int = 500, include_content: bool = False
) -> None:
    """
    格式化打印爬虫抓取到的原生数据（控制台预览）

    :param articles: 抓取到的 ArticleItem 列表
    :param max_content_len: 正文打印的最大字符数，默认 500 字
    """
    total = len(articles)
    print("\n" + "=" * 35 + f" 📊 共抓取到 {total} 条原生内容 " + "=" * 35 + "\n")

    if total == 0:
        print("⚠️ 未抓取到任何有效文章内容，请检查爬虫 URL、选择器或网络连接！\n")
        print("=" * 90 + "\n")
        return

    for idx, item in enumerate(articles, 1):
        # 兼容 dict 和 Pydantic / dataclass 对象
        if isinstance(item, dict):
            source = item.get("source_name", "未知来源")
            category = item.get("category", "")
            title = item.get("title", "无标题")
            url = item.get("url", "无链接")
            summary = item.get("summary", "")
            content = item.get("content", "")
            fetched_at = item.get("fetched_at", "")
        else:
            source = getattr(item, "source_name", "未知来源")
            category = getattr(item, "category", "")
            title = getattr(item, "title", "无标题")
            url = getattr(item, "url", "无链接")
            summary = getattr(item, "summary", "")
            if include_content:
                content = getattr(item, "content", "")
            else:
                content = ""
            fetched_at = getattr(item, "fetched_at", "")

        # 格式化分类与时间显示
        cat_info = f" [{category}]" if category else ""
        time_str = (
            fetched_at.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(fetched_at, "strftime")
            else str(fetched_at)
        )

        # 确定主内容显示：优先显示正文，若正文为空则显示摘要
        main_text = (
            content.strip()
            if content
            else (summary.strip() if summary else "（无正文及摘要）")
        )
        if len(main_text) > max_content_len:
            main_text = main_text[:max_content_len] + "... (后略)"

        print(f"[{idx}/{total}] 来源: {source}{cat_info} | 抓取时间: {time_str}")
        print(f"📌 标题: {title}")
        print(f"🔗 链接: {url}")
        if summary and content:
            print(f"💡 摘要: {summary.strip()}")
        print(f"📝 正文/内容:\n{main_text}")

        # 每一个内容之间空一行
        print("\n" + "-" * 80 + "\n")


def save_raw_articles_to_txt(
    articles: List[Any],
    include_content: bool = False,
    output_file: str = "output/raw_fetched_articles.txt",
) -> None:
    """
    同步将抓取到的内容带空行写入本地 txt 文件，方便离线查看
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(
            f"==================== 📊 共抓取到 {len(articles)} 条原生内容 ====================\n\n"
        )
        for idx, item in enumerate(articles, 1):
            if isinstance(item, dict):
                source = item.get("source_name", "未知来源")
                category = item.get("category", "")
                title = item.get("title", "无标题")
                url = item.get("url", "无链接")
                summary = item.get("summary", "")
                content = item.get("content", "")
                fetched_at = item.get("fetched_at", "")
            else:
                source = getattr(item, "source_name", "未知来源")
                category = getattr(item, "category", "")
                title = getattr(item, "title", "无标题")
                url = getattr(item, "url", "无链接")
                summary = getattr(item, "summary", "")
                content = getattr(item, "content", "")
                fetched_at = getattr(item, "fetched_at", "")

            cat_info = f" [{category}]" if category else ""
            time_str = (
                fetched_at.strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(fetched_at, "strftime")
                else str(fetched_at)
            )

            f.write(f"[{idx}] 来源: {source}{cat_info} | 抓取时间: {time_str}\n")
            f.write(f"📌 标题: {title}\n")
            f.write(f"🔗 链接: {url}\n")
            if summary:
                f.write(f"💡 摘要: {summary.strip()}\n")
            if include_content and content:
                f.write(
                    f"📝 正文/内容:\n{content.strip() if content else '（无正文）'}\n"
                )
            f.write("\n" + "-" * 80 + "\n\n")

    print(f"💾 原生抓取结果已同步保存至: {output_file}")
