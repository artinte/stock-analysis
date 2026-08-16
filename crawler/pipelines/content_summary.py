import asyncio
import re
from typing import Any, List
from openai import OpenAI


class ContentSummaryPipeline:
    """文章内容提炼/生成摘要 Pipeline
    专门用于为单条新闻/文章的 content 字段生成精炼 summary 字段
    """

    def __init__(self, model_name,concurrency_limit: int = 5):
        """初始化 Pipeline
        :param concurrency_limit: AI API 调用的最大并发数，防止触发 Rate Limit
        """
        self.model_name = model_name
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def _call_ai_model(self, content: str) -> str:
        """调用本地 Ollama AI 模型生成新闻摘要。"""

        if not content or not content.strip():
            return "（文本为空，无法生成摘要）"

        API_KEY = "ollama-local"
        BASE_URL = "http://localhost:11434/v1"

        try:
            client = OpenAI(
                api_key=API_KEY,
                base_url=BASE_URL,
                timeout=600.0,
            )

            system_prompt = (
                "你是一名专业的财经新闻编辑，负责生成高质量的新闻摘要。\n"
                "请根据提供的新闻正文，提炼出最核心的信息。\n"
                "要求：\n"
                "1. 严格依据原文，不得编造信息。\n"
                "2. 准确提炼新闻的核心事实、事件、数据和影响。\n"
                "3. 摘要控制在100～150字以内。\n"
                "4. 语言简洁、客观、信息密度高。\n"
                "5. 不要加入个人观点、投资建议或主观判断。\n"
                "6. 不要重复标题或添加“摘要：”等前缀。\n"
                "7. 直接输出摘要正文。\n"
            )

            user_prompt = (
                "请根据以下财经新闻正文生成一段简洁的新闻摘要：\n\n"
                f"{content[:8000]}"
            )

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.3,
                max_tokens=300,
            )

            full_content = response.choices[0].message.content or ""

            # 清理模型可能输出的 <think>...</think>
            clean_content = re.sub(
                r"<think>.*?</think>",
                "",
                full_content,
                flags=re.DOTALL,
            ).strip()

            return clean_content if clean_content else "（AI未生成有效摘要）"

        except Exception as e:
            print(f"❌ AI 摘要生成失败：{e}")
            return "（AI摘要生成失败）"

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
