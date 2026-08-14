
StockInsight

个股综合研究平台

技术：Python FastAPI + Vue3 + TypeScript + ECharts




01：股票概览

一个股票就是一个完整的信息中心。

股票
 ↓
基本信息
 ↓
公司
 ↓
行业
 ↓
指数
 ↓
ETF
 ↓
行情
 ↓
估值
 ↓
财务
 ↓
股东
 ↓
机构
 ↓
新闻
 ↓
公告
 ↓
研报
 ↓
事件
 ↓
竞争对手
 ↓
产业链
 ↓
技术面
 ↓
基本面
 ↓
估值分析
 ↓
投资逻辑


---


二、最核心的页面：股票详情页

例如以后你输入：

601117

或者：

中国化学

最终进入：

/stock/601117

页面大概应该长这样：

┌──────────────────────────────────────────────────────────┐
│ 🔍 搜索股票： 中国化学 / 601117                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 中国化学 601117.SH                                      │
│ 中国化学工程股份有限公司                                │
│                                                          │
│ 当前价格   涨跌幅   市值   PE-TTM   PB   股息率          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│ [概览] [行情] [估值] [财务] [行业] [指数] [ETF]         │
│ [股东] [机构] [新闻] [公告] [研报] [产业链] [事件]       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                  当前页面内容                            │
│                                                          │
└──────────────────────────────────────────────────────────┘

这里最重要的一点：

不要把所有东西全部堆在一个页面。

而是：

一个股票 + 多个研究维度。


---

三、我建议股票主页至少设计成 15 个模块

这个项目以后可以非常大。

第一版先把框架全部留好。

01：股票概览

这是打开股票之后首先看到的东西。

中国化学
601117.SH


公司全称
上市日期
所属交易所
所属板块
证券简称
证券代码
公司官网
实际控制人
最终控制人
注册资本
公司地址

然后是行情摘要：

最新价格
今日涨跌
涨跌幅
成交量
成交额
换手率
总市值
流通市值


---


四、02：基本面

这是一个独立模块。

基本面
────────────────────


营业收入
营业收入增长率


归母净利润
净利润增长率


扣非净利润
扣非净利润增长率


毛利率
净利率
ROE
ROA
资产负债率
经营现金流
自由现金流

然后做趋势：

营收趋势


2021 ───
2022 ─────
2023 ───────
2024 ─────────
2025 ───────────

净利润也一样。


----



五、03：估值

这个模块我建议以后做得非常强。

因为你本身就很关注PE。

页面：

估值
────────────────────────


PE-TTM
PE-静态
PE-动态


PB
PS
PEG


股息率
EV/EBITDA


当前PE
历史PE


5年PE分位
10年PE分位


行业PE
行业PB
行业股息率

然后：

         当前
          ↓
PE ─────────────────────
       │
       │       ●
       │
       └──────────────────
        2021 22 23 24 25 26

以后可以继续加入：

估值分位

行业估值比较

历史估值比较

同类公司估值比较


---


六、04：行情

这个模块单独做。

行情


[分时] [日K] [周K] [月K]


[前复权] [后复权] [不复权]

下面：

成交量
成交额
换手率
振幅
最高
最低

然后增加：

MA5
MA10
MA20
MA60
MA120
MA250


MACD
RSI
KDJ
BOLL

但是：

这些先不要实现。

现在只把组件位置留出来。


---

七、05：行业

这个模块非常重要。

例如中国化学：

行业


申万行业
中证行业
中上协行业
自定义行业


一级行业
二级行业
三级行业

然后：

行业排名


行业市值排名
行业营收排名
行业利润排名
行业ROE排名
行业PE排名

最重要的是：

行业内股票比较

例如：

化工行业


公司        PE     PB     ROE    利润增速
中国化学
万华化学
……

以后可以一键：

“和同行比较”


---



八、06：指数

这个就是你刚才说的中证指数真正应该放的位置。

不是：

打开中证指数网站研究5000个指数。

而是：

输入一只股票 → 自动告诉我它属于哪些指数。

例如：

所属指数


