from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from gateways.data_manager import DataManager

# ============================================================
# 全局数据管理器
# ============================================================

data: DataManager | None = None


# ============================================================
# 服务生命周期
# ============================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    global data

    # ==================== 启动 ====================

    print()
    print("=" * 60)
    print("正在启动股票数据服务...")
    print("数据源：yinhe")
    print("=" * 60)

    try:
        data = DataManager("yinhe")
        data.start()

        print("✅ 股票数据服务启动成功")

    except Exception as exc:
        data = None

        print(f"❌ 股票数据服务启动失败：{exc}")

        raise

    # ==================== 运行 ====================

    yield

    # ==================== 关闭 ====================

    print()
    print("=" * 60)
    print("正在关闭股票数据服务...")
    print("=" * 60)

    if data is not None:
        try:
            data.stop()
            print("✅ 数据源已关闭")

        except Exception as exc:
            print(f"⚠️ 关闭数据源失败：{exc}")

        finally:
            data = None


def require_data() -> DataManager:
    """
    获取 DataManager。

    如果数据源没有启动，直接抛出异常。
    """

    if data is None:

        raise RuntimeError("数据源尚未启动")

    return data


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="A股股票研究中心 API",
    description="股票行情与研究数据 API",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# 路径配置
# ============================================================

# 项目根目录下的前端目录
FRONTEND_DIR = Path("docs/stock_center")


# ============================================================
# API：健康检查
# ============================================================


@app.get("/api/health")
def health_check():
    """
    检查 API 和数据服务是否正常。
    """

    return {
        "success": True,
        "api": "running",
        "data_source": "yinhe",
        "data_manager": data is not None,
    }


# ============================================================
# API：市场指数
# ============================================================


@app.get("/api/indices")
def get_indices(indices: str = Query(...)):
    """
    获取指定指数行情。

    示例：
        /api/indices?indices=000001,399001,399006,000688
    """

    if data is None:
        return {
            "success": False,
            "message": "数据源尚未启动",
        }

    symbols = [
        symbol.strip().upper() for symbol in indices.split(",") if symbol.strip()
    ]

    try:
        quotes = data.get_quotes(symbols)

    except Exception as exc:
        print(f"❌ 批量获取指数行情失败：{exc}")

        return {
            "success": False,
            "message": "获取指数行情失败",
        }

    result = []

    for quote in quotes:
        result.append(
            {
                "code": quote.symbol,
                "name": quote.name,
                "price": quote.last_price,
                "change": quote.change,
                "changePercent": quote.change_percent,
            }
        )

    return {
        "success": True,
        "data": result,
    }


# =========================================================
# 1. 股票行情
# =========================================================


def success(
    symbol: str,
    data_value: Any = None,
) -> dict:

    return {
        "success": True,
        "symbol": symbol,
        "data": data_value,
    }


def failure(
    symbol: str,
    message: str = "暂无数据",
) -> dict:

    return {
        "success": False,
        "symbol": symbol,
        "message": message,
        "data": None,
    }


@app.get("/api/stock/{symbol}")
def get_stock(symbol: str):

    symbol = symbol.strip().upper()

    print(f"📊 获取股票信息：{symbol}")

    try:

        manager = require_data()

        stock = manager.get_stock(symbol)

        if stock is None:

            return failure(
                symbol,
                "未获取到股票信息",
            )
        else:
            print(stock)

        return success(
            symbol,
            {
                "symbol": stock.symbol,
                "name": stock.name,
                "market": getattr(stock, "market", None),
                "area": getattr(stock, "area", None),
                "listDate": getattr(stock, "list_date", None),
            },
        )

    except NotImplementedError:

        return failure(
            symbol,
            "当前数据源暂未实现股票信息接口",
        )

    except Exception as exc:

        print(f"❌ 股票信息获取失败：{symbol} -> {exc}")

        return failure(
            symbol,
            "股票信息暂不可用",
        )


