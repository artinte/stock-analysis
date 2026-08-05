import asyncio
import logging
import ctypes
import platform
import threading
import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import Any, Callable, Dict, List
import pandas as pd
import numpy as np
import yfinance as yf

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================================================
# 1. MCP 统一协议接口与数据结构
# ============================================================================
class MCPToolDefinition:
    """MCP 工具标准声明 (符合 MCP Protocol Specification)"""

    def __init__(self, name: str, description: str, input_schema: dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


# ============================================================================
# 2. 核心路由管理器：MCPClientRouter (解耦与扩展的核心)
# ============================================================================
class MCPClientRouter:
    """
    MCP 客户端路由核心：
    - 管理所有的 Tool 注册
    - 负责分发意图到不同的工具 Handler (如: 股票、文件、爬虫、计算器等)
    - 动态对接远程 MCP Server 或本地 Mock 逻辑
    """

    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_tool(cls, name: str, description: str, input_schema: dict):
        """装饰器：用于注册新的 MCP 工具处理器"""

        def decorator(func: Callable):
            cls._registry[name] = {
                "definition": MCPToolDefinition(name, description, input_schema),
                "handler": func,
            }
            return func

        return decorator

    @classmethod
    def get_registered_tools(cls) -> List[dict]:
        """获取所有已注册工具的标准 MCP Manifest (用于 Prompt / LLM 工具选择)"""
        return [item["definition"].to_dict() for item in cls._registry.values()]

    @classmethod
    async def dispatch(
        cls, tool_name: str, arguments: dict, context_params: dict
    ) -> dict:
        """统一的工具分发执行器"""
        if tool_name not in cls._registry:
            # 兜底提示或路由到大模型通用回答
            return {
                "reply": f"⚠️ 未找到处理工具 [{tool_name}]，已切入通用 LLM 回答模式。",
                "actions": {},
            }

        try:
            handler = cls._registry[tool_name]["handler"]
            # 区分同步与异步 Handler 支持
            if asyncio.iscoroutinefunction(handler):
                return await handler(arguments, context_params)
            else:
                return handler(arguments, context_params)
        except Exception as e:
            logging.error(f"MCP Tool '{tool_name}' 执行异常: {str(e)}", exc_info=True)
            return {"reply": f"❌ 工具执行错误: {str(e)}", "actions": {}}


# ============================================================================
# 3. 业务 Handler 拓展区 (日后所有新功能只需在此处叠加 @register_tool)
# ============================================================================


# ----------------- 领域 1: 证券与行情标的解析 -----------------
@MCPClientRouter.register_tool(
    name="financial_quant_parser",
    description="处理金融、股票标的切换、均线参数修改等量化指令",
    input_schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "用户原始自然语言输入"}
        },
        "required": ["prompt"],
    },
)
async def handle_financial_quant(args: dict, context: dict) -> dict:
    prompt = args.get("prompt", "").lower()

    # 标的识别逻辑 (日后可在此处接入真实行情 API 或大模型实体提取)
    stock_map = {
        "苹果": "AAPL",
        "aapl": "AAPL",
        "特斯拉": "TSLA",
        "tsla": "TSLA",
        "英伟达": "NVDA",
        "nvda": "NVDA",
        "茅台": "600519.SH",
        "腾讯": "0700.HK",
    }

    for key, symbol in stock_map.items():
        if key in prompt:
            return {
                "reply": f"📈 [MCP:Financial] 已解析标的意图，为您切换至 **{symbol}** 行情与分析界面。",
                "actions": {"symbol": symbol},
            }

    return {
        "reply": f"📈 [MCP:Financial] 未在此命令中检测到明确标的切换，保持当前标的 {context.get('symbol')}。",
        "actions": {},
    }


# ----------------- 领域 2: 本地文件/数据解析 (日后拓展预留) -----------------
@MCPClientRouter.register_tool(
    name="local_file_processor",
    description="解析本地 CSV、Excel、PDF 报表或交易日志数据",
    input_schema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "action": {"type": "string", "enum": ["parse", "summarize", "export"]},
        },
    },
)
async def handle_file_processing(args: dict, context: dict) -> dict:
    # 异步读取文件 / 数据管道
    await asyncio.sleep(0.2)
    file_path = args.get("file_path", "data.csv")
    return {
        "reply": f"📁 [MCP:File] 成功调用文件解析组件，读取目标路径: `{file_path}`",
        "actions": {"loaded_file": file_path},
    }


