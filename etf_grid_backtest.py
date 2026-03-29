from dotenv import dotenv_values
from gateways.data_manager import DataManager
import requests
import pandas as pd
from io import BytesIO

"""
中证A500指数：https://www.csindex.com.cn/#/indices/family/detail?indexCode=000510

本ETF主要研究中证A500指数，它从各行业选取市值较大、流动性较好的500只证券作为指数样本，以反映各行业最具代表性上市公司证券的整体表现。

从2026年3月27日来看，中证A500不是一只适合长期定投的ETF，近五年的年化收益为 -0.44%，意味着你五年前的今天投进去100万，至今仍然亏损 4400 元。
这就是股票市场的残酷现实，你不仅没挣钱，还要承担有些时间 20% 以上的损失。

所以必须要改变策略，要学会低吸高抛，在价格较低的时候买入，在价格较高的时候卖出，才能在这个市场中生存下来。以下是基于低吸高抛的动态底仓与高频网格实战策略：

中证 A500 指数：动态底仓与高频网格实战策略

一、 市场真相：为什么要改变策略？

参考指数：
该指数选取了各行业市值大、流动性好的 500 只龙头，反映中国核心资产的整体表现。

残酷数据：截至 2026 年 3 月 27 日，中证 A500 近五年的年化收益率为 -0.44%。

扎心现实：五年前投入 100 万，今天依然亏损 4400 元。你不仅没赚到钱，还在这五年间承担了多次超过 20% 的大幅回撤压力。

结论：A 股核心资产不是简单的“定投天堂”。 如果只会死拿，你就在拿真金白银去忍受毫无回报的波动。必须改变策略，变“死拿”为“低吸高抛”。

二、 核心实战模型：15k - 150k 动态防御系统

我们要利用 A500 每日频繁的“电梯行情”，通过高频小单持续收割利润。

1. 仓位控制（生命线）
为了确保“涨有票卖、跌有钱买”，设定严格的底仓运行区间：

最低底仓 (15,000 股)：持仓市值的下限。无论市场涨多高，永远保留 1.5 万的筹码，确保不踏空，保留对未来牛市的参与权。

最高持仓 (150,000 股)：持仓市值的上限。在极端下跌行情中，允许通过网格不断加仓至 15 万（包含预留资金），这是防御深度的极限，防止单边下跌导致无限接盘。

动态核心：让持仓市值在 1.5 万至 15 万 之间随波动灵活伸缩，形成一个“不倒翁”结构。

2. 网格参数设定
执行标的：中证 A500 ETF（如易方达、广发等流动性极佳的品种）。

单笔金额：2000 股（以目前 1.2 元单价来看，大概要投入 2400 元，小步慢跑，降低单次博弈风险）。

买入间距：0.56%（下跌触发）。

卖出间距：0.59%（上涨触发）。

实战频率：目标日均成交 4 次（2 买 2 卖）。



三、 收益预测与逻辑对冲

1. 波动增厚 vs 银行利息
单日目标：2 次卖出成功，产生利润约 23 元。

年化预估：23 元 × 240 交易日 ≈ 5,520 元。

对冲价值：即便指数价格一年内一分钱不涨，这 5.5% 的额外收益也足以秒杀 2.5% 的银行定期利息，并有效覆盖指数回撤带来的心理压力。

2. 策略优势
自动去弱留强：A500 指数每半年自动剔除像“海格通信”这类财务恶化的个股，换入绩优龙头。你无需操心个股爆雷，只需专注于指数波动。

科学避坑：通过 2,000 元的小额切分，避开了 2021 年宁德时代 100 倍 PE 时的那种盲目梭哈，用“时间的玫瑰”换成“波动的收割”。


四、 策略优化：通道识别与动态应对（核心进阶）

虽然单笔 2,000 元固定，但执行节奏应根据通道经验进行微调，以应对不同行情：

1. 震荡行情（无明显趋势）
特征：价格在水平区间波动，RSI 在 30-70 之间。

对策：严格执行 0.56% / 0.59%。这是网格最肥美的时期，无需干预，让系统自动刷单。

2. 上升通道（多头占优）
特征：均线向上，高点不断创新高。

优化逻辑：“缓买快卖”。

调大买入间距（如 0.8%）：防止回撤过小时过早补仓，保留子弹。

调小卖出间距（如 0.4%）：在上涨中更频繁地止盈，把浮盈变成现金。

目的：在上升趋势中不断提高底仓的安全性。

3. 下降通道（空头占优）
特征：阴线多于阳线，重心下移。

优化逻辑：“慎买缓卖”。

调大买入间距（如 1.2% - 1.5%）：防止在单边下跌中由于网格过密而过快打满 15 万股上限。

调大卖出间距：不急于反弹一点就跑，等待更厚实的价差出现。

目的：拉长补仓距离，增加抗跌深度，应对像 2021 年宁德时代那种“估值回归”的杀伤力。

五、 结语

“死拿是信仰，网格是生意。”
在 A 股这种“牛短熊长”的环境里，价格是虚的，只有落袋的波动利润才是实的。10 万资金分成 50 份，在 1.5 万到 15 万的区间里反复“摩擦”，这才是应对中证 A500 最理性的生存方式。

"""


A500_URL = "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/closeweight/000510closeweight.xls"


def get_a500_components(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 1. 直接从网络读取到内存
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        file_content = BytesIO(response.content)

        # 2. 常规读取逻辑：先尝试 Excel，失败则尝试 HTML
        try:
            df = pd.read_excel(file_content)
        except Exception:
            # 中证官网文件经常是 HTML 伪装的 .xls
            df = pd.read_html(file_content)[0]

        # 3. 标准化清洗 (提取核心列)
        # 注意：中证文件的列名通常是：'成份券代码', '成份券名称', '权重(%)'
        # 或者是英文：'Constituent Code', 'Constituent Name', 'Weight(%)'

        # 自动识别列名（取包含代码、名称、权重的列）
        target_cols = {
            "code": [c for c in df.columns if "成份券代码" in str(c) or "Constituent Code" in str(c)][0],
            "name": [c for c in df.columns if "成份券名称" in str(c) or "Constituent Name" in str(c)][0],
            "weight": [c for c in df.columns if "权重" in str(c) or "Weight" in str(c)][
                0
            ],
        }

        result = df[
            [target_cols["code"], target_cols["name"], target_cols["weight"]]
        ].copy()
        result.columns = ["Stock_Code", "Stock_Name", "Weight_Percent"]

        # 4. 代码补全 (如 1 变为 000001)
        result["Stock_Code"] = result["Stock_Code"].astype(str).str.zfill(6)

        return result

    except Exception as e:
        print(f"提取失败: {e}")
        return None


def main():
    config = dotenv_values("private_config.txt")
    dm = DataManager(provider_name="yinhe")

    if dm.start(config):
        try:
            a500_df = get_a500_components(A500_URL)
            if a500_df is not None:
                print("中证A500成分股及权重：")
                print(a500_df.head(10))  # 打印前10行预览
            else:
                print("未能获取到有效的成分股数据。")

        except Exception as e:
            print("数据获取失败：", e)
        finally:
            dm.stop()


if __name__ == "__main__":
    main()