中证A500
中证XXX
中证XXX
沪深XXX

每个指数可以点击。

进入：

指数详情


指数名称
指数代码
指数类型
当前点位


成分股
行业分布
前十大权重
PE
PB
股息率
九、07：E


---

九、07：ETF

这个模块你一定会用得上。

逻辑：

股票 → 哪些ETF持有它

例如：

ETF持仓


ETF名称              股票权重
────────────────────────────
ETF A                 2.31%
ETF B                 1.82%
ETF C                 0.95%

然后进一步：

ETF规模
ETF成交额
ETF份额
ETF跟踪指数
ETF行业

再反向：

哪些ETF和这只股票高度相关？

这以后非常有用。


---


十、08：股东

单独一个页面。

股东结构


控股股东
实际控制人


十大股东


股东名称
持股数量
持股比例
持股变化


十大流通股东

再做：

股东变化历史

例如：

2025Q1
2025Q2
2025Q3
2025Q4
2026Q1
2026Q2

---

十一、09：机构

这个以后可以做得非常强。

机构持仓


基金
社保
保险
QFII
券商
北向资金

以及：

机构数量
机构持仓比例
机构增减仓

以后可以继续做：

机构持仓趋势


---

十二、10：新闻

你说的：

最近的走势、新闻

这里一定要单独做。

例如：

新闻


2026-08-14
中国化学……


2026-08-13
中国化学……


2026-08-12
……


[全部新闻]

分类：

全部
公司
行业
政策
宏观
海外
技术
市场

以后再增加：

AI新闻摘要

新闻情绪

新闻重要程度

新闻影响分析



---


十三、11：公告

这个必须和新闻分开。

公告


定期报告
业绩预告
业绩快报
重大合同
股权变动
关联交易
对外投资
分红
回购
减持
增持

以后可以做：

公告自动分类

例如：

🟢 利好
🟡 中性
🔴 利空

但这是后面的事情。


---



十四、12：研报

单独一个模块：

研报


券商
发布日期
标题
评级
目标价


[研报摘要]

以后：

AI自动提取

核心观点
盈利预测
风险
目标价
估值


---

十五、13：产业链

这个我特别建议你预留。

例如中国化学：

产业链


上游
────────────
原材料
设备
能源


        ↓


中国化学


        ↓


下游
────────────
己二腈
尼龙66
气凝胶
……

以后可以逐步加入：

上游供应商

下游客户

竞争对手

产品价格

产能

行业供需



---


十六、14：事件

把股票相关的重大事件单独抽出来。

例如：

事件时间轴


2026-08
重大项目


2026-07
重大合同


2026-06
业绩


2026-05
投资项目


2026-04
产能变化

这个功能以后会非常漂亮。


---


十七、15：投资分析

这是最后一层。

不是数据，而是：

把前面的数据变成结论。

例如：

投资分析


估值
★★★★☆


成长
★★★☆☆


盈利能力
★★★☆☆


行业地位
★★★★☆


现金流
★★★☆☆


分红
★★★★☆


景气度
★★★☆☆

然后：

核心逻辑


1. 传统工程业务提供基本盘
2. T+EPC可能提升商业模式
3. 新材料提供第二增长曲线
4. 当前估值较低

当然，这部分以后再做。


---


十八、所以整个网站应该是这个结构
A股股票研究终端
│
├── 首页
│   ├── 股票搜索
│   ├── 最近浏览
│   ├── 自选股
│   └── 市场概览
│
├── 股票
│   └── :symbol
│       │
│       ├── 概览
│       ├── 基本信息
│       ├── 行情
│       ├── 估值
│       ├── 财务
│       ├── 行业
│       ├── 指数
│       ├── ETF
│       ├── 股东
│       ├── 机构
│       ├── 新闻
│       ├── 公告
│       ├── 研报
│       ├── 产业链
│       ├── 竞争对手
│       ├── 事件
│       └── 投资分析
│
├── 行业
│   ├── 行业列表
│   ├── 行业估值
│   ├── 行业排名
│   └── 行业股票
│
├── 指数
│   ├── 指数列表
│   ├── 指数详情
│   └── 指数成分
│
├── ETF
│   ├── ETF列表
│   ├── ETF详情
│   └── ETF持仓
│
├── 新闻
│   ├── 新闻列表
│   └── 新闻搜索
│
├── 自选
│   ├── 自选股
│   └── 自选分组
│
└── 系统
    ├── 数据源
    ├── 数据更新
    ├── 日志
    └── 配置