# ----------------- 领域 3: 网络爬虫/自动化数据采集 (日后拓展预留) -----------------
@MCPClientRouter.register_tool(
    name="web_scraper_dispatch",
    description="触发后台爬虫抓取宏观政策、招标公告或网页舆情数据",
    input_schema={
        "type": "object",
        "properties": {"url": {"type": "string"}, "target_depth": {"type": "integer"}},
    },
)
async def handle_web_scraper(args: dict, context: dict) -> dict:
    # 模拟触发爬虫任务
    await asyncio.sleep(0.3)
    return {
        "reply": "🕷️ [MCP:Scraper] 已向数据采集引擎提交任务队列，后台异步抓取中...",
        "actions": {"scraper_task_id": "TASK_20260805_001"},
    }


# ============================================================================
# 4. 智能意图分发器 (模拟 Agent 意图判断)
# ============================================================================
class MCPIntentAnalyzer:
    """决定将用户的自然语言路由给哪一个 MCP Tool"""

    @staticmethod
    async def analyze_and_execute(user_text: str, context_params: dict) -> dict:
        # TODO: 日后直接在此处替换为真实大模型 (如 DeepSeek/OpenAI) 的 Function Calling / Tool Call 接口
        # 传入 MCPClientRouter.get_registered_tools() 让大模型自主决定调用哪个 tool

        text = user_text.strip().lower()

        # 简易意图路由判定
        if any(
            keyword in text
            for keyword in ["股票", "苹果", "特斯拉", "英伟达", "标的", "行情", "aapl"]
        ):
            target_tool = "financial_quant_parser"
            arguments = {"prompt": user_text}
        elif any(
            keyword in text for keyword in ["文件", "excel", "csv", "日志", "报表"]
        ):
            target_tool = "local_file_processor"
            arguments = {"file_path": "./user_data.csv", "action": "parse"}
        elif any(
            keyword in text for keyword in ["抓取", "爬虫", "网页", "公告", "新闻"]
        ):
            target_tool = "web_scraper_dispatch"
            arguments = {"url": "https://example.com", "target_depth": 1}
        else:
            # 默认兜底
            target_tool = "financial_quant_parser"
            arguments = {"prompt": user_text}

        # 统一通过路由器分发调用
        return await MCPClientRouter.dispatch(target_tool, arguments, context_params)


# ---------------------------------------------------------------------------
# 1. Windows 高分屏 (DPI) 锯齿/模糊修复
# ---------------------------------------------------------------------------
if platform.system() == "Windows":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# ---------------------------------------------------------------------------
# 2. Matplotlib 绘图库与嵌入配置
# ---------------------------------------------------------------------------
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Segoe UI",
    "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False


