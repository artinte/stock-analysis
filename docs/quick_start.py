import sys
from typing import Any

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import requests

# ============================================================
# matplotlib 中文支持
# ============================================================

plt.rcParams["font.sans-serif"] = [
    "SimHei",
    "Microsoft YaHei",
    "Arial Unicode MS",
]

plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 股票代码转换
# ============================================================


def normalize_tencent_symbol(symbol: str) -> str:
    """
    将统一股票代码转换成腾讯接口格式。

    支持：

        600519
        600519.SH

        000001
        000001.SZ

        002250.SZ

    转换：

        600519.SH -> sh600519
        000001.SZ -> sz000001
    """

    symbol = symbol.strip().upper()

    # 已经是腾讯格式
    if symbol.startswith(("SH", "SZ")):
        return symbol.lower()

    # 去掉交易所后缀
    if "." in symbol:

        code, exchange = symbol.split(".", 1)

    else:

        code = symbol

        # 上海
        if code.startswith(
            (
                "600",
                "601",
                "603",
                "605",
                "688",
                "689",
            )
        ):
            exchange = "SH"

        # 深圳
        elif code.startswith(
            (
                "000",
                "001",
                "002",
                "003",
                "300",
                "301",
            )
        ):
            exchange = "SZ"

        else:
            raise ValueError(f"无法判断股票交易所: {symbol}")

    exchange = exchange.upper()

    if exchange == "SH":
        return f"sh{code}"

    if exchange == "SZ":
        return f"sz{code}"

    raise ValueError(f"不支持的交易所: {exchange}")


# ============================================================
# 腾讯 K 线
# ============================================================


