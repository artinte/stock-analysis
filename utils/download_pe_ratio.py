import datetime
import os
import time
import warnings
import zipfile
import pandas as pd
from playwright.sync_api import sync_playwright

"""
==========================================================================================
脚本名称: download_csindex_pe.py
所属项目: stock-analysis (量化选股数据矩阵框架)
脚本功能: 自动化抓取中证指数官网(csindex.com.cn)行业估值指标压缩包。
          解压后将 Excel 中的 5 个工作表（静态市盈率、滚动市盈率、市净率、股息率、个股数据）
          分别独立解析，并以字典形式返回：
          {
              '行业静态市盈率': DataFrame,
              '行业滚动市盈率': DataFrame,
              '行业市净率':   DataFrame,
              '行业股息率':   DataFrame,
              '个股数据':     DataFrame
          }
==========================================================================================
"""


def extract_and_get_data_file(zip_path, extract_dir):
    """解压 zip 文件并返回里面包含的数据表格文件路径。"""
    print(f"正在解压文件: {zip_path} -> {extract_dir}")
    extracted_files = []

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
        for member in zip_ref.namelist():
            try:
                filename = member.encode("cp437").decode("gbk")
            except Exception:
                filename = member

            full_path = os.path.join(extract_dir, member)
            if filename.endswith((".xlsx", ".xls", ".csv")):
                extracted_files.append(full_path)

    if extracted_files:
        print(f"解压成功，定位到表格文件: {extracted_files[0]}")
        return extracted_files[0]
    else:
        print("错误: 压缩包内未找到有效表格文件。")
        return None


def download_csindex_pe_data(download_dir=os.getcwd(), category="csindex"):
    """自动化下载中证行业估值数据压缩包并解压。"""
    target_url = "https://www.csindex.com.cn/#/dataService/PERatio"
    os.makedirs(download_dir, exist_ok=True)

    tab_text = "中上协行业分类" if category == "csrc" else "中证行业分类"
    category_label = "中上协" if category == "csrc" else "中证"

    with sync_playwright() as p:
        print(f"正在启动浏览器 [目标分类: {tab_text}]...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"正在打开网页: {target_url}")
        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"网页加载提醒: {e}")

        time.sleep(5)

        # 1. 切换行业分类 Tab
        tab_selector = f"text='{tab_text}'"
        print(f"切换分类标签: [{tab_text}]...")
        try:
            page.wait_for_selector(tab_selector, timeout=15000)
            page.click(tab_selector)
            time.sleep(2)
        except Exception as e:
            print(f"提示: 点击标签无需重复操作或遇到微小延迟: {e}")

        # 2. 定位“导出数据”按钮
        export_btn_selector = "button:has-text('导出数据')"
        print("定位 [导出数据] 按钮...")
        try:
            page.wait_for_selector(export_btn_selector, timeout=15000)
        except Exception:
            print("错误: 未能在 15 秒内找到导出按钮。")
            browser.close()
            return None

        # 3. 拦截并下载压缩包
        print("点击导出，拦截并保存压缩包...")
        try:
            with page.expect_download(timeout=30000) as download_info:
                page.click(export_btn_selector)

            download = download_info.value
            today_str = datetime.datetime.now().strftime("%Y%m%d")

            suggested_name = download.suggested_filename
            if suggested_name:
                name_part, ext_part = os.path.splitext(suggested_name)
                zip_filename = f"{name_part}_{category_label}_{today_str}{ext_part}"
            else:
                zip_filename = f"行业估值数据_{category_label}_{today_str}.zip"

            zip_save_path = os.path.join(download_dir, zip_filename)
            download.save_as(zip_save_path)
            print(f"🎉 压缩包保存成功: {zip_save_path}")
            browser.close()

            if zip_save_path.endswith(".zip") or zipfile.is_zipfile(zip_save_path):
                return extract_and_get_data_file(zip_save_path, download_dir)
            else:
                return zip_save_path

        except Exception as e:
            print(f"下载过程遭遇错误: {e}")
            browser.close()
            return None


