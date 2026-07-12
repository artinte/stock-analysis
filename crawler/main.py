import os
import asyncio
from playwright.async_api import async_playwright
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

NEWS_SOURCES = {
    "中华人民共和国商务部-政策发布-外贸管理": "https://wms.mofcom.gov.cn/zcfb/wmgl/index.html"
}

async def fetch_mofcom_news_like_human():
    """使用自动化浏览器，完全模拟人类访问商务部官网抓取政策"""
    target_url = NEWS_SOURCES["中华人民共和国商务部-政策发布-外贸管理"]
    print(f"🕵️  正在启动自动化浏览器，模拟人类访问：{target_url}")
    
    collected_articles = []
    async with async_playwright() as p:
        # 这里改为了 True 模式（后台静默运行），如果你想看浏览器弹窗，可以改回 False
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print("🔗 正在导航至目标网页...")
            await page.goto(target_url, timeout=30000)
            
            print("⏳ 正在等待网页内部 JavaScript 执行以加载最新数据...")
            await page.wait_for_selector(".listCon", timeout=15000)
            
            links_locator = page.locator(".listCon a")
            count = await links_locator.count()
            print(f"👀 页面渲染完毕，检测到区域内有 {count} 个链接，正在筛选核心政策...")
            
            for i in range(count):
                link_element = links_locator.nth(i)
                title = await link_element.inner_text()
                href = await link_element.get_attribute("href")
                
                if any(k in title for k in ["公告", "通知", "目录", "细则", "名单", "公示"]) and href:
                    if href.startswith("/"):
                        full_url = "https://wms.mofcom.gov.cn" + href
                    elif href.startswith("."):
                        full_url = "https://wms.mofcom.gov.cn/zcfb/wmgl" + href.lstrip('.')
                    else:
                        full_url = href
                        
                    collected_articles.append({
                        "category": "商务部官网一手核心政策",
                        "title": title,
                        "link": full_url
                    })
            
            seen = set()
            unique_articles = []
            for art in collected_articles:
                if art['title'] not in seen:
                    seen.add(art['title'])
                    unique_articles.append(art)
                    
            print(f"✅ 成功！获取到了 {len(unique_articles[:5])} 条最新的商务部政策。")
            
            print("\n" + "📋" * 5 + " 抓取到的最新核心政策明细 " + "📋" * 5)
            for idx, art in enumerate(unique_articles[:5], 1):
                print(f" {idx}. [{art['category']}]")
                print(f"    标题: {art['title']}")
                print(f"    链接: {art['link']}\n")
            print("=" * 40 + "\n")
            
            return unique_articles[:5]
            
        except Exception as e:
            print(f"❌ 浏览器模拟访问失败: {e}")
            return []
        finally:
            await browser.close()

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

# ==================== 主运行逻辑 ====================
async def main():
    mofcom_news = await fetch_mofcom_news_like_human()
    
    if mofcom_news:
        xueqiu_post = generate_xueqiu_article(mofcom_news)
        
        if xueqiu_post:
            print("\n" + "🔥" * 10 + " 本地 AI 生成的雪球深度分析长文 " + "🔥" * 10 + "\n")
            print(xueqiu_post)
            print("\n" + "=" * 50)
            
            output_file = "xueqiu_local_output.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(xueqiu_post)
            print(f"🎉 本地实验大成功！文章已完美保存至本地：{output_file}")
    else:
        print("❌ 实验未能完成：未能从官网捕获到有效政策标题。")

if __name__ == "__main__":
    asyncio.run(main())