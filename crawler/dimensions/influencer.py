import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import re

class SentinelWebScraper:
    def __init__(self):
        # 你指定的网页地址
        self.url = "https://truthsocial.com/@realDonaldTrump"
        # 风险关键词：直接关联石油、氦气、铝、化工
        self.risk_keywords = ["Strait", "Tuesday", "8:00", "Power Plant", "Oil", "Helium", "Aluminum", "Bridge"]

    async def fetch_and_analyze(self):
        async with async_playwright() as p:
            # 启动浏览器 (headless=True 为后台运行，改为 False 可以看到浏览器操作)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()

            print(f"🚀 正在访问: {self.url} ...")
            try:
                await page.goto(self.url, wait_until="networkidle", timeout=60000)
                # 等待帖子内容加载（根据 TruthSocial 的 CSS 标签）
                await page.wait_for_selector(".status__content", timeout=15000)
            except Exception as e:
                print(f"❌ 页面加载超时或被拦截: {e}")
                await browser.close()
                return

            # 抓取所有帖子容器
            # 过滤掉转发(Reblogged)的内容，只留原创
            posts = await page.query_selector_all("div.status")
            
            count = 0
            print(f"\n[ 实时情报分析 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ]")
            print("="*60)

            for post in posts:
                if count >= 5: break

                # 检查是否是转贴 (通常带有 'Reblogged' 文本)
                reblog_check = await post.query_selector(".status__prepend")
                if reblog_check: continue

                # 提取文字内容
                content_element = await post.query_selector(".status__content")
                if not content_element: continue
                
                raw_text = await content_element.inner_text()
                # 提取发布时间
                time_element = await post.query_selector("time")
                post_time = await time_element.get_attribute("title") if time_element else "Unknown"

                # --- 核心逻辑分析 ---
                # 1. 情绪分析 (感叹号)
                excitement = raw_text.count("!")
                # 2. 压力分析 (大写单词)
                caps_ratio = sum(1 for w in raw_text.split() if w.isupper()) / (len(raw_text.split()) + 1)
                # 3. 资产关联
                impacts = [k for k in self.risk_keywords if k.lower() in raw_text.lower()]
                # 4. 死线判定
                is_critical = any(word in raw_text for word in ["Tuesday", "8:00", "Deadline"])

                # --- 打印报告 ---
                count += 1
                print(f"【情报 {count}】| 时间: {post_time}")
                print(f"内容: {raw_text.strip()[:200]}...")
                print(f"📊 因子: {'🔥'*excitement if excitement > 0 else '常规'} | 压力指数: {caps_ratio:.1%} | 资产: {impacts if impacts else '宏观'}")
                
                if is_critical:
                    print(f"⚠️  [判定] 锁定周三 08:00 A股开盘风险，对应 3月大宗商品 14.5% 涨幅逻辑。")
                print("-" * 60)

            await browser.close()

if __name__ == "__main__":
    scraper = SentinelWebScraper()
    # 运行一次抓取 5 条
    asyncio.run(scraper.fetch_and_analyze())