@app.get("/api/industry_category/{symbol}")
def get_industry_category(symbol: str):

    symbol = symbol.strip().upper()

    print(f"📊 获取行业分类信息：{symbol}")

    try:

        manager = require_data()

        industry = manager.get_industry(symbol)

        if industry is None:

            return failure(
                symbol,
                "未获取到行业信息",
            )
        else:
            print(industry)

        return success(
            symbol,
            {
                "symbol": industry.symbol,
                "name": industry.name,
                "l1": getattr(industry, "level_1", None),
                "l2": getattr(industry, "level_2", None),
                "l3": getattr(industry, "level_3", None),
                "l4": getattr(industry, "level_4", None),
            },
        )

    except NotImplementedError:

        return failure(
            symbol,
            "当前数据源暂未实现行业信息接口",
        )

    except Exception as exc:

        print(f"❌ 行业信息获取失败：{symbol} -> {exc}")

        return failure(
            symbol,
            "行业信息暂不可用",
        )


@app.get("/api/quote/{symbol}")
def get_quote(symbol: str):

    symbol = symbol.strip().upper()

    print(f"📈 获取行情：{symbol}")

    try:

        manager = require_data()

        quote = manager.get_quote(symbol)

        if quote is None:

            return failure(
                symbol,
                "未获取到行情数据",
            )
        else:
            print(quote)

        return success(
            symbol,
            {
                "symbol": quote.symbol,
                "name": getattr(quote, "name", None),
                "lastPrice": getattr(
                    quote,
                    "last_price",
                    None,
                ),
                "change": getattr(
                    quote,
                    "change",
                    None,
                ),
                "changePercent": getattr(
                    quote,
                    "change_percent",
                    None,
                ),
                "openPrice": getattr(
                    quote,
                    "open_price",
                    None,
                ),
                "highPrice": getattr(
                    quote,
                    "high_price",
                    None,
                ),
                "lowPrice": getattr(
                    quote,
                    "low_price",
                    None,
                ),
                "previousClose": getattr(
                    quote,
                    "previous_close",
                    None,
                ),
                "volume": getattr(
                    quote,
                    "volume",
                    None,
                ),
                "amount": getattr(
                    quote,
                    "amount",
                    None,
                ),
                "turnover": getattr(
                    quote,
                    "turnover",
                    None,
                ),
                "marketCap": getattr(
                    quote,
                    "market_cap",
                    None,
                ),
                "floatMarketCap": getattr(
                    quote,
                    "float_market_cap",
                    None,
                ),
            },
        )

    except NotImplementedError:

        return failure(
            symbol,
            "当前数据源暂未实现行情接口",
        )

    except Exception as exc:

        print(f"❌ 行情获取失败：{symbol} -> {exc}")

        return failure(
            symbol,
            "行情数据暂不可用",
        )


# =========================================================
# 2. K线
# =========================================================


@app.get("/api/kline/{symbol}")
def get_kline(
    symbol: str,
    interval: str = Query(
        "1d",
        description="K线周期",
    ),
    limit: int = Query(
        120,
        ge=1,
        le=1000,
    ),
):

    symbol = symbol.strip().upper()

    print(f"📊 获取K线：" f"{symbol} " f"interval={interval} " f"limit={limit}")

    try:

        manager = require_data()

        # -------------------------------------------------
        # 这里暂时调用你的 DataManager
        #
        # 如果你现在还没有这个方法，
        # 先返回暂无数据即可。
        # -------------------------------------------------

        if not hasattr(manager, "get_kline"):

            return failure(
                symbol,
                "K线接口暂未实现",
            )

        klines = manager.get_kline(
            symbol,
            interval=interval,
            limit=limit,
        )
        if not klines:

            return failure(
                symbol,
                "暂无K线数据",
            )

        result = []

        for item in klines:

            result.append(
                {
                    "timestamp": getattr(
                        item,
                        "timestamp",
                        None,
                    ),
                    "open": getattr(
                        item,
                        "open",
                        None,
                    ),
                    "high": getattr(
                        item,
                        "high",
                        None,
                    ),
                    "low": getattr(
                        item,
                        "low",
                        None,
                    ),
                    "close": getattr(
                        item,
                        "close",
                        None,
                    ),
                    "volume": getattr(
                        item,
                        "volume",
                        None,
                    ),
                    "amount": getattr(
                        item,
                        "amount",
                        None,
                    ),
                }
            )

        return success(
            symbol,
            {
                "interval": interval,
                "data": result,
            },
        )

    except NotImplementedError:

        return failure(
            symbol,
            "K线接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ K线获取失败：{symbol} -> {exc}")

        return failure(
            symbol,
            "K线数据暂不可用",
        )


