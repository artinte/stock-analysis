import os
import re
from typing import Any, List
from openai import OpenAI

# ==================== 【本地模型配置区域】 ====================
API_KEY = "ollama-local"
BASE_URL = "http://localhost:11434/v1"
# ==========================================================


def generate_daily_content_summary(
    news_list: List[Any],
    model_name: str,
) -> str:
    """调用本地大模型，提炼每日股票市场重点关注信息。"""

    if not news_list:
        print("未抓取到有效新闻，无法生成每日重点摘要。")
        return None

    print(
        f"🤖 正在调用本地 AI (模型: {model_name}) " f"提炼今日重点投资信息，请稍候..."
    )

    # 1. 构建新闻摘要素材
    raw_material = ""

    for idx, news in enumerate(news_list, 1):
        if isinstance(news, dict):
            source_name = news.get(
                "source_name",
                news.get("category", "综合资讯"),
            )
            title = news.get("title", "")
            summary = news.get("summary", "")
            published_at = news.get("published_at", "")
            link = news.get("link", news.get("url", ""))
        else:
            source_name = getattr(
                news,
                "source_name",
                "综合资讯",
            )
            title = getattr(news, "title", "")
            summary = getattr(news, "summary", "")
            published_at = getattr(news, "published_at", "")
            link = getattr(news, "url", "")

        # 没有摘要的新闻不作为主要分析素材
        if not summary:
            continue

        raw_material += (
            f"【新闻{idx}】\n"
            f"数据源：{source_name}\n"
            f"时间：{published_at}\n"
            f"标题：{title}\n"
            f"摘要：{summary}\n"
            f"链接：{link}\n\n"
        )

    if not raw_material:
        print("未找到有效新闻摘要，无法生成每日重点信息。")
        return None

    # 2. 每日重点信息提炼 Prompt
    system_prompt = (
        "你是一名专业的A股市场研究员和财经信息分析师。\n"
        "你的任务不是写新闻，而是从当天大量财经新闻中，"
        "筛选出真正值得股票投资者关注的信息，并进行归纳总结。\n\n"
        "【核心目标】\n"
        "从提供的新闻摘要中识别当天最重要的市场信息，"
        "帮助投资者快速回答三个问题：\n"
        "1. 今天发生了什么重要事情？\n"
        "2. 哪些行业、板块和上市公司可能受到影响？\n"
        "3. 接下来最值得继续关注什么？\n\n"
        "【重要规则】\n"
        "1. 必须严格依据提供的新闻内容，不得编造新闻、数据和事件。\n"
        "2. 不要简单罗列新闻，要进行归类、去重和交叉分析。\n"
        "3. 同一事件被多个媒体报道时，只保留一个核心事件，"
        "并说明多个数据源是否形成一致信号。\n"
        "4. 优先关注对A股市场可能产生实际影响的信息。\n"
        "5. 对重大政策、产业趋势、商品价格、海外事件、"
        "公司重大事件、行业供需变化给予更高权重。\n"
        "6. 如果新闻无法明确对应A股公司，不要强行关联上市公司。\n"
        "7. 不得把新闻事实直接写成确定性的股价预测。\n"
        "8. 不要输出投资建议、买入卖出指令或具体仓位。\n"
        "9. 对信息的重要程度进行排序，最重要的信息放在最前面。\n"
        "10. 语言简洁，信息密度高，避免空话和套话。\n\n"
        "【重点判断维度】\n"
        "请重点从以下几个方向筛选信息：\n"
        "① 宏观经济与政策\n"
        "② 产业政策与监管变化\n"
        "③ 行业供需与价格变化\n"
        "④ 海外市场与国际事件\n"
        "⑤ 大宗商品价格变化\n"
        "⑥ AI、半导体、新能源等产业趋势\n"
        "⑦ 上市公司重大事件\n"
        "⑧ 资金、市场情绪和指数变化\n"
        "⑨ 对A股行业和上市公司的潜在影响\n\n"
        "【输出格式】\n"
        "请严格按照以下结构输出：\n\n"
        "一、今日市场核心结论\n"
        "用3～5句话概括今天最重要的市场变化和核心逻辑。\n\n"
        "二、今日最值得关注的事件\n"
        "筛选5～10条最重要的信息，并按照重要程度排序。\n"
        "每条使用以下格式：\n"
        "【重要程度：★★★★★】\n"
        "事件：具体事件名称\n"
        "核心信息：用简洁语言说明发生了什么。\n"
        "市场影响：说明可能影响哪些行业或产业链。\n"
        "A股映射：列出有明确逻辑关联的A股行业或公司；"
        "如果无法确定则写“暂无明确映射”。\n\n"
        "三、行业与板块信号\n"
        "按照行业进行归类，只保留有明显信息变化的行业。\n"
        "格式：\n"
        "【行业名称】\n"
        "变化：发生了什么变化。\n"
        "逻辑：为什么值得关注。\n"
        "影响方向：偏利好 / 偏利空 / 中性 / 暂不明确。\n\n"
        "四、今日需要重点跟踪\n"
        "列出未来1～7天最值得继续关注的事项，"
        "例如政策落地、业绩披露、价格变化、重大会议、"
        "行业数据等。\n\n"
        "五、今日一句话总结\n"
        "用一句话总结今天对A股投资者最重要的信息。"
    )

    user_prompt = (
        "请根据以下已经提炼好的财经新闻摘要，"
        "生成一份《每日股票重点关注信息》。\n\n"
        "注意：以下内容中的 summary 已经是单条新闻的AI摘要，"
        "请在此基础上进行第二层综合分析，不要重新复述所有新闻。\n\n"
        f"{raw_material}"
    )

    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
            timeout=600.0,
        )

        response = client.chat.completions.create(
            model=model_name,
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
            temperature=0.7,
            max_tokens=4000,
        )

        full_content = response.choices[0].message.content

        # 清理模型可能输出的 <think>...</think>
        clean_content = re.sub(
            r"<think>.*?</think>",
            "",
            full_content or "",
            flags=re.DOTALL,
        ).strip()

        return clean_content if clean_content else full_content

    except Exception as e:
        print(f"❌ 调用本地 AI 失败，请检查 Ollama 是否正常运行。" f"错误信息: {e}")
        return None


class DailyContentSummaryPipeline:
    """每日财经信息综合提炼与本地落盘管道。"""

    def __init__(
        self,
        output_filename: str = "daily_content_summary.txt",
        model_name: str = "",
    ):
        self.output_filename = output_filename
        self.model_name = model_name

    def process(self, news_list: List[Any]):
        """生成每日股票重点关注信息。"""

        if not news_list:
            print("❌ 未能捕获到有效新闻素材。")
            return

        if not self.model_name:
            print("❌ 未指定本地 Ollama 模型名称。")
            return

        daily_summary = generate_daily_content_summary(
            news_list,
            self.model_name,
        )

        if daily_summary:
            print("\n" + "📊" * 10 + " 今日股票重点关注信息 " + "📊" * 10 + "\n")

            print(daily_summary)

            print("\n" + "=" * 60)

            output_dir = os.path.join(
                os.getcwd(),
                "output",
            )

            os.makedirs(
                output_dir,
                exist_ok=True,
            )

            output_file = os.path.join(
                output_dir,
                self.output_filename,
            )

            with open(
                output_file,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(daily_summary)

            print(f"🎉 每日重点信息生成完成：{output_file}")

        return daily_summary
