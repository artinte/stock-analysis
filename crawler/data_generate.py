
from openai import OpenAI

# ==================== 【本地模型配置区域】 ====================
# 当使用本地 Ollama 时：
# 1. API_KEY 可以随便填一个非空字符串（Ollama 本地不需要鉴权）
API_KEY = "ollama-local" 

# 2. BASE_URL 指向你本地启动的 Ollama 端口
BASE_URL = "http://localhost:11434/v1" 

# 3. MODEL_NAME 改为你刚刚在本地下载的模型名称（例如 deepseek-r1:8b 或 llama3 等）
MODEL_NAME = "deepseek-r1:latest"            
# ==========================================================



def generate_xueqiu_article(news_list):
    """调用【本地大模型】，将抓取到的一手政策熔炼成雪球爆款分析长文"""
    if not news_list:
        print("未抓取到有效新闻，无法生成文章。")
        return None
        
    # 明确提示正在调用本地模型，本地推理需要消耗你电脑本身的硬件性能
    print(f"🤖 正在调用本地 AI (模型: {MODEL_NAME}) 深度熔炼文章，请稍候（取决于本地显卡/CPU速度）...")
    
    raw_material = ""
    for idx, news in enumerate(news_list, 1):
        raw_material += f"【素材{idx}】来源: {news['category']} | 标题: {news['title']} | 链接: {news['link']}\n"

    system_prompt = (
        "你是一位活跃在雪球（Xueqiu）的顶级财经大V，粉丝极度认可你的政策解读能力。\n"
        "你的任务是把用户提供的一手『商务部官网外贸政策』，转换一篇极具冲击力的深度分析长文。\n"
        "请严格遵守以下雪球风格要求：\n"
        "1. 标题必须有爆发力、悬念十足（例如：重磅突发！商务部深夜出手，这几个板块的老铁要抱紧了！）。\n"
        "2. 语言极度口语化且富有煽动性，多用『盘面来看』、『核心逻辑』、『主力资金』等雪球高频词。\n"
        "3. 文章骨架：先抛出最震撼的政策结论 -> 针对商务部最新的公告标题进行一针见血的解读 -> 详细拆解这会利好或利空A股的哪些具体行业板块（如半导体、国防军工、汽车等） -> 给出具体的实操仓位建议。\n"
        "4. 结尾要留互动话题（例如：老铁们，你们觉得这波能走多远？评论区见！）。"
    )
    
    user_prompt = f"请根据以下刚刚从商务部官网直接捕获的最新外贸管理一手素材，撰写一篇雪球深度的爆款长文：\n\n{raw_material}"

    try:
        # 这里的 client 会自动向你本地 11434 端口的 Ollama 发起通信
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ 调用本地 AI 失败，请检查 Ollama 是否在后台正常运行。错误信息: {e}")
        return None