# =========================================================
# 3. 财务数据
# =========================================================


@app.get("/api/financial/{symbol}")
def get_financial(symbol: str):

    symbol = symbol.strip().upper()

    print(f"💰 获取财务数据：{symbol}")

    try:

        manager = require_data()

        if not hasattr(
            manager,
            "get_financial",
        ):

            return failure(
                symbol,
                "财务接口暂未实现",
            )

        result = manager.get_financial(symbol)

        if result is None:

            return failure(
                symbol,
                "暂无财务数据",
            )

        return success(
            symbol,
            result,
        )

    except NotImplementedError:

        return failure(
            symbol,
            "财务接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ 财务数据获取失败：" f"{symbol} -> {exc}")

        return failure(
            symbol,
            "财务数据暂不可用",
        )


# =========================================================
# 4. 估值数据
# =========================================================


@app.get("/api/valuation/{symbol}")
def get_valuation(symbol: str):

    symbol = symbol.strip().upper()

    print(f"💎 获取估值数据：{symbol}")

    try:

        manager = require_data()

        if not hasattr(
            manager,
            "get_valuation",
        ):

            return failure(
                symbol,
                "估值接口暂未实现",
            )

        valuation = manager.get_valuation(symbol)

        if valuation is None:

            return failure(
                symbol,
                "暂无估值数据",
            )

        return success(
            symbol,
            {
                "pe": getattr(
                    valuation,
                    "pe",
                    None,
                ),
                "peTtm": getattr(
                    valuation,
                    "pe_ttm",
                    None,
                ),
                "pb": getattr(
                    valuation,
                    "pb",
                    None,
                ),
                "ps": getattr(
                    valuation,
                    "ps",
                    None,
                ),
                "marketCap": getattr(
                    valuation,
                    "market_cap",
                    None,
                ),
                "roe": getattr(
                    valuation,
                    "roe",
                    None,
                ),
            },
        )

    except NotImplementedError:

        return failure(
            symbol,
            "估值接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ 估值获取失败：" f"{symbol} -> {exc}")

        return failure(
            symbol,
            "估值数据暂不可用",
        )


# =========================================================
# 5. 行业数据
# =========================================================


@app.get("/api/industry/{symbol}")
def get_industry(symbol: str):

    symbol = symbol.strip().upper()

    print(f"🏭 获取行业数据：{symbol}")

    try:

        manager = require_data()

        if not hasattr(
            manager,
            "get_industry",
        ):

            return failure(
                symbol,
                "行业接口暂未实现",
            )

        industry = manager.get_industry(symbol)

        if industry is None:

            return failure(
                symbol,
                "暂无行业数据",
            )

        return success(
            symbol,
            industry,
        )

    except NotImplementedError:

        return failure(
            symbol,
            "行业接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ 行业数据获取失败：" f"{symbol} -> {exc}")

        return failure(
            symbol,
            "行业数据暂不可用",
        )


# =========================================================
# 6. 技术指标
# =========================================================


@app.get("/api/technical/{symbol}")
def get_technical(symbol: str):

    symbol = symbol.strip().upper()

    print(f"📐 获取技术指标：{symbol}")

    try:

        manager = require_data()

        if not hasattr(
            manager,
            "get_technical",
        ):

            return failure(
                symbol,
                "技术指标接口暂未实现",
            )

        technical = manager.get_technical(symbol)

        if technical is None:

            return failure(
                symbol,
                "暂无技术指标数据",
            )

        return success(
            symbol,
            technical,
        )

    except NotImplementedError:

        return failure(
            symbol,
            "技术指标接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ 技术指标获取失败：" f"{symbol} -> {exc}")

        return failure(
            symbol,
            "技术指标暂不可用",
        )


