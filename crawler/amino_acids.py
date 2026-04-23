import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import urllib3
from urllib.parse import urljoin
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

"""
目标站点：饲料添加剂价格行情
URL 模式： https://www.caaa.cn/html/fw/market/slyl/2026/0409/23122.html
数据点：70%赖氨酸价格、98%赖氨酸价格、固体蛋氨酸价格、苏氨酸价格、山东色氨酸价格
挑战点：
1. 日期提取：日期不在正文，而是隐含在 URL 中，需要从链接中解析出日期信息。
2. 数据格式：价格通常以 "4800-5200元/吨" 的格式出现，需要提取数值并计算平均价。
3. 网站结构：老旧网站结构复杂，可能存在多层嵌套，需要灵活的解析策略。
4. 数据清洗：需要剔除无效数据行，确保绘图数据的准确性。
"""


# 设置中文支持
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

# 1. 屏蔽 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def plot_dataframe(df):
    if df is None or df.empty:
        print("❌ 数据集为空")
        return

    plot_df = df.copy()

    # --- 1. 核心修正：从链接提取日期 ---
    # 链接样例: https://www.caaa.cn/html/fw/market/slyl/2026/0409/23122.html
    # 提取结果: 2026/0409
    def extract_date_from_url(url):
        match = re.search(r'/(\d{4})/(\d{4})/', str(url))
        if match:
            year = match.group(1)
            month_day = match.group(2)
            return f"{year}-{month_day[:2]}-{month_day[2:]}"
        return None

    plot_df['date_dt'] = pd.to_datetime(plot_df['链接'].apply(extract_date_from_url), errors='coerce')
    
    # 剔除无效日期并按时间排序
    plot_df = plot_df.dropna(subset=['date_dt']).sort_values('date_dt')

    if plot_df.empty:
        print("❌ 日期提取失败，请检查链接格式。")
        return

    # --- 2. 绘图 ---
    plt.figure(figsize=(12, 7))
    
    # 你样例中的列名
    target_cols = ["70%赖氨酸", "98%赖氨酸", "苏氨酸", "固体蛋氨酸"]
    has_data = False

    for col in target_cols:
        if col in plot_df.columns:
            # 过滤掉非数字行
            mask = plot_df[col].astype(str).str.contains(r'\d+-\d+')
            sub_df = plot_df[mask].copy()
            
            if not sub_df.empty:
                # 拆分 4800-5200 取均值
                prices = sub_df[col].str.extract(r'(\d+)-(\d+)')
                sub_df['avg'] = (prices[0].astype(float) + prices[1].astype(float)) / 2
                
                plt.plot(sub_df['date_dt'], sub_df['avg'], label=col, marker='o', markersize=4)
                has_data = True

    if not has_data:
        print("❌ 虽然日期对了，但价格列的数据格式无法解析成数字。")
        return

    # --- 3. 美化 ---
    plt.title('饲料添加剂价格走势图 (由 URL 自动解析日期)', fontsize=14)
    plt.ylabel('平均价 (元/吨)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    
    # 优化日期显示
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    plt.savefig('market_report.png', dpi=300)
    print("✅ 绘图成功！请查看当前目录下的 market_report.png")
    plt.show()

class CAAASpider:
    def __init__(self):
        # 基础栏目路径
        self.base_dir_url = "https://www.caaa.cn/html/fw/market/slyl/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.data_list = []

    def get_article_links(self, page_num=1):
        """适配该站特殊的 2.html, 3.html 分页逻辑"""
        if page_num == 1:
            url = urljoin(self.base_dir_url, "index.html")
        else:
            # 关键：由于你观察到的是 2.html，这里直接拼接数字
            url = urljoin(self.base_dir_url, f"{page_num}.html")
            
        print(f"正在扫描列表页: {url}")
        
        try:
            res = requests.get(url, headers=self.headers, verify=False, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')
            
            links = []
            # 这种老网站链接通常在 td 标签内的 a 标签里
            all_a = soup.find_all('a', href=True)
            
            for a in all_a:
                href = a['href']
                # 提取包含日期的路径特征，例如 /2026/0120/xxxxx.html
                if re.search(r'/\d{4}/\d{4}/', href):
                    full_url = urljoin(url, href)
                    links.append(full_url)
            
            unique_links = list(set(links))
            print(f"本页找到 {len(unique_links)} 个详情页链接")
            return unique_links
        except Exception as e:
            print(f"扫描列表页失败: {e}")
            return []

    def parse_detail(self, url):
        """精准提取正文价格数据"""
        try:
            res = requests.get(url, headers=self.headers, verify=False, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')
            
            # 针对该站点的正文定位：尝试最广泛的文本获取
            # 老网站经常把内容放在 td 标签里，这里直接取 body 文本进行正则匹配最稳妥
            text = soup.get_text()
            title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "无标题"
            
            # 定义匹配目标
            targets = {
                "70%赖氨酸": r"70%赖氨酸价格(\d+-\d+)元/吨",
                "98%赖氨酸": r"98%赖氨酸价格(\d+-\d+)元/吨",
                # "固体蛋氨酸": r"固体蛋氨酸价格(\d+-\d+)元/吨",
                "苏氨酸": r"苏氨酸价格(\d+-\d+)元/吨",
                "山东色氨酸": r"山东色氨酸价格(\d+-\d+)元/吨"
            }
            
            row = {"日期标题": title, "链接": url}
            found_any = False
            for name, pattern in targets.items():
                m = re.search(pattern, text)
                if m:
                    row[name] = m.group(1)
                    found_any = True
                else:
                    row[name] = "N/A"
            
            return row if found_any else None
        except:
            return None

    def run(self, start_page=1, end_page=3):
        """运行爬虫"""
        for i in range(start_page, end_page + 1):
            links = self.get_article_links(i)
            if not links:
                continue
                
            for link in links:
                print(f"  正在解析: {link.split('/')[-1]}")
                data = self.parse_detail(link)
                if data:
                    self.data_list.append(data)
                time.sleep(0.5)

        if self.data_list:
            df = pd.DataFrame(self.data_list)
            plot_dataframe(df)  # 直接传 DataFrame 给绘图函数
            # 导出 CSV
            filename = f"caaa_data_{time.strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n成功！提取到 {len(self.data_list)} 条价格记录，已保存至 {filename}")
        else:
            print("\n抓取完成，但未发现匹配的价格数据。")

if __name__ == "__main__":
    spider = CAAASpider()
    # 抓取第 1 页到第 5 页（包含 index.html, 2.html, 3.html...）
    spider.run(start_page=1, end_page=1)