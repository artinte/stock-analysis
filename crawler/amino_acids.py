import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import urllib3
from urllib.parse import urljoin

# 1. 屏蔽 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
                "固体蛋氨酸": r"固体蛋氨酸价格(\d+-\d+)元/吨",
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
            # 导出 CSV
            filename = f"caaa_data_{time.strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n成功！提取到 {len(self.data_list)} 条价格记录，已保存至 {filename}")
        else:
            print("\n抓取完成，但未发现匹配的价格数据。")

if __name__ == "__main__":
    spider = CAAASpider()
    # 抓取第 1 页到第 5 页（包含 index.html, 2.html, 3.html...）
    spider.run(start_page=1, end_page=5)