def read_separated_sheets(file_path):
    """读取 Excel 所有 Sheet，拆分为 5 个独立的 DataFrame 字典输出。"""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

        if file_path.endswith(".csv"):
            try:
                df = pd.read_csv(file_path, encoding="utf-8-sig")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="gbk")
            return {"全量数据": df}

        # 读取全部 Sheet，返回 {sheet_name: dataframe} 字典
        excel_sheets = pd.read_excel(file_path, sheet_name=None)
        print(f"读取到的工作表列表: {list(excel_sheets.keys())}")

        parsed_data = {}
        for sheet_name, df in excel_sheets.items():
            clean_name = sheet_name.strip()

            # 匹配 5 个主要分页
            if "静态" in clean_name or "静态市盈率" in clean_name:
                parsed_data["行业静态市盈率"] = df
            elif "滚动" in clean_name or "TTM" in clean_name or "滚动市盈率" in clean_name:
                parsed_data["行业滚动市盈率"] = df
            elif "市净率" in clean_name or "PB" in clean_name:
                parsed_data["行业市净率"] = df
            elif "股息率" in clean_name:
                parsed_data["行业股息率"] = df
            elif "个股" in clean_name or "股票" in clean_name:
                parsed_data["个股数据"] = df
            else:
                parsed_data[clean_name] = df

        return parsed_data


def get_csindex_pe_data(download_dir=os.getcwd(), category="csindex", force_update=False):
    """外部调用核心入口函数。

    参数:
        download_dir (str): 保存目录。
        category (str): 'csindex' (中证行业分类) 或 'csrc' (中上协行业分类)。
        force_update (bool): 是否强制线上重新下载。
    返回:
        dict: 包含 5 个独立 DataFrame 的字典
    """
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    category_label = "中上协" if category == "csrc" else "中证"

    expected_file = None
    for file in os.listdir(download_dir):
        if (
            today_str in file
            and category_label in file
            and file.endswith((".xlsx", ".xls", ".csv"))
        ):
            expected_file = os.path.join(download_dir, file)
            break

    if expected_file and os.path.exists(expected_file) and not force_update:
        print(f"检测到今日 [{category_label}行业分类] 缓存文件: {expected_file}，开始解析...")
        return read_separated_sheets(expected_file)
    else:
        if force_update:
            print(f"触发强制更新，启动线上下载 [{category_label}行业分类]...")
        else:
            print(f"未检测到今日缓存，启动线上下载 [{category_label}行业分类]...")

        data_file_path = download_csindex_pe_data(download_dir=download_dir, category=category)

        if data_file_path and os.path.exists(data_file_path):
            print("数据文件解压完成，正在分类拆解 5 个 Sheet...")
            return read_separated_sheets(data_file_path)
        else:
            raise FileNotFoundError(
                f"未能成功下载/解压 [{category_label}] 估值数据。"
            )


# 测试当前脚本
if __name__ == "__main__":
    try:
        # 获取拆分后的 5 个数据表字典
        data_dict = get_csindex_pe_data(category="csindex")

        print("\n================== 数据拆解结果 ==================")
        for name, df in data_dict.items():
            print(f"📌 表格类型: [{name}] | 数据行数: {len(df)}")

        # 示例：提取单独的 DataFrame 进行分析
        if "行业静态市盈率" in data_dict:
            df_static_pe = data_dict["行业静态市盈率"]
            print("\n--- 行业静态市盈率前 3 行预览 ---")
            print(df_static_pe.head(3))

        if "个股数据" in data_dict:
            df_stock = data_dict["个股数据"]
            print("\n--- 个股数据前 3 行预览 ---")
            print(df_stock.head(3))

    except Exception as ex:
        print(f"运行失败: {ex}")