---

十九：后端


backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   ├── stocks.py
│   │   ├── market.py
│   │   ├── valuation.py
│   │   ├── financial.py
│   │   ├── industry.py
│   │   ├── indices.py
│   │   ├── etf.py
│   │   ├── shareholders.py
│   │   ├── institutions.py
│   │   ├── news.py
│   │   ├── announcements.py
│   │   ├── reports.py
│   │   └── events.py
│   │
│   ├── schemas/
│   │   ├── stock.py
│   │   ├── valuation.py
│   │   ├── financial.py
│   │   ├── industry.py
│   │   ├── index.py
│   │   ├── etf.py
│   │   ├── news.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── stock_service.py
│   │   ├── valuation_service.py
│   │   ├── industry_service.py
│   │   ├── index_service.py
│   │   ├── etf_service.py
│   │   ├── news_service.py
│   │   └── ...
│   │
│   ├── repositories/
│   │   ├── stock_repository.py
│   │   ├── financial_repository.py
│   │   ├── market_repository.py
│   │   └── ...
│   │
│   ├── data_sources/
│   │   ├── csindex/
│   │   ├── akshare/
│   │   ├── eastmoney/
│   │   ├── tushare/
│   │   └── ...
│   │
│   ├── models/
│   │   ├── stock.py
│   │   ├── financial.py
│   │   ├── market.py
│   │   ├── industry.py
│   │   ├── index.py
│   │   ├── etf.py
│   │   ├── news.py
│   │   └── ...
│   │
│   └── core/
│       ├── config.py
│       ├── database.py
│       ├── logging.py
│       └── exceptions.py
│
├── tests/
└── pyproject.toml


---

20. 前端

frontend/
│
├── src/
│   │
│   ├── main.ts
│   ├── App.vue
│   │
│   ├── router/
│   │   └── index.ts
│   │
│   ├── layouts/
│   │   └── MainLayout.vue
│   │
│   ├── views/
│   │   ├── Home/
│   │   ├── Stock/
│   │   ├── Industry/
│   │   ├── Index/
│   │   ├── ETF/
│   │   ├── News/
│   │   └── Watchlist/
│   │
│   ├── components/
│   │   ├── stock/
│   │   │   ├── StockHeader.vue
│   │   │   ├── StockOverview.vue
│   │   │   ├── StockQuote.vue
│   │   │   ├── StockValuation.vue
│   │   │   ├── StockFinancial.vue
│   │   │   ├── StockIndustry.vue
│   │   │   ├── StockIndices.vue
│   │   │   ├── StockETF.vue
│   │   │   ├── StockShareholders.vue
│   │   │   ├── StockInstitutions.vue
│   │   │   ├── StockNews.vue
│   │   │   ├── StockAnnouncements.vue
│   │   │   ├── StockReports.vue
│   │   │   ├── StockIndustryChain.vue
│   │   │   └── StockEvents.vue
│   │   │
│   │   ├── charts/
│   │   ├── common/
│   │   └── layout/
│   │
│   ├── api/
│   │   ├── stock.ts
│   │   ├── valuation.ts
│   │   ├── financial.ts
│   │   ├── industry.ts
│   │   ├── index.ts
│   │   ├── etf.ts
│   │   └── news.ts
│   │
│   ├── stores/
│   │   ├── stock.ts
│   │   ├── market.ts
│   │   └── user.ts
│   │
│   ├── types/
│   │   ├── stock.ts
│   │   ├── financial.ts
│   │   ├── valuation.ts
│   │   ├── industry.ts
│   │   └── ...
│   │
│   └── utils/
│       ├── format.ts
│       ├── number.ts
│       └── date.ts
│
└── package.json


