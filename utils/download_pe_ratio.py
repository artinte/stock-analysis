import datetime
import os
import shutil
import time
import warnings
import zipfile
import pandas as pd
from playwright.sync_api import sync_playwright

"""
==========================================================================================
脚本名称: download_csindex_pe.py
所属项目: stock-analysis (量化选股数据矩阵框架)
脚本功能: 自动化抓取中证指数官网(csindex.com.cn)行业市盈率(PE Ratio)数据压缩包，
          自动解压并解析导出为 Pandas DataFrame / Excel。

技术机制与避坑说明:
1. Zip 压缩包自动解压与识别:
   PERatio 页面导出的文件通常为 .zip 压缩包。脚本在拦截并保存 zip 文件后，会自动将其解压
   到指定的缓存目录，并检索出解压后的 Excel 或 CSV 表格文件。

2. Blob 管道拦截与防超时策略:
   继承原有 Playwright expect_download 拦截机制与 domcontentloaded 骨架加载放行策略，
   彻底解决前端动态 Blob 内存流无法直接通过 request/urllib 抓取的问题。

3. 本地缓存与自动清理机制:
   优先检测本地是否已包含今日解压好的表格数据，避免重复启动浏览器下载。
==========================================================================================
"""


def extract_and_get_data_file(zip_path, extract_dir):
    """解压 zip 文件并返回里面包含的数据文件路径（.xlsx, .xls, .csv）。"""
    print(f"正在解压文件: {zip_path} -> {extract_dir}")
    extracted_files = []

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
        for member in zip_ref.namelist():
            # 解决 zip 中文文件名乱码问题（如果有）
            try:
                filename = member.encode("cp437").decode("gbk")
            except Exception:
                filename = member

            full_path = os.path.join(extract_dir, member)
            if filename.endswith((".xlsx", ".xls", ".csv")):
                extracted_files.append(full_path)

    if extracted_files:
        print(f"成功找到解压后的数据文件: {extracted_files[0]}")
        return extracted_files[0]
    else:
        print("警告: 压缩包内未找到 Excel 或 CSV 文件。")
        return None


def download_csindex_pe_data(download_dir=os.getcwd()):
    """自动化下载中证行业市盈率 ZIP 压缩包并解压，返回解压后的表格文件绝对路径。

    失败返回 None。
    """
    target_url = "https://www.csindex.com.cn/#/dataService/PERatio"
    os.makedirs(download_dir, exist_ok=True)

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

        print("等待市盈率数据表格加载...")
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

        print("点击导出按钮，正在拦截并下载压缩包...")
        try:
            with page.expect_download(timeout=30000) as download_info:
                page.click(export_btn_selector)

            download = download_info.value
            today_str = datetime.datetime.now().strftime("%Y%m%d")

            suggested_name = download.suggested_filename
            if suggested_name:
                name_part, ext_part = os.path.splitext(suggested_name)
                zip_filename = f"{name_part}_{today_str}{ext_part}"
            else:
                zip_filename = f"中证行业市盈率数据_{today_str}.zip"

            zip_save_path = os.path.join(download_dir, zip_filename)
            download.save_as(zip_save_path)
            print(f"🎉 压缩包下载成功！保存至: {zip_save_path}")
            browser.close()

            # 判断下载的是否为 zip，进行对应处理
            if zip_save_path.endswith(".zip") or zipfile.is_zipfile(
                zip_save_path
            ):
                data_file_path = extract_and_get_data_file(
                    zip_save_path, download_dir
                )
                return data_file_path
            else:
                # 如果官网直接返回了未压缩的 Excel 文件
                return zip_save_path

        except Exception as e:
            print(f"下载/处理文件时遭遇错误: {e}")
            browser.close()
            return None


def read_data_file(file_path):
    """根据文件扩展名自动选择读取方式。"""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", category=UserWarning, module="openpyxl"
        )
        if file_path.endswith(".csv"):
            try:
                return pd.read_csv(file_path, encoding="utf-8-sig")
            except UnicodeDecodeError:
                return pd.read_csv(file_path, encoding="gbk")
        else:
            return pd.read_excel(file_path)


def get_csindex_pe_data(download_dir=os.getcwd(), force_update=False):
    """外部调用核心入口函数。

    参数:
        download_dir (str): 下载及解压文件的保存目录。默认为当前目录。
        force_update (bool): 是否强制重新下载。默认为 False。
    返回:
        pandas.DataFrame 结构体
    """
    today_str = datetime.datetime.now().strftime("%Y%m%d")

    # 1. 在本地寻找今日已经解压出来的 Excel / CSV 数据文件
    expected_file = None
    for file in os.listdir(download_dir):
        if (
            today_str in file
            and ("PERatio" in file or "市盈率" in file or "pe" in file.lower())
            and file.endswith((".xlsx", ".xls", ".csv"))
        ):
            expected_file = os.path.join(download_dir, file)
            break

    # 2. 判断并读取/下载
    if expected_file and os.path.exists(expected_file) and not force_update:
        print(
            f"检测到今日解压后的市盈率数据已存在本地: {expected_file}，直接加载..."
        )
        return read_data_file(expected_file)
    else:
        if force_update:
            print("已触发 [强制更新]，跳过本地缓存，开始启动线上下载...")
        else:
            print("本地未检测到今日市盈率数据，开始启动线上下载...")

        data_file_path = download_csindex_pe_data(download_dir=download_dir)

        if data_file_path and os.path.exists(data_file_path):
            print("数据准备就绪，开始转换为 Pandas DataFrame...")
            return read_data_file(data_file_path)
        else:
            raise FileNotFoundError(
                "未能成功获取并解压中证行业市盈率数据，无法转换为 DataFrame。"
            )


# 测试当前文件运行情况
if __name__ == "__main__":
    try:
        df_pe = get_csindex_pe_data()
        print("\n--- 成功获取行业市盈率数据前 5 行预览 ---")
        print(df_pe.head())
        print(f"数据总行数: {len(df_pe)}")
    except Exception as ex:
        print(f"运行失败: {ex}")