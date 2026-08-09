import os
import json
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

"""
====================================================================
雪球自动化评论与去重控制脚本 (Xueqiu Auto-Comment System)
====================================================================

【主要功能】
1. 自动化发表评论：利用 Selenium 模拟浏览器自动定位雪球帖子/股票页面的快捷编辑器进行评论。
2. 免密登录凭证复用：支持 Cookie 的本地持久化存储 (`xueqiu_cookies.json`)，仅需首次手动登录。
3. 自动化弹窗与遮罩清理：发布评论前，自动检测并点击关闭各类弹窗，并通过 JS 强行清理蒙层与遮罩。
4. 智能去重与过期清理缓存：
   - 维护本地缓存文件 (`commented_history.json`)，避免对同一个 URL 重复评论。
   - 内置时效控制机制（默认 15 天）：超过 15 天的旧评论记录会自动清理，释放缓存空间。
   - 设置评论间隔 60 秒，避免触发风控。

【环境依赖】
- Python 3.8+
- selenium, webdriver-manager

【文件结构】
- temp/xueqiu_cookies.json      : 存放登录态 Cookie
- temp/commented_history.json  : 存放历史评论记录与时间戳
- error_screenshot.png         : 异常时的截图留存
====================================================================
"""


COOKIE_FILE = os.path.join("temp", "xueqiu_cookies.json")
CACHE_FILE = os.path.join("temp", "commented_history.json")


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        },
    )
    return driver


def save_cookies(driver):
    os.makedirs("temp", exist_ok=True)
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f)
    print("✅ 成功保存登录状态 (Cookie)！")


def load_cookies(driver):
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ 已加载本地登录状态 (Cookie)")
        return True
    return False


def clean_and_load_history(days=15):
    """读取历史记录并自动清理 N 天（默认 15 天）之前的过期缓存"""
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

        now = datetime.now()
        cleaned_history = {}
        expired_count = 0

        # 遍历缓存，过滤掉超过 15 天的记录
        for url, data in history.items():
            commented_at_str = data.get("commented_at")
            if commented_at_str:
                commented_time = datetime.strptime(
                    commented_at_str, "%Y-%m-%d %H:%M:%S"
                )
                # 如果记录时间在 15 天以内，予以保留
                if now - commented_time <= timedelta(days=days):
                    cleaned_history[url] = data
                else:
                    expired_count += 1
            else:
                cleaned_history[url] = data

        if expired_count > 0:
            print(f"🧹 已自动清理 {expired_count} 条超过 {days} 天的过期评论缓存")

        return cleaned_history
    except Exception as e:
        print(f"⚠️ 读取/清理历史缓存出错: {e}")
        return {}


def is_already_commented(url):
    """检查 URL 是否在有效期内的缓存中"""
    history = clean_and_load_history(days=15)
    return url in history


def record_comment_history(url, content):
    """保存最新评论，同时剔除过期记录后存盘"""
    os.makedirs("temp", exist_ok=True)

    # 1. 加载并清理 15 天前的旧数据
    history = clean_and_load_history(days=15)

    # 2. 插入当前最新评论记录
    history[url] = {
        "content": content,
        "commented_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 3. 重新写入 JSON 文件
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print("💾 已记录该 URL 到评论缓存（有效期 15 天）！")


def post_comment(url, comment_content=None, interval=60):
    # 0. 去重与过期校验
    if is_already_commented(url):
        print(f"⚠️ 跳过执行：该 URL 在近 15 天内已评论过 -> {url}")
        return

    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(2)

        if not load_cookies(driver):
            print("\n" + "=" * 50)
            print("【首次运行】未找到登录凭证！请在 60 秒内手动完成登录。")
            print("=" * 50 + "\n")
            time.sleep(60)
            save_cookies(driver)
            driver.get(url)
            time.sleep(3)
        else:
            driver.refresh()
            time.sleep(4)

        # 1. 向上/向下平滑滚动，确保组件载入
        print("正在定位快捷编辑器 (.lite-editor)...")
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(1)

        # 💡 自动关闭弹窗并彻底清理遮罩蒙层
        try:
            close_btns = driver.find_elements(
                By.CSS_SELECTOR,
                ".modal .close, .ui.modal .close, .download-app-close, [class*='close']",
            )
            for btn in close_btns:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
        except Exception:
            pass

        driver.execute_script("""
            var overlays = document.querySelectorAll('.modals.dimmer, .ui.dimmer, .modal, .mask, [class*="popup"], [class*="qrcode"], [class*="weixin"]');
            overlays.forEach(function(el) { el.remove(); });
            document.body.classList.remove('dimmable', 'dimmed', 'scrolling', 'modal-open');
        """)
        time.sleep(0.5)

        wait = WebDriverWait(driver, 10)

        # 2. 精准定位伪输入框
        fake_editor = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".fake-placeholder, .lite-editor__textarea, .lite-editor",
                )
            )
        )

        # 3. 将元素居中并点击激活输入框
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", fake_editor
        )
        time.sleep(1)
        fake_editor.click()
        print("✅ 成功点击伪输入框，已激活编辑状态！")
        time.sleep(1)

        # 4. 激活后输入文字
        active_element = driver.switch_to.active_element
        active_element.send_keys(comment_content)
        print("✅ 内容已输入！")
        time.sleep(1)

        # 5. 精准定位【发布】按钮
        submit_btn = driver.find_element(By.CSS_SELECTOR, ".lite-editor__submit")

        # 6. 使用 JavaScript 强制触发点击发布
        driver.execute_script("arguments[0].click();", submit_btn)
        print(f"🎉 评论发布成功：{comment_content}")

        # 7. 成功发布后记录并更新缓存
        record_comment_history(url, comment_content)
        
        # 8. 留存间隔，避免过快操作
        time.sleep(interval)

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        driver.save_screenshot("error_screenshot.png")

    finally:
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    url = "https://xueqiu.com/S/SZ002430"  # 替换为你要评论的雪球帖子 URL
    comment_content = "这是一条测试评论。"
    post_comment(url, comment_content)
