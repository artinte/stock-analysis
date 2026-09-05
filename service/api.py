from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from gateways.data_manager import DataManager

# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="A股股票研究中心 API",
    description="股票行情与研究数据 API",
    version="1.0.0",
)


# ============================================================
# 路径配置
# ============================================================

# 项目根目录下的前端目录
FRONTEND_DIR = Path("docs/stock_center")


# ============================================================
# 全局数据管理器
# ============================================================

data: DataManager | None = None


# ============================================================
# 服务启动
# ============================================================


@app.on_event("startup")
def startup() -> None:
    global data

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


# ============================================================
# 服务关闭
# ============================================================


@app.on_event("shutdown")
def shutdown() -> None:
    global data

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
# API：获取股票行情
# ============================================================


@app.get("/api/quote/{symbol}")
def get_quote(symbol: str):
    """
    获取指定股票的实时行情。

    示例：

        /api/quote/600519.SH
        /api/quote/600519
    """

    if data is None:
        return {
            "success": False,
            "message": "数据源尚未启动",
            "symbol": symbol,
        }

    try:
        print(f"📈 获取股票行情：{symbol}")

        quote = data.get_quote(symbol)

        if quote is None:
            return {
                "success": False,
                "message": "未获取到行情数据",
                "symbol": symbol,
            }

        # 使用现有模型自己的 display 方法
        quote.display()

        return {
            "success": True,
            "symbol": quote.symbol,
            "price": quote.last_price,
        }

    except NotImplementedError:
        return {
            "success": False,
            "message": "当前数据源暂未实现行情数据接口",
            "symbol": symbol,
        }

    except Exception as exc:
        print(f"❌ 获取股票行情失败：{symbol} -> {exc}")

        return {
            "success": False,
            "message": f"获取行情失败：{exc}",
            "symbol": symbol,
        }


# ============================================================
# API：市场指数
# ============================================================


@app.get("/api/indices")
def get_indices():

    if data is None:
        return {
            "success": False,
            "message": "数据源尚未启动",
        }

    symbols = [
        "000001.SH",
        "399001.SZ",
        "399006.SZ",
        "000688.SH",
    ]

    indices = []

    for symbol in symbols:

        try:
            quote = data.get_quote(symbol)

            if quote is None:
                continue

            indices.append({
                "code": quote.symbol,
                "name": quote.name,
                "price": quote.last_price,
                "change": quote.change,
                "changePercent": quote.change_percent,
            })

        except Exception as exc:
            print(
                f"❌ 获取指数行情失败："
                f"{symbol} -> {exc}"
            )

    return {
        "success": True,
        "data": indices,
    }


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
    "/document",
    StaticFiles(
        directory=FRONTEND_DIR / "document",
        html=True,
    ),
    name="document",
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
