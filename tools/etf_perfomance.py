import os
import time
import datetime
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from playwright.sync_api import sync_playwright

ETF_PATH = "https://www.csindex.com.cn/#/indices/family/detail?indexCode=931380"


def download_etf_weight_data(target_url=ETF_PATH):
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


def analyze_and_plot(file_path):
    """解析下载的权重Excel，在控制台完整打印，并绘制【宽屏横向延伸】的图表"""
    print(f"\n=================== 开始解析与绘图 ===================")
    print(f"正在读取文件: {file_path}")

    try:
        # 读取 Excel 数据
        df = pd.read_excel(file_path)

        # 模糊匹配列名
        name_col = next(
            (col for col in df.columns if "名称" in col and "成分" in col), None
        )
        if not name_col:
            name_col = next((col for col in df.columns if "简称" in col), df.columns[5])

        weight_col = next((col for col in df.columns if "权重" in col), df.columns[-1])

        # 数据清洗：转数值型，丢弃空值
        df[weight_col] = pd.to_numeric(df[weight_col], errors="coerce")
        df = df.dropna(subset=[name_col, weight_col])

        # 按权重从大到小排序（横着展示时，从左往右依次递减）
        sorted_df = df.sort_values(by=weight_col, ascending=False)

        if sorted_df.empty:
            print("❌ 数据为空，无法绘图。")
            return

        # ----------------- 1. 控制台全量打印 -----------------
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 1000)
        pd.set_option("display.max_colwidth", None)
        pd.set_option("display.expand_frame_repr", False)

        print(f"\n📊 --- 完整成分股权重列表 (共 {len(sorted_df)} 个) ---")
        print(sorted_df[[name_col, weight_col]].to_string(index=False))
        print("---------------------------------------------------\n")

        # ----------------- 2. 绘制【宽屏横向】图表 -----------------
        # 设置支持中文的字体
        plt.rcParams["font.sans-serif"] = [
            "SimHei",
            "Microsoft YaHei",
            "Arial Unicode MS",
        ]
        plt.rcParams["axes.unicode_minus"] = False

        # 【核心修改】动态计算宽度：每个成分股分配 0.4 英寸的宽度。
        # 如果有 50 只股，图表宽度就是 20 英寸；高度固定为 8 英寸，形成完美的“横向长条宽屏”效果
        num_items = len(sorted_df)
        dynamic_width = max(12, num_items * 0.4)

        fig, ax = plt.subplots(figsize=(dynamic_width, 8))

        names = sorted_df[name_col].values
        weights = sorted_df[weight_col].values

        # 使用 standard bar (垂直柱状图)，让图表向右横向延伸
        bars = ax.bar(names, weights, color="#5470C6", edgecolor="none", width=0.6)

        # 强制显示所有 x 轴标签，并倾斜 45 度，防止长名字重叠
        ax.set_xticks(range(num_items))
        ax.set_xticklabels(names, rotation=45, ha="right", fontsize=10)

        # 在每根柱子上方渲染具体数值（数值也旋转 90 度竖立起来，避免互相拥挤）
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.1,
                f"{height:.2f}%",
                va="bottom",
                ha="center",
                fontsize=9,
                rotation=90,
            )

        # 装饰图表
        ax.set_title(
            f"中证 931380 指数 - 全量成分股权重分布 (共 {num_items} 只)",
            fontsize=16,
            pad=25,
        )
        ax.set_ylabel("权重 (%)", fontsize=12)
        ax.set_xlabel("成分券名称", fontsize=12)
        ax.grid(axis="y", linestyle="--", alpha=0.6)  # 改为背景水平虚线

        # 限制 y 轴的最大值，给顶部的文字留出一点空白空间
        ax.set_ylim(0, max(weights) * 1.2)

        # 优化边框
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # 使用 tight 布局并保存
        img_name = os.path.splitext(file_path)[0] + "_横向宽屏可视化.png"
        plt.savefig(img_name, dpi=300, bbox_inches="tight")
        print(f"📊 宽屏分布图已完整生成并保存至: {img_name}")

        # 弹窗展示
        plt.show()

    except Exception as e:
        print(f"❌ 解析或绘图时发生错误: {e}")


def main():
    print("=================== 启动自动化爬取与分析流 ===================")

    # 1. 爬取并下载 Excel 权重文件
    excel_file = download_etf_weight_data()
    if not excel_file:
        print("❌ 自动化文件下载流程失败。")
        return

    print(f"主程序获取到的文件路径: {excel_file}")

    # 2. 读取并绘制图表
    analyze_and_plot(excel_file)


if __name__ == "__main__":
    main()
