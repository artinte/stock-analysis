from playwright.async_api import async_playwright
from urllib.parse import urljoin
from playwright.async_api import async_playwright


async def fetch_cctv_finance_news():
    url = "https://finance.cctv.com/"
    print(f"🕵️  正在精准抓取央视财经核心新闻：{url}")

    collected_articles = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        try:
            print("🔗 正在导航至央视财经首页...")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            print("⏳ 正在等待新闻区块加载...")
            # 1. 核心改变：避开全页 a 标签，精准限定在财经主要内容区/列表区
            content_area = page.locator(
                ".content, .list, .con_left, #page_body, .text_box"
            )
            await content_area.first.wait_for(state="visible", timeout=15000)

            # 向下滚动 600px 避开顶栏干扰，并触发懒加载
            await page.evaluate("window.scrollBy(0, 600)")
            await page.wait_for_timeout(1000)

            # 2. 提取内容区域内的所有新闻链接
            links_locator = page.locator(
                '.content a, .list a, .con_left a, .text_box a, a[href*="ARTI"]'
            )
            count = await links_locator.count()
            print(f"👀 找到 {count} 个候选文章节点...")

            for i in range(count):
                item = links_locator.nth(i)
                title = (await item.inner_text()).strip()
                href = await item.get_attribute("href")

                if not href or not title:
                    continue

                full_url = urljoin(url, href)
                clean_title = title.replace("\n", " ").strip()

                # ---------------- 🛡️ 核心过滤逻辑 ----------------
                # 规则 1（硬核特征）：央视网真实新闻页面的 URL 必须包含 "ARTI" 或 "202" (年份)
                if "ARTI" not in full_url and "/202" not in full_url:
                    continue

                # 规则 2（黑名单）：彻底踢掉顶栏/多语言/App/专题
                blacklist = [
                    "rmlx",
                    "app.cctv",
                    "english.cctv",
                    "worldcup",
                    "passport",
                    "mn.cctv",
                    "live",
                ]
                if any(k in full_url for k in blacklist):
                    continue

                # 规则 3：过滤标题太短或通用导航词
                if (
                    len(clean_title) < 6
                    or clean_title in ["更多", "详细", "点击查看"]
                    or clean_title.startswith("http")
                ):
                    continue
                # ------------------------------------------------

                collected_articles.append(
                    {
                        "category": "央视财经",
                        "title": clean_title,
                        "link": full_url,
                    }
                )

            # 标题去重
            seen = set()
            unique_articles = []
            for art in collected_articles:
                if art["title"] not in seen:
                    seen.add(art["title"])
                    unique_articles.append(art)

            print(
                f"✅ 成功清洗！获取到 {len(unique_articles)} 条真正的央视财经新闻。\n"
            )

            for idx, art in enumerate(unique_articles[:5], 1):
                print(f"{idx}. {art['title']}")
                print(f"   🔗 {art['link']}\n")

            return unique_articles

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return []
        finally:
            await browser.close()


async def fetch_hot_topics_from_eastmoney():
    url = "https://gubatopic.eastmoney.com/"
    print(f"🕵️  正在抓取东方财富网热门话题：{url}")

    collected_topics = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        try:
            print("🔗 正在导航至目标网页...")
            # 采用 domcontentloaded，避免因个别广告图片加载慢导致超时
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            print("⏳ 正在等待话题元素加载...")
            # 策略：不硬编码类名，等待任意包含 topic 的链接或主要卡片出现
            target_locator = page.locator(
                'a[href*="topic"], .topic_item, .topic_list, .list_item'
            )
            await target_locator.first.wait_for(state="visible", timeout=15000)

            # 向下滚动一点触发懒加载
            await page.evaluate("window.scrollBy(0, 400)")
            await page.wait_for_timeout(1000)

            count = await target_locator.count()
            print(f"👀 找到 {count} 个候选话题节点...")

            for i in range(count):
                item = target_locator.nth(i)
                title = (await item.inner_text()).strip()
                href = await item.get_attribute("href")

                full_url = urljoin(url, href) if href else url  # 使用 urljoin 补全

                # 1. 黑名单：剔除登录、注册、个人中心等通用页面
                if any(
                    k in full_url
                    for k in ["passport", "login", "register", "user.eastmoney"]
                ):
                    continue

                # 过滤太短的垃圾链接或换行文本
                clean_title = title.replace("\n", " ").strip()
                if not clean_title or len(clean_title) < 3:
                    continue

                collected_topics.append(
                    {
                        "category": "东方财富热门话题",
                        "title": clean_title,
                        "link": full_url,
                    }
                )

            # 标题去重
            seen = set()
            unique_topics = []
            for t in collected_topics:
                if t["title"] not in seen:
                    seen.add(t["title"])
                    unique_topics.append(t)

            print(f"✅ 成功抓取到 {len(unique_topics)} 条热门话题！\n")
            for idx, top in enumerate(unique_topics[:5], 1):
                print(f"{idx}. {top['title']}")
                print(f"   🔗 {top['link']}\n")

            return unique_topics

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            # 如果依然超时，保存一张截图看看页面变成了什么样
            await page.screenshot(path="eastmoney_error.png")
            print("📸 已保存报错现场截图至 eastmoney_error.png")
            return []
        finally:
            await browser.close()


async def fetch_mofcom_news_like_human():
    """使用自动化浏览器，完全模拟人类访问商务部官网抓取政策"""
    url = "https://wms.mofcom.gov.cn/zcfb/wmgl/index.html"
    print(f"🕵️  正在访问 中华人民共和国商务部-政策发布-外贸管理：{url}")

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
            await page.goto(url, timeout=30000)

            print("⏳ 正在等待网页内部 JavaScript 执行以加载最新数据...")
            await page.wait_for_selector(".listCon", timeout=15000)

            links_locator = page.locator(".listCon a")
            count = await links_locator.count()
            print(
                f"👀 页面渲染完毕，检测到区域内有 {count} 个链接，正在筛选核心政策..."
            )

            for i in range(count):
                link_element = links_locator.nth(i)
                title = await link_element.inner_text()
                href = await link_element.get_attribute("href")

                if (
                    any(
                        k in title
                        for k in ["公告", "通知", "目录", "细则", "名单", "公示"]
                    )
                    and href
                ):
                    if href.startswith("/"):
                        full_url = "https://wms.mofcom.gov.cn" + href
                    elif href.startswith("."):
                        full_url = "https://wms.mofcom.gov.cn/zcfb/wmgl" + href.lstrip(
                            "."
                        )
                    else:
                        full_url = href

                    collected_articles.append(
                        {
                            "category": "商务部官网一手核心政策",
                            "title": title,
                            "link": full_url,
                        }
                    )

            seen = set()
            unique_articles = []
            for art in collected_articles:
                if art["title"] not in seen:
                    seen.add(art["title"])
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
