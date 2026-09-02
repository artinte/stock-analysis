"""
中证指数行业分类数据下载与读取。

本模块负责获取中证指数有限公司发布的行业分类数据，
并统一转换为 Pandas DataFrame，供股票行业分类、行业分析
及量化选股模块使用。

数据来源：
    中证指数有限公司
    https://www.csindex.com.cn/

主要功能：
    1. 自动访问中证指数行业分类页面。
    2. 自动下载最新行业分类 Excel 文件。
    3. 按月份缓存本地数据，避免重复下载。
    4. 本月已有缓存时直接读取本地文件。
    5. 支持 force_update 强制重新下载。
    6. 自动将 Excel 数据转换为 Pandas DataFrame。

缓存策略：
    行业分类数据更新频率较低，因此以“月份”为缓存周期。

    默认情况下：
        - 本月已有 Excel 文件 → 直接读取。
        - 本月没有 Excel 文件 → 自动下载。
        - force_update=True → 忽略本地缓存，重新下载。

主要接口：
    download_csindex_industry_data()
        下载中证行业分类 Excel 文件。

    get_csindex_industry_data()
        获取中证行业分类 DataFrame。
        优先使用本月本地缓存，不存在时自动下载。

返回：
    pandas.DataFrame

异常：
    下载失败或无法获取有效数据时，
    get_csindex_industry_data() 会抛出 FileNotFoundError。
"""

import os
import time
import datetime
import pandas
import warnings
import concurrent.futures
from playwright.sync_api import sync_playwright


def download_csindex_industry_data(
    download_dir: str | None = None,
) -> str | None:
    """自动化下载中证行业数据，并返回保存的文件绝对路径。

    如果下载失败，返回 None。
    """
    target_url = "https://www.csindex.com.cn/#/dataService/industryClassification"

    if download_dir is None:
        download_dir = os.path.join(os.getcwd(), "temp")

    os.makedirs(download_dir, exist_ok=True)

    with sync_playwright() as p:
        print("正在启动自动化浏览器...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
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


def get_csindex_industry_data(
    download_dir: str | None = None,
    force_update: bool = False,
) -> pandas.DataFrame:
    """
    获取中证指数行业数据。

    Args:
        download_dir: 下载文件保存目录。
        force_update: 是否强制更新。

    Returns:
        行业数据。
    """
    if download_dir is None:
        download_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(download_dir, exist_ok=True)

    month_str = datetime.datetime.now().strftime("%Y%m")

    expected_file = None
    for file in os.listdir(download_dir):
        if month_str in file and file.endswith(".xlsx"):
            expected_file = os.path.join(download_dir, file)
            break

    if expected_file and os.path.exists(expected_file) and not force_update:
        print(f"检测到本月数据已存在本地: {expected_file}，直接加载...")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
            df = pandas.read_excel(expected_file)
        return df
    else:
        if force_update:
            print("已触发 [强制更新]，跳过本地缓存，开始启动线上下载...")
        else:
            print("本地未检测到本月数据，开始启动线上下载...")

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
                df = pandas.read_excel(file_path)
            return df
        else:
            raise FileNotFoundError(
                "未能成功下载中证行业分类数据，无法转换为 DataFrame。"
            )
