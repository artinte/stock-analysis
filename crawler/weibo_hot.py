

import requests
import pandas as pd
from datetime import datetime

def get_weibo_hot_search():
    # 微博热搜 H5 端接口地址
    url = "https://weibo.com/ajax/side/hotSearch"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://s.weibo.com/top/summary?cate=realtimehot",
        "Accept": "application/json, text/plain, */*"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 提取热搜列表
        hot_list = data.get('data', {}).get('realtime', [])
        
        results = []
        for index, item in enumerate(hot_list):
            # 过滤掉广告（有些条目没有 rank）
            if 'rank' not in item and index != 0:
                continue
                
            title = item.get('word', '')
            num = item.get('num', 0) # 热度值
            
            results.append({
                "排名": item.get('rank', 0) if 'rank' in item else "置顶",
                "标题": title,
                "热度值": num,
            })
            
        return results

    except Exception as e:
        print(f"爬取失败: {e}")
        return []

if __name__ == "__main__":
    hot_data = get_weibo_hot_search()
    
    if hot_data:
        df = pd.DataFrame(hot_data)
        print(f"--- 微博热搜榜 ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---")
        print(df.to_string(index=False))
        
        # 可选：保存到 Excel
        # df.to_excel("weibo_hot.xlsx", index=False)
    else:
        print("未获取到数据")