from playwright.async_api import async_playwright


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
            