# ---------------------------------------------------------------------------
# 3. 量化数据与计算引擎
# ---------------------------------------------------------------------------
class QuantEngine:
    """量化数据抓取与技术指标/策略回测引擎"""

    @staticmethod
    def fetch_data(symbol: str, start: str, end: str) -> pd.DataFrame:
        data = yf.download(symbol, start=start, end=end, progress=False)
        if data.empty:
            raise ValueError(
                f"未获取到标的 [{symbol}] 的历史行情，请检查代码拼写或网络状态。"
            )
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data

    @staticmethod
    def add_indicators(
        df: pd.DataFrame, ma_short=10, ma_long=50, rsi_period=14
    ) -> pd.DataFrame:
        df = df.copy()
        df["MA_Short"] = df["Close"].rolling(window=ma_short).mean()
        df["MA_Long"] = df["Close"].rolling(window=ma_long).mean()

        # MACD (12, 26, 9)
        exp1 = df["Close"].ewm(span=12, adjust=False).mean()
        exp2 = df["Close"].ewm(span=26, adjust=False).mean()
        df["DIF"] = exp1 - exp2
        df["DEA"] = df["DIF"].ewm(span=9, adjust=False).mean()
        df["MACD"] = (df["DIF"] - df["DEA"]) * 2

        # RSI 指标
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / (loss + 1e-10)
        df["RSI"] = 100 - (100 / (1 + rs))
        return df

    @staticmethod
    def run_ma_backtest(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """双均线金叉/死叉交叉策略回测"""
        bt_df = df.copy()
        bt_df["Signal"] = 0
        bt_df.loc[bt_df["MA_Short"] > bt_df["MA_Long"], "Signal"] = 1
        bt_df["Position"] = bt_df["Signal"].shift(1)

        bt_df["Market_Return"] = bt_df["Close"].pct_change()
        bt_df["Strategy_Return"] = bt_df["Market_Return"] * bt_df["Position"]

        bt_df["Market_Cum"] = (1 + bt_df["Market_Return"].fillna(0)).cumprod()
        bt_df["Strategy_Cum"] = (1 + bt_df["Strategy_Return"].fillna(0)).cumprod()

        strat_returns = bt_df["Strategy_Return"].dropna()
        total_return = (bt_df["Strategy_Cum"].iloc[-1] - 1) * 100

        annual_return = strat_returns.mean() * 252
        annual_vol = strat_returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - 0.02) / (annual_vol + 1e-10)

        cum_peak = bt_df["Strategy_Cum"].cummax()
        drawdown = (bt_df["Strategy_Cum"] - cum_peak) / cum_peak
        max_drawdown = drawdown.min() * 100

        win_trades = (strat_returns > 0).sum()
        total_trades = (strat_returns != 0).sum()
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0.0

        metrics = {
            "Total_Return": f"{total_return:.2f}%",
            "Sharpe_Ratio": f"{sharpe_ratio:.2f}",
            "Max_Drawdown": f"{max_drawdown:.2f}%",
            "Win_Rate": f"{win_rate:.2f}%",
        }
        return bt_df, metrics

    @staticmethod
    def fetch_market_indices():
        """获取大盘主要指数的即时走势数据"""
        indices = {
            "标普 500": "SPY",
            "纳斯达克": "QQQ",
            "道琼斯": "DIA",
            "恐慌指数": "^VIX",
        }
        results = {}
        for name, sym in indices.items():
            try:
                ticker = yf.Ticker(sym)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    last_price = hist["Close"].iloc[-1]
                    prev_price = hist["Close"].iloc[-2]
                    change = (last_price - prev_price) / prev_price * 100
                    results[name] = {
                        "price": f"{last_price:.2f}",
                        "change": f"{change:+.2f}%",
                    }
            except Exception:
                results[name] = {"price": "N/A", "change": "N/A"}
        return results

    @staticmethod
    def fetch_sector_performance():
        """获取主要板块的 ETF 收益表现"""
        sectors = {
            "科技 (XLK)": "XLK",
            "金融 (XLF)": "XLF",
            "医疗 (XLV)": "XLV",
            "消费 (XLY)": "XLY",
            "能源 (XLE)": "XLE",
            "工业 (XLI)": "XLI",
        }
        results = {}
        for name, sym in sectors.items():
            try:
                hist = yf.download(sym, period="1mo", progress=False)
                if not hist.empty:
                    if isinstance(hist.columns, pd.MultiIndex):
                        hist.columns = hist.columns.droplevel(1)
                    monthly_return = (
                        hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1
                    ) * 100
                    results[name] = round(monthly_return, 2)
            except Exception:
                results[name] = 0.0
        return results


# ---------------------------------------------------------------------------
# 4. AI 语言交互与意图解析器
# ---------------------------------------------------------------------------
class AIAssistantService:
    @staticmethod
    def parse_user_intent(user_text: str, current_params: dict) -> dict:
        user_text_lower = user_text.lower()
        action_params = {}

        symbol_match = re.search(r"\b[a-zA-Z]{1,5}\b", user_text)
        if (
            any(
                kw in user_text for kw in ["分析", "切换", "看下", "查", "股票", "标的"]
            )
            and symbol_match
        ):
            potential_symbol = symbol_match.group(0).upper()
            if potential_symbol not in ["MA", "RSI", "MACD", "AI", "K"]:
                action_params["symbol"] = potential_symbol

        ma_s_match = re.search(
            r"(快线|短期|短线|ma1|快均线)[^\d]*(\d+)", user_text_lower
        )
        if ma_s_match:
            action_params["ma_short"] = int(ma_s_match.group(2))

        ma_l_match = re.search(
            r"(慢线|长期|长线|ma2|慢均线)[^\d]*(\d+)", user_text_lower
        )
        if ma_l_match:
            action_params["ma_long"] = int(ma_l_match.group(2))

        if action_params:
            changes = []
            if "symbol" in action_params:
                changes.append(f"标的 -> **{action_params['symbol']}**")
            if "ma_short" in action_params:
                changes.append(f"快线 -> **{action_params['ma_short']}日**")
            if "ma_long" in action_params:
                changes.append(f"慢线 -> **{action_params['ma_long']}日**")
            response_text = (
                f"已识别您的需求！调整参数：{', '.join(changes)}。正在刷新数据..."
            )
        else:
            response_text = (
                "我是您的量化助手。您可以尝试这样跟我交流：\n"
                "• '帮我分析下 AAPL 行情'\n"
                "• '把快线调到 5，慢线调到 20 并重新回测'\n"
                "• '查一下 TSLA 股票'"
            )

        return {"reply": response_text, "actions": action_params}