---


二十一、最关键的设计：组件必须“可插拔”

比如股票页面：

<StockPage>
    <StockHeader />


    <StockOverview />


    <StockQuote />


    <StockValuation />


    <StockFinancial />


    <StockIndustry />


    <StockIndices />


    <StockETF />


    <StockShareholders />


    <StockInstitutions />


    <StockNews />


    <StockAnnouncements />


    <StockReports />


    <StockIndustryChain />


    <StockEvents />
</StockPage>

以后你突然想到：

“我要增加北向资金。”

不用改整个系统。

只需要：

StockNorthbound.vue

然后：

<StockNorthbound />

就行。


---


二十二、数据库现在也不要追求完整数据

你说：

数据我会不断补充。

这个思路完全正确。

所以现在我们只设计数据结构。

例如股票：

Stock
────────────────────
id
symbol
exchange
name
name_en
company_name
industry_id
list_date
status
created_at
updated_at

估值：

StockValuation
────────────────────
stock_id
date
pe
pe_ttm
pe_forward
pb
ps
peg
dividend_yield
market_cap

行情：

StockQuote
────────────────────
stock_id
date
open
high
low
close
volume
amount
turnover

财务：

FinancialReport
────────────────────
stock_id
report_date
revenue
net_profit
net_profit_attributable
gross_profit
operating_cash_flow
roe
roa
debt_ratio


---


二十三、股票和指数一定是多对多关系

这个一定要提前设计。

Stock
  │
  │ N
  │
  │
  │ N
StockIndexMember
  │
  │
  │
Index

因为：

一只股票可以属于多个指数。

一个指数：

也有很多股票。

所以：

stock_index_members

里面：

stock_id
index_id
weight
effective_date

这样以后你查询：

中国化学属于哪些指数？

直接：

SELECT *
FROM stock_index_members
WHERE stock_id = ?


---


二十四、ETF也是多对多

同样：

Stock
   │
   │
ETFHolding
   │
   │
ETF

字段：

etf_id
stock_id
weight
shares
market_value
date

以后：

哪些ETF持有中国化学？

直接查。



---


二十五、新闻不要直接塞Stock表

新闻应该独立：

News
────────────────────
id
title
content
source
url
publish_time
category
created_at

然后：

NewsStock
────────────────────
news_id
stock_id
relevance

因为一条新闻可能涉及：

中国化学 + 万华化学 + 化工行业 + 某个政策。

所以新闻和股票必须是：

多对多。


---


二十六、行业也一样
Industry
    │
    ├── 一级行业
    │      └── 二级行业
    │             └── 三级行业
    │
    └── 不同分类体系

你以后会用到：

申万
中证
中上协
自定义

因此不能简单：

stock.industry = "化工"

应该：

IndustryClassification

再建立：

StockIndustry

这样以后你就能同时显示：

中证行业：XXX
申万行业：XXX
中上协行业：XXX
自定义行业：XXX


---



二十七、最终整个系统的数据关系应该是这样
                         ┌──────────────┐
                         │     Stock    │
                         │   股票核心表  │
                         └──────┬───────┘
                                │
       ┌────────────┬───────────┼────────────┬─────────────┐
       ↓            ↓           ↓            ↓             ↓
     行情          财务         估值          行业           指数
       │            │           │            │             │
       ↓            ↓           ↓            ↓             ↓
   StockQuote   Financial   Valuation   StockIndustry   StockIndex
                                                            │
                                                            ↓
                                                         Index
       
       ┌────────────┬────────────┬────────────┬────────────┐
       ↓            ↓            ↓            ↓
      ETF          股东         机构         新闻
       │            │            │            │
       ↓            ↓            ↓            ↓
   ETFHolding    Shareholder   Institution  NewsStock
       
       ┌────────────┬────────────┬────────────┐
       ↓            ↓            ↓
      公告         研报          事件
       │            │            │
       ↓            ↓            ↓
   Announcement   Report       Event

这就是整个项目的核心骨架。


---


二十八、项目开发顺序我建议严格按照这个来

