import requests
import pandas as pd
from datetime import datetime, timedelta
import json

def get_latest_shfe_copper():
    """
    抓取上期所最近一个交易日的铜库存（阴极铜）
    """
    # 模拟真实浏览器，增加更多 Header 字段
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': 'https://www.shfe.com.cn/statements/dataview.html?paramid=dailywarrant',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 自动回溯 10 天，确保能跨越长假
    for i in range(10):
        target_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        # 注意：部分年份接口后缀可能是 .json 或 .dat，当前主用 .dat
        url = f"https://www.shfe.com.cn/reports/tradedata/dailyandweeklydata/"
        
        try:
            # 禁用代理影响，设置合理的超时
            response = requests.get(url, headers=headers, timeout=10, verify=True)
            
            if response.status_code == 404:
                continue
                
            if response.status_code == 200:
                # 某些情况下返回的内容开头会有不可见字符，进行 strip 处理
                raw_content = response.text.strip()
                data = json.loads(raw_content)
                
                records = data.get('Record', [])
                if not records:
                    continue

                # 核心过滤逻辑：
                # 1. VARNAME 包含 '铜'
                # 2. 排除掉汇总行（汇总行通常带有 '合计' 字样）
                # 3. 排除掉表格说明文字
                df_all = pd.DataFrame(records)
                
                # 确保字段存在
                if 'VARNAME' not in df_all.columns:
                    continue
                
                # 精准匹配阴极铜仓库数据
                df_cu = df_all[
                    (df_all['VARNAME'].str.contains('铜')) & 
                    (~df_all['VARNAME'].str.contains('合计')) &
                    (df_all['WARRANTS'].str.isnumeric()) # 确保仓单量是数字字符串
                ].copy()

                if df_cu.empty:
                    continue

                # 转换数值类型
                df_cu['WARRANTS'] = pd.to_numeric(df_cu['WARRANTS'])
                df_cu['WRCHANGE'] = pd.to_numeric(df_cu['WRCHANGE'])
                
                total = df_cu['WARRANTS'].sum()
                change = df_cu['WRCHANGE'].sum()

                print(f"🎯 成功匹配日期: {target_date}")
                print(f"📦 阴极铜总仓单: {total} 吨 ({'增加' if change >=0 else '减少'}: {abs(change)} 吨)")
                
                return {
                    'date': target_date,
                    'total': total,
                    'change': change,
                    'df': df_cu[['WHSE_ABBRNM', 'WARRANTS', 'WRCHANGE']]
                }
        except Exception as e:
            # 打印调试信息，正式运行时可以注释掉
            # print(f"尝试 {target_date} 时出错: {e}")
            continue

    print("❌ 错误：未能在最近 10 天内找到有效的库存数据文件。")
    print("可能原因：1. 接口 URL 变更；2. 触发了上期所 WAF 防火墙（需更换 IP）。")
    return None

if __name__ == "__main__":
    result = get_latest_shfe_copper()
    if result:
        print("\n--- 仓库分布明细 ---")
        print(result['df'].rename(columns={
            'WHSE_ABBRNM': '仓库',
            'WARRANTS': '仓单量',
            'WRCHANGE': '日增减'
        }).to_string(index=False))