# -*- coding: utf-8 -*-
import argparse
import asyncio
import sys
import time

from dataclasses import dataclass, field
from typing import Any, Dict, List

"""
A股股票信息中心

本模块用于构建一只股票的完整信息中心，统一管理股票的基础信息、
市场行情、估值、财务、股东、机构、新闻、公告、研报、重大事件、
竞争对手、产业链、技术分析以及 AI 投资分析等数据。

整体采用异步任务调度方式，将股票分析拆分为多个相互独立的任务，
在数据采集阶段通过 asyncio.gather() 并发执行，从而减少整体等待时间。
对于新闻抓取、历史行情、复杂数据分析以及本地大模型调用等耗时操作，
提供统一的实时进度输出，避免程序长时间无输出导致用户误以为程序卡死。

主要组成：

    StockCenter
        股票信息中心数据模型。
        统一保存一只股票的全部原始数据和分析结果。

    ProgressManager
        全局进度管理器。
        负责任务开始、完成、失败、详细步骤以及耗时操作的实时输出。
        当前支持模拟耗时，后续接入真实数据源和 Ollama 后无需修改整体结构。

    StockDataService
        股票数据采集服务。
        负责获取基础信息、公司资料、行业分类、指数、ETF、行情、
        估值、财务、股东、机构、新闻、公告、研报、事件、
        竞争对手、产业链以及历史行情等数据。

    StockAIAnalyzer
        AI 分析服务。
        负责基本面分析、估值分析以及投资逻辑分析。
        后续可直接接入本地 Ollama，例如 qwen3:8b。

    TechnicalAnalyzer
        技术分析服务。
        负责计算 MA、MACD、KDJ、RSI、布林带以及趋势等技术指标。

    StockAnalyzer
        股票分析总调度器。
        按照“基础数据 → 资讯 → 公司关系 → 技术面 → AI 分析”的
        顺序组织整个股票信息中心的构建过程。

    StockPrinter
        股票信息中心输出模块。
        将最终结果按照不同分析维度进行结构化展示。

执行流程：

    输入股票代码
        ↓
    股票代码标准化
        ↓
    基础数据并发采集
        ↓
    新闻 / 公告 / 研报 / 事件采集
        ↓
    竞争对手 / 产业链分析
        ↓
    技术指标分析
        ↓
    AI 基本面分析
        ↓
    AI 估值分析
        ↓
    AI 投资逻辑分析
        ↓
    输出完整股票信息中心

当前版本中的数据接口部分使用模拟数据和模拟耗时，
主要用于验证整体架构、异步调度以及进度显示效果。

后续接入真实数据源时，可以直接在 StockDataService 中替换对应方法，
例如接入东方财富、财联社、央视财经、交易所、指数基金数据、
券商研报等数据源；AI 分析部分则可以直接接入本地 Ollama
或兼容 OpenAI API 的其他大模型服务。

使用方式：

    python stock_center.py 600519

或者：

    python stock_center.py

然后根据提示输入股票代码。

指定 AI 模型：

    python stock_center.py 600519 --model qwen3:8b

设计原则：

    1. 数据采集、分析、调度和输出相互解耦。
    2. 独立数据任务尽可能采用异步并发执行。
    3. 所有耗时任务均提供明确的进度反馈。
    4. 单个数据源失败不会直接导致整个股票分析流程中断。
    5. AI 分析与原始数据采集保持独立，方便替换不同模型。
    6. 当前模拟接口与未来真实数据接口保持一致，便于逐步替换。
"""


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

    负责：

        1. 大阶段进度
        2. detail 明细进度
        3. 模拟耗时
        4. AI 分析进度
        5. 任务耗时统计
        6. 异常显示

    示例：

        [01/20] 🔄 基本信息     进行中...
                 ↳ 查询股票基本信息
                 ↳ 查询股票基本信息：处理中... 0.5s
                 ↳ 查询股票基本信息：完成，耗时 0.62s
        [01/20] ✅ 基本信息     完成 5 项 (0.63s / 总计 0.6s)

        [11/20] 🔄 新闻         进行中...
                 ↳ 东方财富新闻
                 ↳ 东方财富新闻：抓取中... 0.5s
                 ↳ 东方财富新闻：抓取中... 1.0s
                 ↳ 东方财富新闻：完成，共 19 条，耗时 1.21s
                 ↳ 财联社新闻
                 ↳ 财联社新闻：抓取中... 0.5s
                 ↳ 财联社新闻：完成，共 13 条，耗时 0.83s
        [11/20] ✅ 新闻         完成 共 32 条 (2.10s / 总计 2.7s)

        [18/20] 🤖 基本面       进行中...
                 ↳ 整理财务数据
                 ↳ 整理行业数据
                 ↳ 构建 AI Prompt
                 ↳ 调用本地模型：qwen3:8b
                 ↳ 调用本地模型：qwen3:8b：处理中... 0.5s
                 ↳ 调用本地模型：qwen3:8b：处理中... 1.0s
                 ↳ 调用本地模型：qwen3:8b：处理中... 1.5s
                 ↳ 调用本地模型：qwen3:8b：完成，耗时 2.31s
                 ↳ 解析 AI 分析结果
        [18/20] ✅ 基本面       完成 8 项 (2.35s / 总计 8.2s)
    """

    def __init__(self, total: int):

        self.total = total
        self.completed = 0

        self.lock = asyncio.Lock()

        self.start_time = time.perf_counter()

        # 每个大任务开始时间
        self.task_start_times: Dict[str, float] = {}

    async def start(
        self,
        name: str,
        icon: str = "🔄",
    ):

        async with self.lock:

            current = self.completed + 1

            self.task_start_times[name] = time.perf_counter()

            elapsed = time.perf_counter() - self.start_time

            print(
                f"[{current:02d}/{self.total}] "
                f"{icon} {name:<12} 进行中..."
                f"  (总计 {elapsed:.1f}s)",
                flush=True,
            )

    async def done(
        self,
        name: str,
        message: str = "",
    ):

        async with self.lock:

            self.completed += 1

            total_elapsed = time.perf_counter() - self.start_time

            task_start = self.task_start_times.pop(
                name,
                None,
            )

            if task_start is not None:

                task_elapsed = time.perf_counter() - task_start

            else:

                task_elapsed = 0.0

            suffix = ""

            if message:

                suffix = f" {message}"

            print(
                f"[{self.completed:02d}/{self.total}] "
                f"✅ {name:<12} 完成"
                f"{suffix}"
                f"  ({task_elapsed:.2f}s / "
                f"总计 {total_elapsed:.1f}s)",
                flush=True,
            )

    async def failed(
        self,
        name: str,
        error: Exception,
    ):

        async with self.lock:

            self.completed += 1

            task_start = self.task_start_times.pop(
                name,
                None,
            )

            if task_start is not None:

                task_elapsed = time.perf_counter() - task_start

            else:

                task_elapsed = 0.0

            print(
                f"[{self.completed:02d}/{self.total}] "
                f"❌ {name:<12} 失败：{error}"
                f"  ({task_elapsed:.2f}s)",
                flush=True,
            )

    async def ai(
        self,
        name: str,
    ):

        async with self.lock:

            print(
                f"           🤖 {name:<12} " f"AI 分析中...",
                flush=True,
            )

    async def detail(
        self,
        message: str,
    ):

        async with self.lock:

            print(
                f"                 ↳ {message}",
                flush=True,
            )

    async def simulate(
        self,
        message: str,
        seconds: float = 1.0,
        interval: float = 0.5,
        progress_text: str = "处理中",
    ):
        """
        模拟一个耗时操作。

        参数：

            message:
                当前正在执行的操作。

            seconds:
                模拟总耗时。

            interval:
                多久输出一次进度。

            progress_text:
                进度显示文字。
        """

        start = time.perf_counter()

        await self.detail(message)

        elapsed = 0.0

        while elapsed < seconds:

            wait_time = min(
                interval,
                seconds - elapsed,
            )

            await asyncio.sleep(wait_time)

            elapsed = time.perf_counter() - start

            if elapsed < seconds:

                async with self.lock:

                    print(
                        f"                 ↳ "
                        f"{message}："
                        f"{progress_text}... "
                        f"{elapsed:.1f}s",
                        flush=True,
                    )

        elapsed = time.perf_counter() - start

        async with self.lock:

            print(
                f"                 ↳ " f"{message}：完成，" f"耗时 {elapsed:.2f}s",
                flush=True,
            )

    async def warning(
        self,
        message: str,
    ):

        async with self.lock:

            print(
                f"                 ⚠️ {message}",
                flush=True,
            )

    async def info(
        self,
        message: str,
    ):

        async with self.lock:

            print(
                f"                 ℹ️ {message}",
                flush=True,
            )


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

    def __init__(
        self,
        progress: ProgressManager,
    ):

        self.progress = progress

    async def detail(
        self,
        message: str,
    ):

        await self.progress.detail(message)

    async def get_basic_info(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "查询股票基本信息",
            seconds=0.5,
        )

        return {
            "股票代码": symbol,
            "股票名称": "待查询",
            "市场": "A股",
            "上市状态": "待查询",
            "上市日期": "待查询",
        }

    async def get_company(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "查询公司基本资料",
            seconds=0.6,
        )

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

    async def get_industry(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "查询行业分类",
            seconds=0.5,
        )

        return {
            "所属行业": "待查询",
            "申万行业": "待查询",
            "中信行业": "待查询",
            "行业地位": "待分析",
            "行业规模": "待分析",
            "行业景气度": "待分析",
        }

    async def get_indices(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "查询成分指数",
            seconds=0.4,
        )

        return []

    async def get_etfs(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "查询 ETF 持仓",
            seconds=0.6,
        )

        return []

    async def get_market(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "查询实时行情",
            seconds=0.4,
        )

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

    async def get_valuation(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "查询估值指标",
            seconds=0.5,
        )

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

    async def get_financial(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "查询最新财务数据",
            seconds=0.7,
        )

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

    async def get_shareholders(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "查询十大股东",
            seconds=0.8,
        )

        return []

    async def get_institutions(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "查询机构持仓",
            seconds=0.8,
        )

        return []

    async def get_news(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        # ----------------------------------------------------
        # 东方财富
        # ----------------------------------------------------

        await self.progress.simulate(
            "东方财富新闻",
            seconds=1.3,
            progress_text="抓取中",
        )

        # 后面替换成真实爬虫
        #
        # eastmoney = await self.eastmoney.get_news(symbol)

        # ----------------------------------------------------
        # 财联社
        # ----------------------------------------------------

        await self.progress.simulate(
            "财联社新闻",
            seconds=1.0,
            progress_text="抓取中",
        )

        # cls = await self.cls.get_news(symbol)

        # ----------------------------------------------------
        # 央视财经
        # ----------------------------------------------------

        await self.progress.simulate(
            "央视财经",
            seconds=1.1,
            progress_text="抓取中",
        )

        # cctv = await self.cctv.get_news(symbol)

        # ----------------------------------------------------
        # 新闻处理
        # ----------------------------------------------------

        await self.progress.simulate(
            "新闻去重",
            seconds=0.4,
        )

        await self.progress.simulate(
            "新闻排序",
            seconds=0.3,
        )

        return []

    async def get_announcements(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "查询公司公告",
            seconds=1.0,
            progress_text="抓取中",
        )

        return []

    async def get_research_reports(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "查询券商研报",
            seconds=1.2,
            progress_text="抓取中",
        )

        return []

    async def get_events(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "查询重大事件",
            seconds=0.8,
        )

        return []

    async def get_competitors(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "识别竞争对手",
            seconds=1.0,
        )

        return []

    async def get_industry_chain(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "分析产业链结构",
            seconds=1.3,
            progress_text="分析中",
        )

        return {
            "上游": [],
            "中游": [],
            "下游": [],
            "客户": [],
            "供应商": [],
            "核心原材料": [],
            "核心产品": [],
        }

    async def get_price_history(
        self,
        symbol: str,
    ) -> List[Dict[str, Any]]:

        await self.progress.simulate(
            "获取历史行情",
            seconds=1.0,
            progress_text="获取中",
        )

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

    def __init__(
        self,
        progress: ProgressManager,
        model_name: str = "qwen3:8b",
    ):

        self.progress = progress
        self.model_name = model_name

    async def analyze_fundamental(
        self,
        center: StockCenter,
    ) -> Dict[str, Any]:

        await self.progress.ai("基本面分析")

        await self.progress.detail("整理财务数据")

        await self.progress.detail("整理行业数据")

        await self.progress.detail("构建 AI Prompt")

        # ----------------------------------------------------
        # 模拟 Ollama
        # ----------------------------------------------------

        await self.progress.simulate(
            f"调用本地模型：{self.model_name}",
            seconds=2.8,
            progress_text="模型运行中",
        )

        await self.progress.detail("解析 AI 分析结果")

        await asyncio.sleep(0.2)

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

    async def analyze_valuation(
        self,
        center: StockCenter,
    ) -> Dict[str, Any]:

        await self.progress.ai("估值分析")

        await self.progress.detail("整理 PE / PB / PEG")

        await self.progress.detail("整理历史估值")

        await self.progress.detail("整理行业估值")

        await self.progress.detail("构建 AI Prompt")

        await self.progress.simulate(
            f"调用本地模型：{self.model_name}",
            seconds=2.4,
            progress_text="模型运行中",
        )

        await self.progress.detail("生成估值结论")

        await asyncio.sleep(0.2)

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

    async def analyze_investment_logic(
        self,
        center: StockCenter,
    ) -> Dict[str, Any]:

        await self.progress.ai("投资逻辑")

        await self.progress.detail("汇总公司信息")

        await self.progress.detail("汇总行业信息")

        await self.progress.detail("汇总新闻与公告")

        await self.progress.detail("汇总财务数据")

        await self.progress.detail("汇总竞争对手与产业链")

        await self.progress.detail("构建最终 AI Prompt")

        await self.progress.simulate(
            f"调用本地模型：{self.model_name}",
            seconds=3.2,
            progress_text="模型运行中",
        )

        await self.progress.detail("生成投资逻辑")

        await asyncio.sleep(0.2)

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

    def __init__(
        self,
        progress: ProgressManager,
    ):

        self.progress = progress

    async def analyze(
        self,
        center: StockCenter,
    ) -> Dict[str, Any]:

        await self.progress.simulate(
            "计算 MA5 / MA10 / MA20 / MA60",
            seconds=0.4,
            progress_text="计算中",
        )

        await self.progress.simulate(
            "计算 MACD",
            seconds=0.3,
            progress_text="计算中",
        )

        await self.progress.simulate(
            "计算 KDJ",
            seconds=0.3,
            progress_text="计算中",
        )

        await self.progress.simulate(
            "计算 RSI",
            seconds=0.3,
            progress_text="计算中",
        )

        await self.progress.simulate(
            "计算布林带",
            seconds=0.3,
            progress_text="计算中",
        )

        await self.progress.simulate(
            "判断趋势",
            seconds=0.4,
            progress_text="分析中",
        )

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

    async def _run_task(
        self,
        center: StockCenter,
        name: str,
        attribute: str,
        function,
    ):

        await self.progress.start(name)

        try:

            result = await function(center.symbol)

            setattr(
                center,
                attribute,
                result,
            )

            message = self._result_message(result)

            await self.progress.done(
                name,
                message,
            )

        except Exception as exc:

            await self.progress.failed(
                name,
                exc,
            )

            if isinstance(
                getattr(center, attribute),
                list,
            ):

                setattr(
                    center,
                    attribute,
                    [],
                )

            else:

                setattr(
                    center,
                    attribute,
                    {},
                )

    async def build(
        self,
        symbol: str,
    ) -> StockCenter:

        center = StockCenter(symbol=symbol)

        # ----------------------------------------------------
        # 第一阶段：基础数据
        # ----------------------------------------------------

        basic_tasks = [
            self._run_task(
                center,
                "基本信息",
                "basic_info",
                self.data.get_basic_info,
            ),
            self._run_task(
                center,
                "公司",
                "company",
                self.data.get_company,
            ),
            self._run_task(
                center,
                "行业",
                "industry",
                self.data.get_industry,
            ),
            self._run_task(
                center,
                "指数",
                "indices",
                self.data.get_indices,
            ),
            self._run_task(
                center,
                "ETF",
                "etfs",
                self.data.get_etfs,
            ),
            self._run_task(
                center,
                "行情",
                "market",
                self.data.get_market,
            ),
            self._run_task(
                center,
                "估值",
                "valuation",
                self.data.get_valuation,
            ),
            self._run_task(
                center,
                "财务",
                "financial",
                self.data.get_financial,
            ),
            self._run_task(
                center,
                "股东",
                "shareholders",
                self.data.get_shareholders,
            ),
            self._run_task(
                center,
                "机构",
                "institutions",
                self.data.get_institutions,
            ),
            self._run_task(
                center,
                "历史行情",
                "_price_history",
                self.data.get_price_history,
            ),
        ]

        await asyncio.gather(*basic_tasks)

        center.name = center.basic_info.get(
            "股票名称",
            symbol,
        )

        # ----------------------------------------------------
        # 第二阶段：资讯
        # ----------------------------------------------------

        information_tasks = [
            self._run_task(
                center,
                "新闻",
                "news",
                self.data.get_news,
            ),
            self._run_task(
                center,
                "公告",
                "announcements",
                self.data.get_announcements,
            ),
            self._run_task(
                center,
                "研报",
                "research_reports",
                self.data.get_research_reports,
            ),
            self._run_task(
                center,
                "事件",
                "events",
                self.data.get_events,
            ),
        ]

        await asyncio.gather(*information_tasks)

        # ----------------------------------------------------
        # 第三阶段：公司关系
        # ----------------------------------------------------

        relationship_tasks = [
            self._run_task(
                center,
                "竞争对手",
                "competitors",
                self.data.get_competitors,
            ),
            self._run_task(
                center,
                "产业链",
                "industry_chain",
                self.data.get_industry_chain,
            ),
        ]

        await asyncio.gather(*relationship_tasks)

        # ----------------------------------------------------
        # 第四阶段：技术面
        # ----------------------------------------------------

        await self.progress.start(
            "技术面",
            icon="📈",
        )

        try:

            center.technical = await self.technical.analyze(center)

            await self.progress.done(
                "技术面",
                self._result_message(center.technical),
            )

        except Exception as exc:

            await self.progress.failed(
                "技术面",
                exc,
            )

        # ----------------------------------------------------
        # 第五阶段：AI 基本面
        # ----------------------------------------------------

        await self.progress.start(
            "基本面",
            icon="🤖",
        )

        try:

            center.fundamental = await self.ai.analyze_fundamental(center)

            await self.progress.done(
                "基本面",
                self._result_message(center.fundamental),
            )

        except Exception as exc:

            await self.progress.failed(
                "基本面",
                exc,
            )

        # ----------------------------------------------------
        # 第六阶段：AI 估值
        # ----------------------------------------------------

        await self.progress.start(
            "估值分析",
            icon="🤖",
        )

        try:

            center.valuation_analysis = await self.ai.analyze_valuation(center)

            await self.progress.done(
                "估值分析",
                self._result_message(center.valuation_analysis),
            )

        except Exception as exc:

            await self.progress.failed(
                "估值分析",
                exc,
            )

        # ----------------------------------------------------
        # 第七阶段：AI 投资逻辑
        # ----------------------------------------------------

        await self.progress.start(
            "投资逻辑",
            icon="🤖",
        )

        try:

            center.investment_logic = await self.ai.analyze_investment_logic(center)

            await self.progress.done(
                "投资逻辑",
                self._result_message(center.investment_logic),
            )

        except Exception as exc:

            await self.progress.failed(
                "投资逻辑",
                exc,
            )

        return center

    @staticmethod
    def _result_message(
        result: Any,
    ) -> str:

        if isinstance(
            result,
            list,
        ):

            return f"共 {len(result)} 条"

        if isinstance(
            result,
            dict,
        ):

            return f"{len(result)} 项"

        return ""


# ============================================================
# 输出
# ============================================================


class StockPrinter:

    def __init__(
        self,
        center: StockCenter,
    ):

        self.center = center

    def print(self):

        print()
        print("=" * 90)

        print(f"股票信息中心：" f"{self.center.name} " f"({self.center.symbol})")

        print("=" * 90)

        self._section(
            "1. 基本信息",
            self.center.basic_info,
        )

        self._section(
            "2. 公司",
            self.center.company,
        )

        self._section(
            "3. 行业",
            self.center.industry,
        )

        self._list_section(
            "4. 指数",
            self.center.indices,
        )

        self._list_section(
            "5. ETF",
            self.center.etfs,
        )

        self._section(
            "6. 行情",
            self.center.market,
        )

        self._section(
            "7. 估值",
            self.center.valuation,
        )

        self._section(
            "8. 财务",
            self.center.financial,
        )

        self._list_section(
            "9. 股东",
            self.center.shareholders,
        )

        self._list_section(
            "10. 机构",
            self.center.institutions,
        )

        self._list_section(
            "11. 新闻",
            self.center.news,
        )

        self._list_section(
            "12. 公告",
            self.center.announcements,
        )

        self._list_section(
            "13. 研报",
            self.center.research_reports,
        )

        self._list_section(
            "14. 事件",
            self.center.events,
        )

        self._list_section(
            "15. 竞争对手",
            self.center.competitors,
        )

        self._section(
            "16. 产业链",
            self.center.industry_chain,
        )

        self._section(
            "17. 技术面",
            self.center.technical,
        )

        self._section(
            "18. 基本面",
            self.center.fundamental,
        )

        self._section(
            "19. 估值分析",
            self.center.valuation_analysis,
        )

        self._section(
            "20. 投资逻辑",
            self.center.investment_logic,
        )

        print()
        print("=" * 90)
        print("🎉 股票信息中心构建完成")
        print("=" * 90)
        print()

    @staticmethod
    def _section(
        title: str,
        data: Dict[str, Any],
    ):

        print()
        print(f"【{title}】")

        print("-" * 70)

        if not data:

            print("暂无数据")

            return

        for key, value in data.items():

            StockPrinter._print_value(
                key,
                value,
            )

    @staticmethod
    def _list_section(
        title: str,
        data: List[Dict[str, Any]],
    ):

        print()
        print(f"【{title}】")

        print("-" * 70)

        if not data:

            print("暂无数据")

            return

        for index, item in enumerate(
            data,
            start=1,
        ):

            print(f"[{index}]")

            if isinstance(
                item,
                dict,
            ):

                for key, value in item.items():

                    StockPrinter._print_value(
                        key,
                        value,
                        indent=4,
                    )

            else:

                print(f"    {item}")

    @staticmethod
    def _print_value(
        key: str,
        value: Any,
        indent: int = 2,
    ):

        prefix = " " * indent

        if isinstance(
            value,
            list,
        ):

            print(f"{prefix}{key}:")

            if not value:

                print(f"{prefix}    暂无")

                return

            for item in value:

                if isinstance(
                    item,
                    dict,
                ):

                    print(f"{prefix}    -")

                    for k, v in item.items():

                        print(f"{prefix}      " f"{k}: {v}")

                else:

                    print(f"{prefix}    - {item}")

            return

        if isinstance(
            value,
            dict,
        ):

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


def normalize_symbol(
    symbol: str,
) -> str:

    symbol = symbol.strip().upper()

    symbol = symbol.replace(
        ".",
        "",
    )

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

    parser.add_argument(
        "symbol",
        nargs="?",
        help="股票代码，例如：600519",
    )

    parser.add_argument(
        "--model",
        default="qwen3:8b",
        help="AI 模型，默认 qwen3:8b",
    )

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

    print(f"🚀 股票信息中心启动：" f"{symbol}")

    print("=" * 90)
    print()

    start_time = time.perf_counter()

    progress = ProgressManager(total=21)

    data_service = StockDataService(progress=progress)

    ai_analyzer = StockAIAnalyzer(
        progress=progress,
        model_name=args.model,
    )

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

    print(f"⏱️ 总耗时：" f"{elapsed:.2f} 秒")

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