不要一开始就抓新闻、抓行情、抓中证。

第1阶段：框架
FastAPI
+
Vue
+
TypeScript
+
SQLite

实现：

搜索股票
↓
股票详情页
↓
所有模块空页面
第2阶段：股票基础信息

只放：

代码
名称
交易所
上市日期
公司名称
行业
第3阶段：行情

加入：

当前价格
涨跌
K线
成交量
第4阶段：估值

加入：

PE
PE-TTM
PB
PS
股息率
历史估值
第5阶段：行业

加入：

中证
申万
中上协
第6阶段：指数

实现：

股票 → 所属指数

以及：

指数 → 成分股

第7阶段：ETF

实现：

股票 → ETF

以及：

ETF → 成分股

第8阶段：财务

加入：

营收
净利润
ROE
现金流
资产负债率
第9阶段：新闻

加入：

新闻
公告
研报
第10阶段：高级分析

最后才做：

估值分位
行业比较
历史比较
竞争对手
产业链
资金
机构
事件
AI分析


---


二十九、这样以后你会得到一个非常舒服的工作流

比如你突然看到：

中国化学

你根本不用到处查。

打开：

http://localhost:3000/stock/601117

然后一眼看到：

中国化学
────────────────────────


基本信息
行情
估值
财务
行业
指数
ETF
股东
机构
新闻
公告
研报
产业链
事件
投资分析

然后：

想研究估值

点：

估值

想知道属于哪些行业

点：

行业

想知道哪些ETF持有

点：

ETF

想知道最近发生了什么

点：

新闻 / 公告

想研究最近走势

点：

行情

想研究长期逻辑

点：

财务 / 产业链 / 投资分析


三十、而且以后可以把你的爬虫全部接进来

你现在已经有不少爬虫、新闻抓取、雪球文章生成等代码。

这个项目最终可以成为你的数据中心：

                 数据源
                   │
       ┌───────────┼────────────┐
       ↓           ↓            ↓
     中证         行情          新闻
       ↓           ↓            ↓
    CSIndex      Market       News
       │           │            │
       └───────────┼────────────┘
                   ↓
                Database
                   ↓
                FastAPI
                   ↓
                Vue网站
                   ↓
             股票研究主页

以后你抓到：

路透社新闻

就进入：

News

抓到：

上交所公告

就进入：

Announcement

抓到：

中证指数成分股

就进入：

Index / StockIndexMember

抓到：

财务数据

就进入：

FinancialReport

网站完全不用重新设计。

三十一、所以第一版我建议就叫“骨架工程”

现在甚至可以完全没有真实数据。

我们先放：

中国化学 601117

作为 Demo 股票。

所有模块显示：

暂无数据

但是页面全部存在。

例如：

概览       ✅
行情       ✅
估值       ✅
财务       ✅
行业       ✅
指数       ✅
ETF        ✅
股东       ✅
机构       ✅
新闻       ✅
公告       ✅
研报       ✅
产业链     ✅
事件       ✅

这样以后你只需要往 API 里面塞数据。

最终技术方案

我建议直接确定：

前端
Vue 3
TypeScript
Vite
Element Plus
ECharts
Pinia
Vue Router


后端
Python
FastAPI
Pydantic
SQLAlchemy


数据库
SQLite
↓
以后数据量大
↓
PostgreSQL / DuckDB


数据层
DataProvider
    ├── CSIndexProvider
    ├── MarketProvider
    ├── FinancialProvider
    ├── NewsProvider
    ├── AnnouncementProvider
    └── ETFProvider

FastAPI 的官方文档本身就支持路由拆分、数据模型、数据库、测试、静态文件和自动 OpenAPI 文档，非常适合作为这个项目的后端骨架。

最关键的一句话：先把“股票”定义成整个系统的核心实体，而不是把“中证指数”定义成核心。

这样你以后无论增加中证、申万、行情、财务、ETF、基金、新闻、公告、研报、产业链、机构、AI分析中的任何东西，都只是给 StockDetail 增加一个新的信息模块，不需要推翻整个项目。