# ---------------------------------------------------------------------------
# 5. Tkinter 多视图与丰富菜单客户端
# ---------------------------------------------------------------------------
class HDQuantStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QuantStudio AI - 多终端量化金融工作站")
        self.geometry("1500x950")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_dark_theme()

        self.df_data = None
        self.bt_data = None

        # 1. 构建主菜单栏
        self._build_menu_bar()

        # 2. 构建顶部参数控制区
        self._build_header_control()

        # 3. 构建多视图 Notebook 主展示区
        self._build_main_views()

        # 4. 底部状态栏
        self._build_statusbar()

    def configure_dark_theme(self):
        BG_COLOR = "#1e1e1e"
        FG_COLOR = "#ffffff"
        PANEL_BG = "#252526"
        ACCENT_COLOR = "#007acc"

        self.configure(bg=BG_COLOR)
        font_family = (
            "Microsoft YaHei" if platform.system() == "Windows" else "Segoe UI"
        )

        self.style.configure(
            ".", background=BG_COLOR, foreground=FG_COLOR, font=(font_family, 10)
        )
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Panel.TFrame", background=PANEL_BG)
        self.style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR)
        self.style.configure("Header.TLabel", font=(font_family, 11, "bold"))
        self.style.configure(
            "TButton",
            background=ACCENT_COLOR,
            foreground=FG_COLOR,
            borderwidth=0,
            padding=6,
        )
        self.style.map("TButton", background=[("active", "#005999")])
        self.style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab", background=PANEL_BG, foreground=FG_COLOR, padding=[14, 8]
        )
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)])

    # ---------------- 丰富菜单栏系统 ----------------
    def _build_menu_bar(self):
        menubar = tk.Menu(
            self,
            bg="#252526",
            fg="#ffffff",
            activebackground="#007acc",
            activeforeground="#ffffff",
            borderwidth=0,
        )

        # === 1. 文件 (File) ===
        file_menu = tk.Menu(
            menubar, tearoff=0, bg="#252526", fg="#ffffff", activebackground="#007acc"
        )
        file_menu.add_command(
            label="📁 导出行情与回测数据 (CSV)", command=self._export_csv
        )
        file_menu.add_separator()
        file_menu.add_command(label="🧹 清空 AI 聊天历史", command=self._clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="❌ 退出系统", command=self.quit)
        menubar.add_cascade(label="文件 (F)", menu=file_menu)

        # === 2. 视图切换 (View) ===
        view_menu = tk.Menu(
            menubar, tearoff=0, bg="#252526", fg="#ffffff", activebackground="#007acc"
        )
        view_menu.add_command(
            label="📈 切换至: 单股量化与 AI 对话",
            command=lambda: self.main_notebook.select(self.view_quant),
        )
        view_menu.add_command(
            label="🌐 切换至: 全球大盘监控",
            command=lambda: self._switch_to_view(
                self.view_market, self._load_market_view
            ),
        )
        view_menu.add_command(
            label="📊 切换至: 行业板块强弱",
            command=lambda: self._switch_to_view(
                self.view_sector, self._load_sector_view
            ),
        )
        view_menu.add_command(
            label="🔥 切换至: 实时热点与资讯",
            command=lambda: self._switch_to_view(self.view_news, self._load_news_view),
        )
        menubar.add_cascade(label="视图 (V)", menu=view_menu)

        # === 3. 策略配置 (Strategy) ===
        strat_menu = tk.Menu(
            menubar, tearoff=0, bg="#252526", fg="#ffffff", activebackground="#007acc"
        )
        strat_menu.add_command(
            label="⚡ 默认均线策略 (MA10 / MA50)",
            command=lambda: self._set_preset_ma(10, 50),
        )
        strat_menu.add_command(
            label="🚀 短线高频预设 (MA5 / MA20)",
            command=lambda: self._set_preset_ma(5, 20),
        )
        strat_menu.add_command(
            label="🐢 趋势跟预设 (MA20 / MA100)",
            command=lambda: self._set_preset_ma(20, 100),
        )
        menubar.add_cascade(label="策略 (S)", menu=strat_menu)

        # === 4. 工具与工具箱 (Tools) ===
        tools_menu = tk.Menu(
            menubar, tearoff=0, bg="#252526", fg="#ffffff", activebackground="#007acc"
        )
        tools_menu.add_command(
            label="🔄 刷新当前标的数据", command=self.start_analysis_thread
        )
        tools_menu.add_command(
            label="⚙️ 快捷指令集帮助", command=self._show_usage_guide
        )
        menubar.add_cascade(label="工具 (T)", menu=tools_menu)

        # === 5. 帮助 (Help) ===
        help_menu = tk.Menu(
            menubar, tearoff=0, bg="#252526", fg="#ffffff", activebackground="#007acc"
        )
        help_menu.add_command(label="💡 系统说明书", command=self._show_usage_guide)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ 关于 QuantStudio AI", command=self._show_about)
        menubar.add_cascade(label="帮助 (H)", menu=help_menu)

        self.config(menu=menubar)

    def _switch_to_view(self, view_frame, callback_func):
        self.main_notebook.select(view_frame)
        callback_func()

    # ---------------- 视图构建与布局 ----------------
    def _build_header_control(self):
        control_frame = ttk.Frame(self, padding=8, style="Panel.TFrame")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(control_frame, text="标的代码:").grid(row=0, column=0, padx=5)
        self.entry_symbol = ttk.Entry(control_frame, width=8)
        self.entry_symbol.insert(0, "NVDA")
        self.entry_symbol.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="开始日期:").grid(row=0, column=2, padx=5)
        self.entry_start = ttk.Entry(control_frame, width=10)
        self.entry_start.insert(0, "2023-01-01")
        self.entry_start.grid(row=0, column=3, padx=5)

        ttk.Label(control_frame, text="结束日期:").grid(row=0, column=4, padx=5)
        self.entry_end = ttk.Entry(control_frame, width=10)
        self.entry_end.insert(0, "2026-01-01")
        self.entry_end.grid(row=0, column=5, padx=5)

        ttk.Label(control_frame, text="快/慢均线:").grid(row=0, column=6, padx=5)
        self.entry_ma_s = ttk.Entry(control_frame, width=4)
        self.entry_ma_s.insert(0, "10")
        self.entry_ma_s.grid(row=0, column=7, padx=2)

        self.entry_ma_l = ttk.Entry(control_frame, width=4)
        self.entry_ma_l.insert(0, "50")
        self.entry_ma_l.grid(row=0, column=8, padx=2)

        self.btn_fetch = ttk.Button(
            control_frame, text="运行分析与回测", command=self.start_analysis_thread
        )
        self.btn_fetch.grid(row=0, column=9, padx=15)

    def _build_main_views(self):
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- View 1: 核心单股量化与 AI 交互窗口 ---
        self.view_quant = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.view_quant, text="📈 核心单股与 AI 对话")
        self._build_quant_view_layout(self.view_quant)

        # --- View 2: 大盘全局监控窗口 ---
        self.view_market = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.view_market, text="🌐 全球大盘监控")

        # --- View 3: 行业板块强弱对比窗口 ---
        self.view_sector = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.view_sector, text="📊 行业板块分析")

        # --- View 4: 实时热点与资讯 ---
        self.view_news = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.view_news, text="🔥 市场最热资讯")

    def _build_quant_view_layout(self, parent):
        main_pane = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # 左侧面板
        left_frame = ttk.Frame(main_pane, width=380, style="Panel.TFrame")
        main_pane.add(left_frame, weight=2)

        chat_frame = ttk.LabelFrame(
            left_frame, text="🤖 Quant AI 自然语言助手", padding=10
        )
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        font_family = (
            "Microsoft YaHei" if platform.system() == "Windows" else "Consolas"
        )
        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#00e676",
            font=(font_family, 10),
            insertbackground="white",
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self._append_chat(
            "AI",
            "您好！在菜单栏的 [视图] 中可以随时切换看盘、板块与资讯。输入指令可实时调整股票。",
        )

        input_box = ttk.Frame(chat_frame)
        input_box.pack(fill=tk.X)

        self.chat_input = tk.Entry(
            input_box,
            bg="white",  # 输入框背景色：白色
            fg="black",  # 输入的文字颜色：黑色
            insertbackground="black",  # 闪烁的光标颜色：黑色
            relief="solid",  # 边框样式
            bd=1,
        )
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", lambda e: self.send_ai_message())

        btn_send = ttk.Button(input_box, text="发送", command=self.send_ai_message)
        btn_send.pack(side=tk.RIGHT)

        metrics_frame = ttk.LabelFrame(left_frame, text="📊 策略绩效看板", padding=10)
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)

        self.metrics_vars = {
            "Total_Return": tk.StringVar(value="--"),
            "Sharpe_Ratio": tk.StringVar(value="--"),
            "Max_Drawdown": tk.StringVar(value="--"),
            "Win_Rate": tk.StringVar(value="--"),
        }

        labels_map = {
            "Total_Return": "累计收益率:",
            "Sharpe_Ratio": "夏普比率 (Sharpe):",
            "Max_Drawdown": "历史最大回撤:",
            "Win_Rate": "交易胜率:",
        }

        for k, label in labels_map.items():
            f = ttk.Frame(metrics_frame)
            f.pack(fill=tk.X, pady=3)
            ttk.Label(f, text=label, font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
            ttk.Label(
                f,
                textvariable=self.metrics_vars[k],
                font=("Microsoft YaHei", 11, "bold"),
                foreground="#00e676",
            ).pack(side=tk.RIGHT)

        # 右侧图表 Notebook
        right_notebook = ttk.Notebook(main_pane)
        main_pane.add(right_notebook, weight=5)

        self.tab_chart = ttk.Frame(right_notebook)
        right_notebook.add(self.tab_chart, text="行情与技术指标 (K线/MACD/RSI)")

        self.tab_backtest = ttk.Frame(right_notebook)
        right_notebook.add(self.tab_backtest, text="策略回测与基准对比")

    # ---------------- 视图动态加载逻辑 ----------------
    def _load_market_view(self):
        for child in self.view_market.winfo_children():
            child.destroy()

        frame = ttk.Frame(self.view_market, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame, text="🌐 全球主要指数实时行情", font=("Microsoft YaHei", 14, "bold")
        ).pack(anchor=tk.W, pady=10)

        loading_label = ttk.Label(
            frame, text="正在加载全球大盘数据，请稍候...", font=("Microsoft YaHei", 11)
        )
        loading_label.pack(anchor=tk.W)

        def async_load():
            data = QuantEngine.fetch_market_indices()
            self.after(0, lambda: self._render_market_cards(frame, loading_label, data))

        threading.Thread(target=async_load, daemon=True).start()

    def _render_market_cards(self, parent_frame, loading_label, data):
        loading_label.destroy()
        cards_frame = ttk.Frame(parent_frame)
        cards_frame.pack(fill=tk.X, pady=10)

        col = 0
        for name, info in data.items():
            card = ttk.LabelFrame(cards_frame, text=name, padding=15)
            card.grid(row=0, column=col, padx=10, sticky="ew")

            price_str = info["price"]
            chg_str = info["change"]
            color = (
                "#00e676"
                if "+" in chg_str
                else ("#ff5252" if "-" in chg_str else "white")
            )

            ttk.Label(
                card, text=f"现价: {price_str}", font=("Microsoft YaHei", 12)
            ).pack(anchor=tk.W)
            ttk.Label(
                card,
                text=f"涨跌幅: {chg_str}",
                font=("Microsoft YaHei", 14, "bold"),
                foreground=color,
            ).pack(anchor=tk.W, pady=5)
            col += 1

    def _load_sector_view(self):
        for child in self.view_sector.winfo_children():
            child.destroy()

        frame = ttk.Frame(self.view_sector, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="📊 美股美标近30日板块强弱对比",
            font=("Microsoft YaHei", 14, "bold"),
        ).pack(anchor=tk.W, pady=10)

        def async_load():
            sector_data = QuantEngine.fetch_sector_performance()
            self.after(0, lambda: self._render_sector_chart(frame, sector_data))

        threading.Thread(target=async_load, daemon=True).start()

    def _render_sector_chart(self, parent_frame, data):
        fig = Figure(figsize=(8, 4), dpi=120, facecolor="#1e1e1e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#252526")
        ax.tick_params(colors="white", labelsize=9)

        names = list(data.keys())
        returns = list(data.values())
        colors = ["#00c853" if r >= 0 else "#d50000" for r in returns]

        bars = ax.barh(names, returns, color=colors)
        ax.set_xlabel("月度收益率 (%)", color="white")
        ax.set_title("各板块近30日动量表现", color="white")
        ax.grid(True, color="#333333", linestyle="--", alpha=0.5)

        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (0.2 if width >= 0 else -0.8),
                bar.get_y() + bar.get_height() / 2,
                f"{width:.2f}%",
                color="white",
                va="center",
                fontsize=8,
            )

        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _load_news_view(self):
        for child in self.view_news.winfo_children():
            child.destroy()

        frame = ttk.Frame(self.view_news, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="🔥 市场最热资讯与重大事件情报",
            font=("Microsoft YaHei", 14, "bold"),
        ).pack(anchor=tk.W, pady=10)

        news_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            bg="#252526",
            fg="#ffffff",
            font=("Microsoft YaHei", 10),
            padding=10,
        )
        news_text.pack(fill=tk.BOTH, expand=True)

        sample_news = (
            "【美联储议息会议前瞻】市场普遍预期维持利率不变，重点关注终端利率预期...\n\n"
            "【科技巨头财报】英伟达 (NVDA) 发布新一代 AI 芯片架构，分析师上调目标价至 $150...\n\n"
            "【能源板块动向】原油价格受地缘政治因素推动上涨 2.5%，XLE ETF 同步跟涨...\n\n"
            "【量化观点】当前大盘 VIX 维持在低位，均线突破策略在科技权重股中保持较高胜率。"
        )
        news_text.insert(tk.END, sample_news)
        news_text.config(state=tk.DISABLED)

    # ---------------- 辅助逻辑与响应函数 ----------------
    def _export_csv(self):
        if self.df_data is None or self.df_data.empty:
            messagebox.showwarning("警告", "当前没有可导出的数据，请先运行量化分析！")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            title="保存行情与指标数据",
        )
        if file_path:
            try:
                export_df = self.df_data.copy()
                if self.bt_data is not None:
                    export_df["Strategy_Cum"] = self.bt_data["Strategy_Cum"]
                export_df.to_csv(file_path)
                messagebox.showinfo("成功", f"数据已成功导出至:\n{file_path}")
            except Exception as e:
                messagebox.showerror("导出失败", str(e))

    def _clear_chat(self):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete("1.0", tk.END)
        self.chat_history.config(state=tk.DISABLED)
        self._append_chat("AI", "聊天历史已清空。您可以继续输入指令。")

    def _set_preset_ma(self, short_ma: int, long_ma: int):
        self.entry_ma_s.delete(0, tk.END)
        self.entry_ma_s.insert(0, str(short_ma))
        self.entry_ma_l.delete(0, tk.END)
        self.entry_ma_l.insert(0, str(long_ma))
        self.start_analysis_thread()

    def _show_usage_guide(self):
        guide_msg = (
            "【QuantStudio AI 使用指南】\n\n"
            "1. 顶部菜单 [视图 (View)]：可以随意切换量化回测、大盘看盘、板块强弱以及新闻资讯。\n"
            "2. AI 对话调整：直接在对话框输入 '分析 AAPL' 或 '快线改成 5' 即可自动调整并计算。\n"
            "3. 数据导出：点击 [文件] -> [导出数据] 可保存完整回测 CSV 文件。"
        )
        messagebox.showinfo("使用指南", guide_msg)

    def _show_about(self):
        messagebox.showinfo(
            "关于 QuantStudio AI",
            "QuantStudio AI v3.0 - 多视图终端量化工作站\n\n"
            "• 支持多窗口模式：大盘监控 / 行业分析 / 资讯聚合 / 策略回测\n"
            "• GUI 架构: Tkinter Multi-View Notebook",
        )

    def _build_statusbar(self):
        self.status_var = tk.StringVar(
            value="系统就绪。请选择视图或点击运行量化计算..."
        )
        status_bar = ttk.Label(
            self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=4
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _append_chat(self, sender: str, text: str):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"[{sender}]: {text}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def send_ai_message(self):
        user_text = self.chat_input.get().strip()
        if not user_text:
            return

        self._append_chat("用户", user_text)
        self.chat_input.delete(0, tk.END)

        threading.Thread(
            target=self._process_ai_interaction, args=(user_text,), daemon=True
        ).start()

    def _process_ai_interaction(self, user_text: str):
        """主线程调用的异步解耦入口"""
        curr_params = {
            "symbol": self.entry_symbol.get(),
            "ma_short": self.entry_ma_s.get(),
            "ma_long": self.entry_ma_l.get(),
        }

        def run_mcp_pipeline():
            # 在独立后台子线程中启动全新的 Asyncio 事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 执行 MCP 分析与工具路由链
                result = loop.run_until_complete(
                    MCPIntentAnalyzer.analyze_and_execute(user_text, curr_params)
                )
            except Exception as err:
                result = {"reply": f"MCP 系统运行异常: {str(err)}", "actions": {}}
            finally:
                loop.close()

            # 安全切回主线程 GUI 渲染
            self.after(0, lambda: self._handle_ai_response(result))

        # 后台线程不阻塞 GUI
        threading.Thread(target=run_mcp_pipeline, daemon=True).start()

    def _handle_ai_response(self, result: dict):
        self._append_chat("AI", result["reply"])
        actions = result.get("actions", {})

        need_recalculate = False
        if "symbol" in actions:
            self.entry_symbol.delete(0, tk.END)
            self.entry_symbol.insert(0, actions["symbol"])
            need_recalculate = True

        if "ma_short" in actions:
            self.entry_ma_s.delete(0, tk.END)
            self.entry_ma_s.insert(0, str(actions["ma_short"]))
            need_recalculate = True

        if "ma_long" in actions:
            self.entry_ma_l.delete(0, tk.END)
            self.entry_ma_l.insert(0, str(actions["ma_long"]))
            need_recalculate = True

        # if need_recalculate:
        #     self.start_analysis_thread()

    def start_analysis_thread(self):
        self.btn_fetch.config(state=tk.DISABLED)
        self.status_var.set("正在抓取行情数据并刷新渲染...")
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def _run_analysis(self):
        try:
            symbol = self.entry_symbol.get().strip()
            start = self.entry_start.get().strip()
            end = self.entry_end.get().strip()
            ma_s = int(self.entry_ma_s.get())
            ma_l = int(self.entry_ma_l.get())

            df = QuantEngine.fetch_data(symbol, start, end)
            df = QuantEngine.add_indicators(df, ma_short=ma_s, ma_long=ma_l)
            bt_df, metrics = QuantEngine.run_ma_backtest(df)

            self.df_data = df
            self.bt_data = bt_df

            self.after(0, lambda: self._update_ui(metrics))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("计算错误", str(e)))
            self.after(0, lambda: self.status_var.set("数据加载中断。"))
        finally:
            self.after(0, lambda: self.btn_fetch.config(state=tk.NORMAL))

    def _update_ui(self, metrics: dict):
        for k, v in metrics.items():
            self.metrics_vars[k].set(v)

        self._plot_tech_charts()
        self._plot_backtest_charts()
        self.status_var.set("行情与技术指标渲染完毕。")

    def _plot_tech_charts(self):
        for child in self.tab_chart.winfo_children():
            child.destroy()

        fig = Figure(figsize=(10, 7), dpi=120, facecolor="#1e1e1e")
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.15)

        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax3 = fig.add_subplot(gs[2], sharex=ax1)

        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor("#252526")
            ax.tick_params(colors="white", labelsize=8)
            ax.grid(True, color="#333333", linestyle="--", alpha=0.5)

        ax1.plot(
            self.df_data.index,
            self.df_data["Close"],
            label="收盘价",
            color="#ffffff",
            alpha=0.6,
            linewidth=1.2,
        )
        ax1.plot(
            self.df_data.index,
            self.df_data["MA_Short"],
            label="短期均线",
            color="#ff9800",
            linewidth=1.2,
        )
        ax1.plot(
            self.df_data.index,
            self.df_data["MA_Long"],
            label="长期均线",
            color="#2196f3",
            linewidth=1.2,
        )
        ax1.set_title(
            f"{self.entry_symbol.get().upper()} K线与趋势分析",
            color="white",
            fontsize=10,
        )
        ax1.legend(
            loc="upper left", facecolor="#1e1e1e", labelcolor="white", fontsize=8
        )

        ax2.plot(
            self.df_data.index,
            self.df_data["DIF"],
            label="DIF",
            color="#00e676",
            linewidth=1,
        )
        ax2.plot(
            self.df_data.index,
            self.df_data["DEA"],
            label="DEA",
            color="#ff4081",
            linewidth=1,
        )
        colors = np.where(self.df_data["MACD"] >= 0, "#00c853", "#d50000")
        ax2.bar(self.df_data.index, self.df_data["MACD"], color=colors, width=1)
        ax2.legend(
            loc="upper left", facecolor="#1e1e1e", labelcolor="white", fontsize=8
        )

        ax3.plot(
            self.df_data.index,
            self.df_data["RSI"],
            label="RSI(14)",
            color="#ab47bc",
            linewidth=1,
        )
        ax3.axhline(70, color="#ff5252", linestyle=":", alpha=0.7)
        ax3.axhline(30, color="#69f0ae", linestyle=":", alpha=0.7)
        ax3.set_ylim(0, 100)
        ax3.legend(
            loc="upper left", facecolor="#1e1e1e", labelcolor="white", fontsize=8
        )

        canvas = FigureCanvasTkAgg(fig, master=self.tab_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.tab_chart)
        toolbar.update()

    def _plot_backtest_charts(self):
        for child in self.tab_backtest.winfo_children():
            child.destroy()

        fig = Figure(figsize=(10, 7), dpi=120, facecolor="#1e1e1e")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#252526")
        ax.tick_params(colors="white", labelsize=8)
        ax.grid(True, color="#333333", linestyle="--", alpha=0.5)

        ax.plot(
            self.bt_data.index,
            self.bt_data["Market_Cum"],
            label="基准 (买入持有)",
            color="#9e9e9e",
            linestyle="--",
            linewidth=1.2,
        )
        ax.plot(
            self.bt_data.index,
            self.bt_data["Strategy_Cum"],
            label="双均线量化策略",
            color="#00e676",
            linewidth=1.8,
        )

        ax.set_title("策略净值与基准对比", color="white", fontsize=10)
        ax.legend(loc="upper left", facecolor="#1e1e1e", labelcolor="white", fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=self.tab_backtest)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = HDQuantStudioApp()
    app.mainloop()