def get_tencent_kline(
    symbol: str,
    days: int = 60,
) -> pd.DataFrame:
    """
    从腾讯获取日 K 线。

    腾讯返回格式：

        [
            日期,
            开盘,
            收盘,
            最高,
            最低,
            成交量
        ]

    注意：

    腾讯这里的字段顺序非常重要。

    例如：

        [
            '2026-05-29',
            '1242.576',
            '1297.976',
            '1300.976',
            '1241.976',
            '76478.000'
        ]

    对应：

        日期 = 2026-05-29
        开盘 = 1242.576
        收盘 = 1297.976
        最高 = 1300.976
        最低 = 1241.976

    返回：

        Date
        Open
        High
        Low
        Close
    """

    tencent_symbol = normalize_tencent_symbol(symbol)

    print(f"正在获取腾讯 K 线: " f"{symbol} -> {tencent_symbol}")

    # --------------------------------------------------------
    # 腾讯接口
    # --------------------------------------------------------

    url = "https://web.ifzq.gtimg.cn/" "appstock/app/fqkline/get"

    params = {"param": (f"{tencent_symbol},day,,," f"{days},qfq")}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        )
    }

    # --------------------------------------------------------
    # 请求
    # --------------------------------------------------------

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as exc:

        raise RuntimeError(f"腾讯 K 线请求失败: {symbol}\n" f"{exc}") from exc

    except ValueError as exc:

        raise RuntimeError(f"腾讯返回的数据不是有效 JSON: {symbol}") from exc

    # --------------------------------------------------------
    # 获取股票数据
    # --------------------------------------------------------

    try:

        stock_data = data["data"][tencent_symbol]

    except (
        KeyError,
        TypeError,
    ) as exc:

        raise RuntimeError(
            f"腾讯没有返回 K 线: {symbol}\n"
            f"腾讯代码: {tencent_symbol}\n"
            f"返回数据: {data}"
        ) from exc

    # --------------------------------------------------------
    # 优先使用 qfqday
    # --------------------------------------------------------

    rows = stock_data.get("qfqday")

    if not rows:
        rows = stock_data.get("day")

    if not rows:

        raise RuntimeError(f"腾讯没有返回复权 K 线: {symbol}")

    # --------------------------------------------------------
    # 打印原始数据
    # --------------------------------------------------------

    print()
    print("腾讯原始 K 线示例:")

    if rows:
        print(rows[0])

    # ========================================================
    # 转换
    #
    # 腾讯：
    #
    # [日期, 开盘, 收盘, 最高, 最低, 成交量]
    #
    # Open  = row[1]
    # Close = row[2]
    # High  = row[3]
    # Low   = row[4]
    # ========================================================

    records: list[dict[str, Any]] = []

    for row in rows:

        if not row or len(row) < 5:
            continue

        try:

            records.append(
                {
                    "Date": pd.to_datetime(row[0]),
                    "Open": float(row[1]),
                    "Close": float(row[2]),
                    "High": float(row[3]),
                    "Low": float(row[4]),
                }
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            print(f"跳过异常 K 线: {row}")

            print(f"原因: {exc}")

    if not records:

        raise RuntimeError(f"腾讯 K 线数据为空: {symbol}")

    # --------------------------------------------------------
    # DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(records)

    df.set_index(
        "Date",
        inplace=True,
    )

    df.sort_index(inplace=True)

    # --------------------------------------------------------
    # 最后限制数量
    # --------------------------------------------------------

    if days > 0:

        df = df.tail(days)

    # --------------------------------------------------------
    # 数据检查
    # --------------------------------------------------------

    # 正确检查：
    #
    # 收盘 > 开盘 = 上涨
    # 收盘 < 开盘 = 下跌
    # 收盘 = 开盘 = 平盘

    up_count = (df["Close"] > df["Open"]).sum()

    down_count = (df["Close"] < df["Open"]).sum()

    flat_count = (df["Close"] == df["Open"]).sum()

    print()
    print("K 线数据检查")
    print("-" * 40)

    print(f"数据数量: {len(df)}")

    print(f"上涨: {up_count}")

    print(f"下跌: {down_count}")

    print(f"平盘: {flat_count}")

    print()

    # --------------------------------------------------------
    # 打印前几条验证
    # --------------------------------------------------------

    print("前 5 条 K 线检查:")

    for index, row in df.head(5).iterrows():

        if row["Close"] > row["Open"]:

            direction = "上涨"

        elif row["Close"] < row["Open"]:

            direction = "下跌"

        else:

            direction = "平盘"

        print(
            f"{index.date()} "
            f"O={row['Open']:.2f} "
            f"H={row['High']:.2f} "
            f"L={row['Low']:.2f} "
            f"C={row['Close']:.2f} "
            f"{direction}"
        )

    return df


# ============================================================
# 绘制 K 线
# ============================================================


def plot_kline(
    kline_data: pd.DataFrame,
    stock_code: str = "600519.SH",
) -> None:
    """
    绘制 A 股风格 K 线。

    特点：

        红色 = 上涨
        绿色 = 下跌

    不显示成交量。

    自动增加上下边距，
    防止 K 线贴住图表边缘。
    """

    if kline_data is None or kline_data.empty:
        raise ValueError("K 线数据为空，无法绘图")

    # --------------------------------------------------------
    # 数据完整性检查
    # --------------------------------------------------------

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    for column in required_columns:

        if column not in kline_data.columns:

            raise ValueError(f"K 线缺少字段: {column}")

    # --------------------------------------------------------
    # 强制数值类型
    # --------------------------------------------------------

    data = kline_data.copy()

    for column in required_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data.dropna(
        subset=required_columns,
        inplace=True,
    )

    if data.empty:

        raise ValueError("没有有效的 K 线数据")

    # --------------------------------------------------------
    # 再检查一次 OHLC
    # --------------------------------------------------------

    for index, row in data.iterrows():

        if row["High"] < max(
            row["Open"],
            row["Close"],
        ):

            raise ValueError(f"K 线最高价异常: {index}")

        if row["Low"] > min(
            row["Open"],
            row["Close"],
        ):

            raise ValueError(f"K 线最低价异常: {index}")

    # ========================================================
    # A 股颜色
    #
    # A 股：
    #
    # 上涨 -> 红色
    # 下跌 -> 绿色
    #
    # mplfinance：
    #
    # up   = 收盘 > 开盘
    # down = 收盘 < 开盘
    # ========================================================

    market_colors = mpf.make_marketcolors(
        up="red",
        down="green",
        edge={
            "up": "red",
            "down": "green",
        },
        wick={
            "up": "red",
            "down": "green",
        },
        volume={
            "up": "red",
            "down": "green",
        },
    )

    # --------------------------------------------------------
    # 样式
    # --------------------------------------------------------

    style = mpf.make_mpf_style(
        base_mpf_style="charles",
        marketcolors=market_colors,
        gridaxis="both",
        gridstyle="--",
        y_on_right=False,
        rc={
            "font.sans-serif": [
                "SimHei",
                "Microsoft YaHei",
                "Arial Unicode MS",
            ],
            "axes.unicode_minus": False,
        },
    )

    # ========================================================
    # 计算价格范围
    #
    # 防止：
    #
    # K 线贴住顶部
    # K 线贴住底部
    # 底部被切割
    # ========================================================

    low_price = float(data["Low"].min())

    high_price = float(data["High"].max())

    price_range = high_price - low_price

    # 如果价格范围异常
    if price_range <= 0:

        price_range = max(
            abs(high_price) * 0.05,
            1.0,
        )

    # 上下各增加 6% 空间
    padding = price_range * 0.06

    ylim = (
        low_price - padding,
        high_price + padding,
    )

    # ========================================================
    # 绘制
    # ========================================================

    mpf.plot(
        data,
        type="candle",
        # ----------------------------------------------------
        # 关键：
        # 不显示成交量
        # ----------------------------------------------------
        volume=False,
        title=(f"\n" f"{stock_code} 日K线图"),
        ylabel="价格 (元)",
        style=style,
        figratio=(12, 7),
        figscale=1.1,
        show_nontrading=False,
        datetime_format="%Y-%m-%d",
        xrotation=15,
        # ----------------------------------------------------
        # 给价格上下留空间
        # ----------------------------------------------------
        ylim=ylim,
        tight_layout=True,
    )


# ============================================================
# Main
# ============================================================


def main() -> None:

    print(f"Python 版本: {sys.version}")

    symbol = "600519.SH"

    print()
    print(f"股票: {symbol}")

    # ========================================================
    # 1. 获取腾讯 K 线
    # ========================================================

    data = get_tencent_kline(
        symbol=symbol,
        days=60,
    )

    # ========================================================
    # 2. 打印完整数据
    # ========================================================

    print()
    print("K 线数据:")
    print(data)

    print()

    print(f"共获取 {len(data)} 条 K 线")

    # ========================================================
    # 3. 最终统计
    # ========================================================

    up_count = (data["Close"] > data["Open"]).sum()

    down_count = (data["Close"] < data["Open"]).sum()

    flat_count = (data["Close"] == data["Open"]).sum()

    print()
    print("最终统计")
    print("-" * 40)

    print(f"上涨: {up_count}")

    print(f"下跌: {down_count}")

    print(f"平盘: {flat_count}")

    # ========================================================
    # 4. 绘制
    # ========================================================

    print()
    print("开始绘制 K 线...")

    plot_kline(
        data,
        stock_code=symbol,
    )


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":
    main()
