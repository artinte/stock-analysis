import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_pure_macd(bar_models: list[MACDIndicatorBar], title: str = "纯 MACD 指标图"):
    """
    纯粹的绘图层：只负责接收一组强类型的 Model 数据并渲染 MACD。
    """
    if not bar_models:
        print("数据为空，无法绘制。")
        return

    # 1. 纯原生对象属性提取（不需要 .dict() 或 row[]）
    dates = [bar.timestamp for bar in bar_models]
    dif_values = [bar.dif for bar in bar_models]
    dea_values = [bar.dea for bar in bar_models]
    hist_values = [bar.hist for bar in bar_models]
    code = bar_models[0].code

    # 2. 初始化标准副图画板
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # 3. 绘制两条趋势线 (DIF 蓝线, DEA 黄线)
    ax.plot(dates, dif_values, label="DIF", color="#1F77B4", linewidth=1.5)
    ax.plot(dates, dea_values, label="DEA", color="#FF7F0E", linewidth=1.5)
    
    # 4. 绘制红绿柱状图 (国内习惯：大于等于0为红，小于0为绿)
    hist_colors = ['#FF3232' if h and h >= 0 else '#00E600' for h in hist_values]
    ax.bar(dates, hist_values, width=0.6, color=hist_colors, label="MACD 柱", alpha=0.8)
    
    # 5. 绘制 0 轴分界线
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

    # 6. 图表基本配置
    ax.set_title(f"{code} - {title}", fontsize=12, fontweight='bold')
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")

    # 自动格式化时间轴，防止重叠
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()