# =========================================================
# 7. 新闻
# =========================================================


@app.get("/api/news/{symbol}")
def get_news(
    symbol: str,
    limit: int = Query(
        10,
        ge=1,
        le=100,
    ),
):

    symbol = symbol.strip().upper()

    print(f"📰 获取新闻：" f"{symbol} limit={limit}")

    try:

        manager = require_data()

        if not hasattr(
            manager,
            "get_news",
        ):

            return failure(
                symbol,
                "新闻接口暂未实现",
            )

        news = manager.get_news(
            symbol,
            limit=limit,
        )

        if not news:

            return failure(
                symbol,
                "暂无新闻",
            )

        return success(
            symbol,
            news,
        )

    except NotImplementedError:

        return failure(
            symbol,
            "新闻接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ 新闻获取失败：" f"{symbol} -> {exc}")

        return failure(
            symbol,
            "新闻数据暂不可用",
        )


# =========================================================
# 8. 公告
# =========================================================


@app.get("/api/announcement/{symbol}")
def get_announcements(
    symbol: str,
    limit: int = Query(
        10,
        ge=1,
        le=100,
    ),
):

    symbol = symbol.strip().upper()

    print(f"📢 获取公告：" f"{symbol} limit={limit}")

    try:

        manager = require_data()

        if not hasattr(
            manager,
            "get_announcements",
        ):

            return failure(
                symbol,
                "公告接口暂未实现",
            )

        announcements = manager.get_announcements(
            symbol,
            limit=limit,
        )

        if not announcements:

            return failure(
                symbol,
                "暂无公告",
            )

        return success(
            symbol,
            announcements,
        )

    except NotImplementedError:

        return failure(
            symbol,
            "公告接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ 公告获取失败：" f"{symbol} -> {exc}")

        return failure(
            symbol,
            "公告数据暂不可用",
        )


# =========================================================
# 9. AI研究
# =========================================================


@app.get("/api/ai/{symbol}")
def get_ai_research(symbol: str):

    symbol = symbol.strip().upper()

    print(f"🤖 获取AI研究：{symbol}")

    try:

        manager = require_data()

        if not hasattr(
            manager,
            "get_ai_research",
        ):

            return failure(
                symbol,
                "AI研究接口暂未实现",
            )

        result = manager.get_ai_research(symbol)

        if result is None:

            return failure(
                symbol,
                "暂无AI研究数据",
            )

        return success(
            symbol,
            result,
        )

    except NotImplementedError:

        return failure(
            symbol,
            "AI研究接口暂未实现",
        )

    except Exception as exc:

        print(f"❌ AI研究获取失败：" f"{symbol} -> {exc}")

        return failure(
            symbol,
            "AI研究数据暂不可用",
        )


# ============================================================
# 静态文件
# ============================================================

app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="js",
)


app.mount(
    "/stock",
    StaticFiles(
        directory=FRONTEND_DIR / "stock",
        html=True,
    ),
    name="stock",
)

app.mount(
    "/trade",
    StaticFiles(
        directory=FRONTEND_DIR / "trade",
        html=True,
    ),
    name="trade",
)

app.mount(
    "/document",
    StaticFiles(
        directory=FRONTEND_DIR / "document",
        html=True,
    ),
    name="document",
)

app.mount(
    "/tools",
    StaticFiles(
        directory=FRONTEND_DIR / "tools",
        html=True,
    ),
    name="tools",
)

app.mount(
    "/news",
    StaticFiles(
        directory=FRONTEND_DIR / "news",
        html=True,
    ),
    name="news",
)

app.mount(
    "/research",
    StaticFiles(
        directory=FRONTEND_DIR / "research",
        html=True,
    ),
    name="research",
)


# ============================================================
# 首页
# ============================================================


@app.get("/")
def index():
    """
    返回股票研究中心首页。
    """

    return FileResponse(FRONTEND_DIR / "index.html")
