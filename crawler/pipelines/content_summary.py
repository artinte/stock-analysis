import asyncio
from typing import Any, List


class ContentSummaryPipeline:
    """文章内容提炼/生成摘要 Pipeline
    专门用于为单条新闻/文章的 content 字段生成精炼 summary 字段
    """

    def __init__(self, concurrency_limit: int = 5):
        """初始化 Pipeline
        :param concurrency_limit: AI API 调用的最大并发数，防止触发 Rate Limit
        """
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def _call_ai_model(self, content: str) -> str:
        """调用 AI 模型生成摘要的具体逻辑
        替换为你实际使用的 AI SDK（如 OpenAI, DashScope, ZhiPu 等）
        """
        if not content or not content.strip():
            return "（文本为空，无法生成摘要）"

        # 示例：使用 AsyncOpenAI 异步客户端
        # client = AsyncOpenAI(api_key="your_api_key")
        # response = await client.chat.completions.create(
        #     model="gpt-4o-mini",  # 选择合适高效的模型
        #     messages=[
        #         {"role": "system", "content": "你是一个精炼的新闻摘要助手。请将以下内容精炼总结为100字以内的摘要。"},
        #         {"role": "user", "content": content[:3000]}  # 截断避免超出 Token 限制
        #     ],
        #     max_tokens=200
        # )
        # return response.choices[0].message.content.strip()

        # 模拟 AI 异步调用延迟（实际对接 API 时请删掉这两行并解开上方注释）
        await asyncio.sleep(0.5)
        return f"【AI摘要】: {content[:50]}..."

    async def _process_single_item(self, item: Any) -> Any:
        """单个 Item 的处理逻辑（带信号量控制并发）"""
        async with self.semaphore:
            # 已存在摘要，直接跳过 AI
            existing_summary = (
                item.get("summary")
                if isinstance(item, dict)
                else getattr(item, "summary", None)
            )

            if existing_summary:
                return item

            # 兼容 dict 和 对象 两种数据类型获取 content
            content = getattr(item, "content", None) or (
                item.get("content") if isinstance(item, dict) else ""
            )

            try:
                summary = await self._call_ai_model(content)
            except Exception as e:
                print(f"⚠️ ContentSummaryPipeline 提取摘要失败: {e}")
                summary = "（摘要生成失败）"

            # 将 summary 结果写回 item
            if isinstance(item, dict):
                item["summary"] = summary
            else:
                setattr(item, "summary", summary)

            return item

    async def process_async(self, items: List[Any]) -> List[Any]:
        """异步批量生成摘要（主入口）"""
        if not items:
            print("⚠️ ContentSummaryPipeline: 传入文章列表为空，跳过处理。")
            return []

        print(
            f"\n🤖 [ContentSummaryPipeline] 开始生成单条文章摘要，共 {len(items)} 条..."
        )
        tasks = [self._process_single_item(item) for item in items]
        summarized_items = await asyncio.gather(*tasks)
        print("✅ [ContentSummaryPipeline] 文章摘要生成完成！\n")
        return list(summarized_items)

    def process(self, items: List[Any]) -> List[Any]:
        """同步调用兼容入口（如果在非 async 函数中使用时备用）"""
        return asyncio.run(self.process_async(items))
