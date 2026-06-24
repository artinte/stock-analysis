import os
import time
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

        # 【优化 1】：将等待条件从 "networkidle" 改为 "domcontentloaded"（只等网页骨架加载完）
        # 同时手动设置一个稍微宽松点的整体加载超时时间（45秒）
        print(f"正在打开网页: {target_url}")
        try:
            page.goto(
                target_url, wait_until="domcontentloaded", timeout=45000
            )
        except Exception as e:
            print(f"网页基础加载遇到警告（不影响后续操作）: {e}")

        # 【优化 2】：给页面一个硬性的缓冲时间，让 JavaScript 把表格里的动态数据渲染出来
        print("等待数据表格加载...")
        time.sleep(5)

        # 定位“导出数据”按钮
        export_btn_selector = "button:has-text('导出数据')"

        print("正在定位 [导出数据] 按钮...")
        try:
            # 按钮最多等 15 秒
            page.wait_for_selector(export_btn_selector, timeout=15000)
        except Exception:
            print(
                "错误：页面虽然打开了，但等了 15 秒都没看到 [导出数据] 按钮，可能页面正在加载中或结构变了。"
            )
            browser.close()
            return

        print("点击导出按钮，正在拦截并下载 Excel 文件...")
        try:
            with page.expect_download(timeout=30000) as download_info:
                page.click(export_btn_selector)

            download = download_info.value
            filename = download.suggested_filename
            if not filename:
                filename = f"中证行业分类数据_{int(time.time())}.xlsx"

            save_path = os.path.join(os.getcwd(), filename)
            download.save_as(save_path)
            print(f"🎉 自动化爬取成功！文件已保存至: {save_path}")

        except Exception as e:
            print(f"下载文件时遭遇错误: {e}")

        browser.close()


if __name__ == "__main__":
    download_csindex_industry_data()