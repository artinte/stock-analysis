import os
import time
import datetime
import warnings
import pandas as pd
import concurrent.futures
from playwright.sync_api import sync_playwright

"""
==========================================================================================
脚本名称: download_csindex.py
所属项目: stock-analysis (量化选股数据矩阵框架)
==========================================================================================
"""

# 【恢复同步定义 def】
def download_csindex_industry_data(download_dir=os.getcwd()):
    """自动化下载中证行业数据，并返回保存的文件绝对路径。

    如果下载失败，返回 None。
    """
    target_url = "https://www.csindex.com.cn/#/dataService/industryClassification"

    with sync_playwright() as p:
        print("正在启动自动化浏览器...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"正在打开网页: {target_url}")
        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"网页基础加载遇到警告（不影响后续操作）: {e}")

        print("等待数据表格加载...")
        time.sleep(5)

        export_btn_selector = "button:has-text('导出数据')"

        print("正在定位 [导出数据] 按钮...")
        try:
            page.wait_for_selector(export_btn_selector, timeout=15000)
        except Exception:
            print("错误：页面虽然打开了，但等了 15 秒都没看到 [导出数据] 按钮。")
            browser.close()
            return None

        print("点击导出按钮，正在拦截并下载 Excel 文件...")
        try:
            with page.expect_download(timeout=30000) as download_info:
                page.click(export_btn_selector)

            download = download_info.value
            today_str = datetime.datetime.now().strftime("%Y%m%d")

            suggested_name = download.suggested_filename
            if suggested_name:
                name_part, ext_part = os.path.splitext(suggested_name)
                filename = f"{name_part}_{today_str}{ext_part}"
            else:
                filename = f"中证行业分类数据_{today_str}.xlsx"

            save_path = os.path.join(download_dir, filename)
            download.save_as(save_path)
            print(f"🎉 自动化爬取成功！文件已保存至: {save_path}")
            browser.close()
            return save_path

        except Exception as e:
            print(f"下载文件时遭遇错误: {e}")
            browser.close()
            return None


def get_csindex_industry_data(download_dir=os.getcwd(), force_update=False):
    """外部调用核心入口函数。"""
    today_str = datetime.datetime.now().strftime("%Y%m%d")

    expected_file = None
    for file in os.listdir(download_dir):
        if today_str in file and file.endswith(".xlsx"):
            expected_file = os.path.join(download_dir, file)
            break

    if expected_file and os.path.exists(expected_file) and not force_update:
        print(f"检测到今日数据已存在本地: {expected_file}，直接加载...")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
            df = pd.read_excel(expected_file)
        return df
    else:
        if force_update:
            print("已触发 [强制更新]，跳过本地缓存，开始启动线上下载...")
        else:
            print("本地未检测到今日数据，开始启动线上下载...")

        # 【核心改动】：使用线程池把同步的 Playwright 隔离到子线程执行，避免触发 asyncio 事件循环冲突
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(download_csindex_industry_data, download_dir)
            file_path = future.result()

        if file_path and os.path.exists(file_path):
            print("下载完成，开始转换成 Pandas DataFrame...")
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", category=UserWarning, module="openpyxl"
                )
                df = pd.read_excel(file_path)
            return df
        else:
            raise FileNotFoundError(
                "未能成功下载中证行业分类数据，无法转换为 DataFrame。"
            )


# 测试当前文件运行情况
if __name__ == "__main__":
    try:
        df_data = get_csindex_industry_data()
        print("\n--- 成功获取数据前 5 行预览 ---")
        print(df_data.head())
        print(f"数据总行数: {len(df_data)}")
    except Exception as ex:
        print(f"运行失败: {ex}")