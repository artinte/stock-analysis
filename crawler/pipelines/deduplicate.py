from typing import List
from core.models import ArticleItem


class DeduplicatePipeline:
    """去重管道：基于 [来源+标题] 进行全局内存去重"""

    def process(self, items: List[ArticleItem]) -> List[ArticleItem]:
        seen_keys = set()
        unique_items = []

        for item in items:
            unique_key = f"{item.source_name}_{item.title}"
            if unique_key not in seen_keys:
                seen_keys.add(unique_key)
                unique_items.append(item)

        return unique_items