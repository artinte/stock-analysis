import os
import re
from typing import Any, List
from openai import OpenAI

# ==================== 【本地模型配置区域】 ====================
API_KEY = "ollama-local"
BASE_URL = "http://localhost:11434/v1"

# 确保模型名称与本地一致
MODEL_NAME = "deepseek-r1:latest"
# ==========================================================


def generate_xueqiu_article(news_list: List[Any]) -> str:
    """调用【本地大模型】，熔炼结合具体新闻的爆款雪球深度分析长文"""
    if not news_list:
        print("未抓取到有效新闻，无法生成文章。")
        return None

    print(
        f"🤖 正在调用本地 AI (模型: {MODEL_NAME}) 深度熔炼全网最新资讯，请稍候..."
    )

    # 1. 构建明确且带有来源标注的新闻素材串
    raw_material = ""
    for idx, news in enumerate(news_list, 1):
        if isinstance(news, dict):
            category = news.get("source_name", news.get("category", "综合资讯"))
            title = news.get("title", "")
            link = news.get("link", news.get("url", ""))
        else:
            category = getattr(news, "source_name", "综合资讯")
            title = getattr(news, "title", "")
            link = getattr(news, "url", "")

        raw_material += (
            f"【素材{idx}】[数据源: {category}] 标题: {title} | 链接: {link}\n"
        )

    # 2. 强化的 Prompt：要求必须结合具体新闻标题，禁止泛泛而谈
    system_prompt = (
        "你是一位活跃在雪球（Xueqiu）的顶级财经大V，粉丝极度认可你的政策解读与市场趋势捕捉能力。\n"
        "【重要规则 - 绝对禁止空谈】：\n"
        "1. 文章中必须直接引用用户提供的具体新闻标题（例如：根据《xxx新闻》所述...）。\n"
        "2. 不要只盯着单一部门（如商务部），必须对传入的所有不同数据源（央视财经、东方财富、各部委官网等）进行交叉融合分析！\n"
        "3. 不要只写框架说明，要结合具体新闻点名利好的行业或概念板块，并给出雪球风格的观点。\n"
        "4. 请不要在思考过程（think）中消耗过多篇幅，正文要求字数不少于 1200 字。\n\n"
        "【文章结构规范】：\n"
        "一、 标题：极其吸睛、悬念十足的雪球爆款标题。\n"
        "二、 【重磅解读】：抛出最核心的宏观/行业判断。\n"
        "三、 【新闻事件逐条点睛】：必须列举素材中的具体新闻标题，逐一剖析背后的商业逻辑与主力资金意图。\n"
        "四、 【A股具体板块利好利空分析】：结合上述新闻，直接点名受影响的 A 股板块（如半导体、新能源、医药、农业、外贸等）。\n"
        "五、 【老铁实操策略与互动】：给出具体的仓位建议，并在结尾留下评论区互动话题。"
    )

    user_prompt = f"请根据以下刚刚抓取的具体新闻素材，撰写一篇结合具体新闻标题进行深度拆解的雪球爆款长文：\n\n{raw_material}"

    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=600.0)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )

        full_content = response.choices[0].message.content

        # 过滤掉 DeepSeek-R1 的 <think>...</think> 内部思考过程
        clean_content = re.sub(
            r"<think>.*?</think>", "", full_content, flags=re.DOTALL
        ).strip()

        return clean_content if clean_content else full_content

    except Exception as e:
        print(
            f"❌ 调用本地 AI 失败，请检查 Ollama 是否在后台正常运行。错误信息: {e}"
        )
        return None


class ArticleGeneratePipeline:
    """雪球深度分析与本地落盘管道"""

    def __init__(self, output_filename: str = "xueqiu_local_output.txt"):
        self.output_filename = output_filename

    def process(self, news_list: List[Any]):
        if not news_list:
            print("❌ 实验未能完成：未能捕获到有效新闻素材。")
            return

        post_generated = generate_xueqiu_article(news_list)

        if post_generated:
            print(
                "\n"
                + "🔥" * 10
                + " 本地 AI 生成的雪球深度分析长文 "
                + "🔥" * 10
                + "\n"
            )
            print(post_generated)
            print("\n" + "=" * 50)

            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, self.output_filename)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(post_generated)

            print(f"🎉 本地实验大成功！文章已完美保存至本地：{output_file}")
            
        return post_generated