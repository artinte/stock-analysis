import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


COOKIE_FILE = os.path.join("temp", "xueqiu_cookies.json")

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def save_cookies(driver):
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

def post_comment():
    driver = get_driver()
    try:
        url = "https://xueqiu.com/S/SZ002430"
        driver.get(url)
        time.sleep(2)

        if not load_cookies(driver):
            print("\n" + "="*50)
            print("【首次运行】未找到登录凭证！请在 60 秒内手动完成登录。")
            print("="*50 + "\n")
            time.sleep(60)
            save_cookies(driver)
            driver.get(url)
            time.sleep(3)
        else:
            driver.refresh()
            time.sleep(4)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment_content = f"关注 $杭氧股份(SZ002430)$ 的最新动态 [{now_str}]"

        # 1. 向上/向下平滑滚动，确保组件载入
        print("正在定位快捷编辑器 (.lite-editor)...")
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(1)

        wait = WebDriverWait(driver, 10)

        # 2. 精准定位你给的这层伪输入框：.fake-placeholder 或 .lite-editor__textarea
        fake_editor = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".fake-placeholder, .lite-editor__textarea, .lite-editor")
        ))

        # 3. 将元素居中并点击激活输入框
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fake_editor)
        time.sleep(1)
        fake_editor.click()
        print("✅ 成功点击伪输入框，已激活编辑状态！")
        time.sleep(1)

        # 4. 激活后输入文字（点击后光标会自动聚焦到活动元素，直接输入或寻找展开后的富文本/textarea）
        active_element = driver.switch_to.active_element
        active_element.send_keys(comment_content)
        print("✅ 内容已输入！")
        time.sleep(1)

        # 5. 精准定位你 HTML 中的【发布】按钮: .lite-editor__submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, ".lite-editor__submit")

        # 6. 使用 JavaScript 强制触发点击发布（避开 disabled 或样式拦截）
        driver.execute_script("arguments[0].click();", submit_btn)
        print(f"🎉 评论发布成功：{comment_content}")

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        driver.save_screenshot("error_screenshot.png")

    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    post_comment()