# -*- coding: utf-8 -*-

import argparse
import asyncio
import inspect
import sys
import time

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ============================================================
# 数据模型
# ============================================================


@dataclass
class StockCenter:
    """一只股票的完整信息中心"""

    symbol: str
    name: str = ""

    # 基础信息
    basic_info: Dict[str, Any] = field(default_factory=dict)
    company: Dict[str, Any] = field(default_factory=dict)
    industry: Dict[str, Any] = field(default_factory=dict)

    # 关联关系
    indices: List[Dict[str, Any]] = field(default_factory=list)
    etfs: List[Dict[str, Any]] = field(default_factory=list)

    # 市场数据
    market: Dict[str, Any] = field(default_factory=dict)
    valuation: Dict[str, Any] = field(default_factory=dict)
    financial: Dict[str, Any] = field(default_factory=dict)

    # 股东 / 机构
    shareholders: List[Dict[str, Any]] = field(default_factory=list)
    institutions: List[Dict[str, Any]] = field(default_factory=list)

    # 资讯
    news: List[Dict[str, Any]] = field(default_factory=list)
    announcements: List[Dict[str, Any]] = field(default_factory=list)
    research_reports: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

    # 公司关系
    competitors: List[Dict[str, Any]] = field(default_factory=list)
    industry_chain: Dict[str, Any] = field(default_factory=dict)

    # 分析结果
    technical: Dict[str, Any] = field(default_factory=dict)
    fundamental: Dict[str, Any] = field(default_factory=dict)
    valuation_analysis: Dict[str, Any] = field(default_factory=dict)
    investment_logic: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# 进度管理器
# ============================================================


class ProgressManager:
    """
    股票信息中心统一进度管理器。

    支持：

        [01/20] 🔄 基本信息        查询中...
        [01/20] ✅ 基本信息        完成

        [11/20] 🔄 新闻            查询中...
                 ↳ 东方财富
                 ↳ 财联社
                 ↳ 央视财经

        [18/20] 🤖 基本面          AI 分析中...
                 ↳ 准备财务数据
                 ↳ 构建 Prompt
                 ↳ 调用 Ollama
                 ↳ 解析分析结果
    """

    def __init__(self, total: int):

        self.total = total
        self.completed = 0
        self.lock = asyncio.Lock()

        self.start_time = time.perf_counter()

    async def start(self, name: str, icon: str = "🔄"):

        async with self.lock:

            current = self.completed + 1

            print(
                f"[{current:02d}/{self.total}] " f"{icon} {name:<12} 进行中...",
                flush=True,
            )

    async def done(self, name: str, message: str = ""):

        async with self.lock:

            self.completed += 1

            elapsed = time.perf_counter() - self.start_time

            suffix = ""

            if message:
                suffix = f" {message}"

            print(
                f"[{self.completed:02d}/{self.total}] "
                f"✅ {name:<12} 完成"
                f"{suffix}"
                f"  ({elapsed:.1f}s)",
                flush=True,
            )

    async def failed(self, name: str, error: Exception):

        async with self.lock:

            self.completed += 1

            print(
                f"[{self.completed:02d}/{self.total}] " f"❌ {name:<12} 失败：{error}",
                flush=True,
            )

    async def ai(self, name: str):

        async with self.lock:

            print(f"           🤖 {name:<12} " f"AI 分析中...", flush=True)

    async def detail(self, message: str):

        async with self.lock:

            print(f"                 ↳ {message}", flush=True)

    async def warning(self, message: str):

        async with self.lock:

            print(f"                 ⚠️ {message}", flush=True)

    async def info(self, message: str):

        async with self.lock:

            print(f"                 ℹ️ {message}", flush=True)


# ============================================================
# 数据服务
# ============================================================


