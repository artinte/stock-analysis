import os
import time
import datetime
import warnings
import pandas as pd
from playwright.sync_api import sync_playwright

"""
==========================================================================================
脚本名称: download_csindex.py
所属项目: stock-analysis (量化选股数据矩阵框架)
脚本功能: 自动化抓取中证指数官网(csindex.com.cn)全量A股官方行业分类数据，并导出为Excel文件。

技术机制与避坑说明:
1. 解决 Blob 临时链接阻碍问题: 
   目标网页的“导出数据”按钮由前端 JavaScript 动态生成内存对象 (blob:https://...)。
   传统 requests/urllib 爬虫由于无法执行 JS 且无法跨域截获内存流，故在此失效。
   本脚本采用新一代仿真浏览器框架 Playwright，通过开启 `expect_download()` 下载管道监听器，
   在底层成功拦截并捕获了浏览器下载管道中由 Blob 对象转化而来的二进制文件流，实现无缝落盘。

2. 解决 Timeout 30000ms 超时崩溃问题:
   中证官网在渲染完核心数据后，后台仍会持续发送大量埋点、监控和字体流请求。
   若盲目使用 `wait_until="networkidle"` 会导致脚本陷入长达30秒的死等并触发崩溃。
   本脚本优化为 `wait_until="domcontentloaded"`（骨架加载即放行），并配合 5 秒硬性缓冲时间，
   在兼顾按钮渲染完整性的同时，彻底规避了网络请求死锁导致的超时错误。

依赖环境:
    pip install playwright
    playwright install chromium

维护建议:
   - 本数据可作为六维量化矩阵（VCP形态、Forward PEG、PB-ROE匹配度等）的基础行业分类映射表。
   - 中证行业分类通常按交易日/季度更新。建议配置定时任务(如 Windows 任务计划或 Crontab)定期运行。
   - 网页元素如发生版面大改（如“导出数据”按钮文本或结构变更），需同步修正 `export_btn_selector`。
==========================================================================================
"""


def download_csindex_industry_data():
    """自动化下载中证行业数据，并返回保存的文件绝对路径。

    如果下载失败，返回 None。
    """
    target_url = (
        "https://www.csindex.com.cn/#/dataService/industryClassification"
    )

    with sync_playwright() as p:
        print("正在启动自动化浏览器...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"正在打开网页: {target_url}")
        try:
            page.goto(
                target_url, wait_until="domcontentloaded", timeout=45000
            )
        except Exception as e:
            print(f"网页基础加载遇到警告（不影响后续操作）: {e}")

        print("等待数据表格加载...")
        time.sleep(5)

        export_btn_selector = "button:has-text('导出数据')"

        print("正在定位 [导出数据] 按钮...")
        try:
            page.wait_for_selector(export_btn_selector, timeout=15000)
        except Exception:
            print(
                "错误：页面虽然打开了，但等了 15 秒都没看到 [导出数据] 按钮。"
            )
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

            save_path = os.path.join(os.getcwd(), filename)
            download.save_as(save_path)
            print(f"🎉 自动化爬取成功！文件已保存至: {save_path}")
            browser.close()
            return save_path  # 【改动】成功后返回文件路径

        except Exception as e:
            print(f"下载文件时遭遇错误: {e}")
            browser.close()
            return None


def get_csindex_industry_data():
    """外部调用核心入口函数。

    检查今日数据是否存在，存在则直接加载，不存在则下载后加载。
    返回: pandas.DataFrame 结构体
    """
    today_str = datetime.datetime.now().strftime("%Y%m%d")

    # 1. 在当前目录下，寻找包含今天日期的 .xlsx 文件
    current_dir = os.getcwd()
    expected_file = None

    # 遍历当前目录，看有没有名字里带今天日期且是 xlsx 的文件
    for file in os.listdir(current_dir):
        if today_str in file and file.endswith(".xlsx"):
            expected_file = os.path.join(current_dir, file)
            break

    # 判断并读取/下载
    if expected_file and os.path.exists(expected_file):
        print(f"检测到今日数据已存在本地: {expected_file}，直接加载...")
        # 2. 用 with 语句临时忽略 openpyxl 的特定 UserWarning
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", category=UserWarning, module="openpyxl"
            )
            df = pd.read_excel(expected_file)
        return df
    else:
        print("本地未检测到今日数据，开始启动线上下载...")
        file_path = download_csindex_industry_data()

        if file_path and os.path.exists(file_path):
            print("下载完成，开始转换成 Pandas DataFrame...")
            # 用 with 语句临时忽略 openpyxl 的特定 UserWarning
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
