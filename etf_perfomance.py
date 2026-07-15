import os
import time
import datetime
import warnings
import pandas as pd
from playwright.sync_api import sync_playwright

ETF_PATH = "https://www.csindex.com.cn/#/indices/family/detail?indexCode=931380"


def download_etf_wegith_data(target_url=ETF_PATH):
    """自动化下载中证ETF权重数据，并返回保存的文件绝对路径。"""

    with sync_playwright() as p:
        print("正在启动自动化浏览器...")
        # 调试时如果遇到问题，可以把 headless 改为 False 观察浏览器行为
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"正在打开网页: {target_url}")
        try:
            # 使用 networkidle 或 load 确保页面的异步数据和元素加载完毕
            page.goto(target_url, wait_until="networkidle", timeout=45000)
        except Exception as e:
            print(f"网页基础加载遇到警告: {e}")

        # ------------------- 核心修改：精确定位并点击下载 -------------------
        # 根据你提供的 HTML 结构，使用带有特定 class 的 a 标签或者包含“样本权重”文本的 selector
        weight_download_selector = "a.cursor:has-text('样本权重')"

        print("正在定位 [样本权重] 下载链接...")
        try:
            page.wait_for_selector(weight_download_selector, timeout=20000)
            print("✅ 成功定位到下载元素，准备触发下载...")
        except Exception as e:
            print(
                f"错误：无法定位到 [样本权重] 下载链接。可能是页面未加载完全或结构有变动: {e}"
            )
            browser.close()
            return None

        print("正在点击链接并拦截下载文件...")
        try:
            # 拦截 Playwright 的下载事件
            with page.expect_download(timeout=30000) as download_info:
                page.click(weight_download_selector)

            download = download_info.value
            today_str = datetime.datetime.now().strftime("%Y%m%d")

            # 获取官方推荐文件名，如果获取不到则使用兜底名称
            suggested_name = download.suggested_filename
            if suggested_name:
                name_part, ext_part = os.path.splitext(suggested_name)
                filename = f"{name_part}_{today_str}{ext_part}"
            else:
                # 页面上是 .xlsx 格式
                filename = f"931380closeweight_{today_str}.xlsx"

            save_path = os.path.join(os.getcwd(), filename)
            download.save_as(save_path)

            print(f"🎉 自动化下载成功！文件已保存至: {save_path}")
            browser.close()
            return save_path

        except Exception as e:
            print(f"下载文件时遭遇错误: {e}")
            browser.close()
            return None


def main():
    print("=================== 启动自动化爬取与分析流 ===================")

    # 1. 爬取并下载 Excel 权重文件
    excel_file = download_etf_wegith_data()
    if not excel_file:
        print("❌ 自动化文件下载流程失败。")
        return

    print(f"主程序获取到的文件路径: {excel_file}")


if __name__ == "__main__":
    main()