class StockDataService:
    """
    股票数据服务。

    这里负责从各种数据源获取原始数据。

    后面可以接入：

        东方财富
        同花顺
        雪球
        财联社
        央视财经
        巨潮资讯
        上海证券交易所
        深圳证券交易所
        中证指数
        基金数据
        券商研报
        自己的数据库
    """

    def __init__(self, progress: ProgressManager):

        self.progress = progress

    async def detail(self, message: str):

        await self.progress.detail(message)

        await asyncio.sleep(1)

        await self.progress.detail("模型返回完成")

    async def get_basic_info(self, symbol: str) -> Dict[str, Any]:

        await self.detail("查询股票基本信息")

        return {
            "股票代码": symbol,
            "股票名称": "待查询",
            "市场": "A股",
            "上市状态": "待查询",
            "上市日期": "待查询",
        }

    async def get_company(self, symbol: str) -> Dict[str, Any]:

        await self.detail("查询公司基本资料")

        return {
            "公司名称": "待查询",
            "注册地址": "待查询",
            "办公地址": "待查询",
            "法定代表人": "待查询",
            "董事长": "待查询",
            "总经理": "待查询",
            "实际控制人": "待查询",
            "注册资本": "待查询",
            "员工人数": "待查询",
        }

    async def get_industry(self, symbol: str) -> Dict[str, Any]:

        await self.detail("查询行业分类")

        return {
            "所属行业": "待查询",
            "申万行业": "待查询",
            "中信行业": "待查询",
            "行业地位": "待分析",
            "行业规模": "待分析",
            "行业景气度": "待分析",
        }

    async def get_indices(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("查询成分指数")

        return []

    async def get_etfs(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("查询 ETF 持仓")

        return []

    async def get_market(self, symbol: str) -> Dict[str, Any]:

        await self.detail("查询实时行情")

        return {
            "最新价": None,
            "涨跌幅": None,
            "涨跌额": None,
            "成交量": None,
            "成交额": None,
            "换手率": None,
            "振幅": None,
            "最高": None,
            "最低": None,
            "开盘": None,
            "昨收": None,
        }

    async def get_valuation(self, symbol: str) -> Dict[str, Any]:

        await self.detail("查询估值指标")

        return {
            "总市值": None,
            "流通市值": None,
            "PE": None,
            "PE_TTM": None,
            "PB": None,
            "PS": None,
            "PEG": None,
            "股息率": None,
        }

    async def get_financial(self, symbol: str) -> Dict[str, Any]:

        await self.detail("查询最新财务数据")

        return {
            "营业收入": None,
            "营业收入同比": None,
            "净利润": None,
            "净利润同比": None,
            "扣非净利润": None,
            "毛利率": None,
            "净利率": None,
            "ROE": None,
            "ROA": None,
            "资产负债率": None,
            "经营现金流": None,
            "自由现金流": None,
        }

    async def get_shareholders(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("查询十大股东")

        return []

    async def get_institutions(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("查询机构持仓")

        return []

    async def get_news(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("东方财富新闻")

        # 后面替换成真实爬虫
        #
        # eastmoney = await self.eastmoney.get_news(symbol)

        await self.detail("财联社新闻")

        # cls = await self.cls.get_news(symbol)

        await self.detail("央视财经")

        # cctv = await self.cctv.get_news(symbol)

        await self.detail("新闻去重")

        await self.detail("新闻排序")

        return []

    async def get_announcements(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("查询公司公告")

        return []

    async def get_research_reports(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("查询券商研报")

        return []

    async def get_events(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("查询重大事件")

        return []

    async def get_competitors(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("识别竞争对手")

        return []

    async def get_industry_chain(self, symbol: str) -> Dict[str, Any]:

        await self.detail("分析产业链结构")

        return {
            "上游": [],
            "中游": [],
            "下游": [],
            "客户": [],
            "供应商": [],
            "核心原材料": [],
            "核心产品": [],
        }

    async def get_price_history(self, symbol: str) -> List[Dict[str, Any]]:

        await self.detail("获取历史行情")

        return []


# ============================================================
# AI 分析服务
# ============================================================


class StockAIAnalyzer:
    """
    AI 分析服务。

    后面可以直接接你现在使用的 Ollama：

        http://localhost:11434/v1

    例如：

        qwen3:8b

    或者其他本地模型。
    """

    def __init__(self, progress: ProgressManager, model_name: str = "qwen3:8b"):

        self.progress = progress
        self.model_name = model_name

    async def analyze_fundamental(self, center: StockCenter) -> Dict[str, Any]:

        await self.progress.ai("基本面分析")

        await self.progress.detail("整理财务数据")

        await self.progress.detail("整理行业数据")

        await self.progress.detail("构建 AI Prompt")

        await self.progress.detail(f"调用本地模型：{self.model_name}")

        # TODO:
        # 在这里接入你现有的 Ollama/OpenAI 代码

        await self.progress.detail("解析 AI 分析结果")

        return {
            "盈利能力": None,
            "成长能力": None,
            "偿债能力": None,
            "运营能力": None,
            "现金流": None,
            "竞争优势": None,
            "成长空间": None,
            "行业景气度": None,
        }

    async def analyze_valuation(self, center: StockCenter) -> Dict[str, Any]:

        await self.progress.ai("估值分析")

        await self.progress.detail("整理 PE / PB / PEG")

        await self.progress.detail("整理历史估值")

        await self.progress.detail("整理行业估值")

        await self.progress.detail("构建 AI Prompt")

        await self.progress.detail(f"调用本地模型：{self.model_name}")

        await self.progress.detail("生成估值结论")

        return {
            "历史估值": None,
            "行业估值": None,
            "相对估值": None,
            "PEG分析": None,
            "PE分析": None,
            "PB分析": None,
            "当前估值水平": None,
            "估值结论": None,
        }

    async def analyze_investment_logic(self, center: StockCenter) -> Dict[str, Any]:

        await self.progress.ai("投资逻辑")

        await self.progress.detail("汇总公司信息")

        await self.progress.detail("汇总行业信息")

        await self.progress.detail("汇总新闻与公告")

        await self.progress.detail("汇总财务数据")

        await self.progress.detail("汇总竞争对手与产业链")

        await self.progress.detail("构建最终 AI Prompt")

        await self.progress.detail(f"调用本地模型：{self.model_name}")

        await self.progress.detail("生成投资逻辑")

        return {
            "核心逻辑": [],
            "增长逻辑": [],
            "行业逻辑": [],
            "竞争优势": [],
            "催化剂": [],
            "潜在风险": [],
            "需要跟踪的数据": [],
            "投资结论": None,
        }


# ============================================================
# 技术分析
# ============================================================


class TechnicalAnalyzer:

    def __init__(self, progress: ProgressManager):

        self.progress = progress

    async def analyze(self, center: StockCenter) -> Dict[str, Any]:

        await self.progress.detail("计算 MA5 / MA10 / MA20 / MA60")

        await self.progress.detail("计算 MACD")

        await self.progress.detail("计算 KDJ")

        await self.progress.detail("计算 RSI")

        await self.progress.detail("计算布林带")

        await self.progress.detail("判断趋势")

        return {
            "MA5": None,
            "MA10": None,
            "MA20": None,
            "MA60": None,
            "MACD": None,
            "KDJ": None,
            "RSI": None,
            "BOLL": None,
            "成交量趋势": None,
            "趋势判断": None,
        }


# ============================================================
# 股票分析总调度器
# ============================================================


class StockAnalyzer:

    def __init__(
        self,
        data_service: StockDataService,
        ai_analyzer: StockAIAnalyzer,
        technical_analyzer: TechnicalAnalyzer,
        progress: ProgressManager,
    ):

        self.data = data_service
        self.ai = ai_analyzer
        self.technical = technical_analyzer
        self.progress = progress

    async def _run_task(self, center: StockCenter, name: str, attribute: str, function):

        await self.progress.start(name)

        try:

            result = await function(center.symbol)

            setattr(center, attribute, result)

            message = self._result_message(result)

            await self.progress.done(name, message)

        except Exception as exc:

            await self.progress.failed(name, exc)

            if isinstance(getattr(center, attribute), list):

                setattr(center, attribute, [])

            else:

                setattr(center, attribute, {})

    async def build(self, symbol: str) -> StockCenter:

        center = StockCenter(symbol=symbol)

        # ----------------------------------------------------
        # 第一阶段：基础数据
        # ----------------------------------------------------

        basic_tasks = [
            self._run_task(center, "基本信息", "basic_info", self.data.get_basic_info),
            self._run_task(center, "公司", "company", self.data.get_company),
            self._run_task(center, "行业", "industry", self.data.get_industry),
            self._run_task(center, "指数", "indices", self.data.get_indices),
            self._run_task(center, "ETF", "etfs", self.data.get_etfs),
            self._run_task(center, "行情", "market", self.data.get_market),
            self._run_task(center, "估值", "valuation", self.data.get_valuation),
            self._run_task(center, "财务", "financial", self.data.get_financial),
            self._run_task(center, "股东", "shareholders", self.data.get_shareholders),
            self._run_task(center, "机构", "institutions", self.data.get_institutions),
            self._run_task(
                center, "历史行情", "_price_history", self.data.get_price_history
            ),
        ]

        await asyncio.gather(*basic_tasks)

        center.name = center.basic_info.get("股票名称", symbol)

        # ----------------------------------------------------
        # 第二阶段：资讯
        # ----------------------------------------------------

        information_tasks = [
            self._run_task(center, "新闻", "news", self.data.get_news),
            self._run_task(
                center, "公告", "announcements", self.data.get_announcements
            ),
            self._run_task(
                center, "研报", "research_reports", self.data.get_research_reports
            ),
            self._run_task(center, "事件", "events", self.data.get_events),
        ]

        await asyncio.gather(*information_tasks)

        # ----------------------------------------------------
        # 第三阶段：公司关系
        # ----------------------------------------------------

        relationship_tasks = [
            self._run_task(
                center, "竞争对手", "competitors", self.data.get_competitors
            ),
            self._run_task(
                center, "产业链", "industry_chain", self.data.get_industry_chain
            ),
        ]

        await asyncio.gather(*relationship_tasks)

        # ----------------------------------------------------
        # 第四阶段：技术面
        # ----------------------------------------------------

        await self.progress.start("技术面", icon="📈")

        try:

            center.technical = await self.technical.analyze(center)

            await self.progress.done("技术面")

        except Exception as exc:

            await self.progress.failed("技术面", exc)

        # ----------------------------------------------------
        # 第五阶段：AI 基本面
        # ----------------------------------------------------

        await self.progress.start("基本面", icon="🤖")

        try:

            center.fundamental = await self.ai.analyze_fundamental(center)

            await self.progress.done("基本面")

        except Exception as exc:

            await self.progress.failed("基本面", exc)

        # ----------------------------------------------------
        # 第六阶段：AI 估值
        # ----------------------------------------------------

        await self.progress.start("估值分析", icon="🤖")

        try:

            center.valuation_analysis = await self.ai.analyze_valuation(center)

            await self.progress.done("估值分析")

        except Exception as exc:

            await self.progress.failed("估值分析", exc)

        # ----------------------------------------------------
        # 第七阶段：AI 投资逻辑
        # ----------------------------------------------------

        await self.progress.start("投资逻辑", icon="🤖")

        try:

            center.investment_logic = await self.ai.analyze_investment_logic(center)

            await self.progress.done("投资逻辑")

        except Exception as exc:

            await self.progress.failed("投资逻辑", exc)

        return center

    @staticmethod
    def _result_message(result: Any) -> str:

        if isinstance(result, list):

            return f"共 {len(result)} 条"

        if isinstance(result, dict):

            return f"{len(result)} 项"

        return ""


# ============================================================
# 输出
# ============================================================


class StockPrinter:

    def __init__(self, center: StockCenter):

        self.center = center

    def print(self):

        print()
        print("=" * 90)
        print(f"股票信息中心：" f"{self.center.name} " f"({self.center.symbol})")
        print("=" * 90)

        self._section("1. 基本信息", self.center.basic_info)

        self._section("2. 公司", self.center.company)

        self._section("3. 行业", self.center.industry)

        self._list_section("4. 指数", self.center.indices)

        self._list_section("5. ETF", self.center.etfs)

        self._section("6. 行情", self.center.market)

        self._section("7. 估值", self.center.valuation)

        self._section("8. 财务", self.center.financial)

        self._list_section("9. 股东", self.center.shareholders)

        self._list_section("10. 机构", self.center.institutions)

        self._list_section("11. 新闻", self.center.news)

        self._list_section("12. 公告", self.center.announcements)

        self._list_section("13. 研报", self.center.research_reports)

        self._list_section("14. 事件", self.center.events)

        self._list_section("15. 竞争对手", self.center.competitors)

        self._section("16. 产业链", self.center.industry_chain)

        self._section("17. 技术面", self.center.technical)

        self._section("18. 基本面", self.center.fundamental)

        self._section("19. 估值分析", self.center.valuation_analysis)

        self._section("20. 投资逻辑", self.center.investment_logic)

        print()
        print("=" * 90)
        print("🎉 股票信息中心构建完成")
        print("=" * 90)
        print()

    @staticmethod
    def _section(title: str, data: Dict[str, Any]):

        print()
        print(f"【{title}】")
        print("-" * 70)

        if not data:

            print("暂无数据")
            return

        for key, value in data.items():

            StockPrinter._print_value(key, value)

    @staticmethod
    def _list_section(title: str, data: List[Dict[str, Any]]):

        print()
        print(f"【{title}】")
        print("-" * 70)

        if not data:

            print("暂无数据")
            return

        for index, item in enumerate(data, start=1):

            print(f"[{index}]")

            if isinstance(item, dict):

                for key, value in item.items():

                    StockPrinter._print_value(key, value, indent=4)

            else:

                print(f"    {item}")

    @staticmethod
    def _print_value(key: str, value: Any, indent: int = 2):

        prefix = " " * indent

        if isinstance(value, list):

            print(f"{prefix}{key}:")

            if not value:

                print(f"{prefix}    暂无")

                return

            for item in value:

                if isinstance(item, dict):

                    print(f"{prefix}    -")

                    for k, v in item.items():

                        print(f"{prefix}      " f"{k}: {v}")

                else:

                    print(f"{prefix}    - {item}")

            return

        if isinstance(value, dict):

            print(f"{prefix}{key}:")

            if not value:

                print(f"{prefix}    暂无")

                return

            for k, v in value.items():

                print(f"{prefix}    " f"{k}: {v}")

            return

        if value is None:

            value = "暂无数据"

        print(f"{prefix}{key}: {value}")


# ============================================================
# 股票代码处理
# ============================================================


def normalize_symbol(symbol: str) -> str:

    symbol = symbol.strip().upper()

    symbol = symbol.replace(".", "")

    if symbol.startswith("SH"):

        symbol = symbol[2:]

    elif symbol.startswith("SZ"):

        symbol = symbol[2:]

    elif symbol.startswith("BJ"):

        symbol = symbol[2:]

    if not symbol.isdigit():

        raise ValueError(f"无法识别股票代码：{symbol}")

    if len(symbol) != 6:

        raise ValueError(f"股票代码必须是6位数字：{symbol}")

    return symbol


# ============================================================
# 命令行
# ============================================================


def create_argument_parser():

    parser = argparse.ArgumentParser(description="A股股票信息中心")

    parser.add_argument("symbol", nargs="?", help="股票代码，例如：600519")

    parser.add_argument("--model", default="qwen3:8b", help="AI 模型，默认 qwen3:8b")

    return parser


# ============================================================
# 主程序
# ============================================================


async def async_main():

    parser = create_argument_parser()

    args = parser.parse_args()

    symbol = args.symbol

    if not symbol:

        symbol = input("请输入股票代码：").strip()

    try:

        symbol = normalize_symbol(symbol)

    except ValueError as exc:

        print()
        print(f"❌ {exc}")
        print()

        sys.exit(1)

    print()
    print("=" * 90)
    print(f"🚀 股票信息中心启动：{symbol}")
    print("=" * 90)
    print()

    start_time = time.perf_counter()

    progress = ProgressManager(total=20)

    data_service = StockDataService(progress=progress)

    ai_analyzer = StockAIAnalyzer(progress=progress, model_name=args.model)

    technical_analyzer = TechnicalAnalyzer(progress=progress)

    analyzer = StockAnalyzer(
        data_service=data_service,
        ai_analyzer=ai_analyzer,
        technical_analyzer=technical_analyzer,
        progress=progress,
    )

    center = await analyzer.build(symbol)

    elapsed = time.perf_counter() - start_time

    print()
    print("=" * 90)
    print(f"⏱️ 总耗时：{elapsed:.2f} 秒")
    print("=" * 90)

    printer = StockPrinter(center)

    printer.print()


def main():

    try:

        asyncio.run(async_main())

    except KeyboardInterrupt:

        print()
        print()
        print("⚠️ 用户中断程序")
        print()

    except Exception as exc:

        print()
        print(f"❌ 程序异常：{exc}")
        print()

        sys.exit(1)


if __name__ == "__main__":

    main()
