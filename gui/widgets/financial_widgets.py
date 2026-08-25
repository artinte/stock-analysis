import io
import matplotlib
# matplotlib.use('Agg') # 如果您的程序部署在无显示器的服务器上，请取消此行注释
import matplotlib.pyplot as plt

def generate_financial_chart(years, financial_data, view_type="manager"):
    """
    财务核心看板组件 - 动态切换视角（纯内存操作，不保存文件）
    
    参数:
    :param years: list, 财报周期列表，例如 ['2024', '2025', '2026']
    :param financial_data: dict, 外部程序传进来的完整财务数据集，必须包含图表所需的 key
                           例如: {
                               '营业总收入': , 
                               '归母净利润': ,
                               '毛利率': [0.25, 0.28, 0.30],
                               '每股收益': [1.2, 1.5, 1.8]
                           }
    :param view_type: str, 手动切换视角的参数:
                      - 'manager': 核心高管视角 (营业总收入 + 归母净利润)
                      - 'investor': 外部投资者视角 (归母净利润 + 每股收益EPS)
                      - 'operations': 内部运营视角 (营业总收入 + 毛利率)
    :return: bytes, 渲染好的 PNG 图片二进制字节流
    """
    
    # 1. 初始化环境与中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  
    plt.rcParams['axes.unicode_minus'] = False    
    
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=100)
    ax2 = ax1.twinx()  # 默认启用双轴
    
    # 定义标准配色方案
    COLOR_BLUE = '#1f77b4'
    COLOR_ORANGE = '#ff7f0e'
    COLOR_GREEN = '#2ca02c'
    
    # 2. 根据传入的 view_type 参数，手动切换不同的业务逻辑
    view_type = view_type.lower()
    
    if view_type == "manager":
        # 📌 经理视角：关注规模与最终盈利
        title_text = "公司核心财务指标趋势看板 (Manager View)"
        
        # 左轴：营业总收入（柱状图）
        ax1.set_ylabel('营业总收入 (万元)', color=COLOR_BLUE, fontsize=12)
        bars = ax1.bar(years, financial_data['营业总收入'], color=COLOR_BLUE, alpha=0.6, width=0.4, label='营业总收入')
        ax1.tick_params(axis='y', labelcolor=COLOR_BLUE)
        
        # 右轴：归母净利润（折线图）
        ax2.set_ylabel('归母净利润 (万元)', color=COLOR_ORANGE, fontsize=12)
        lines = ax2.plot(years, financial_data['归母净利润'], color=COLOR_ORANGE, marker='o', linewidth=2.5, label='归母净利润')
        ax2.tick_params(axis='y', labelcolor=COLOR_ORANGE)
        
        # 自动加柱状图标签
        for bar in bars:
            h = bar.get_height()
            ax1.annotate(f'{h}', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
        # 自动加折线图标签
        for x, y in zip(years, financial_data['归母净利润']):
            ax2.annotate(f'{y}', xy=(x, y), xytext=(0, 10), textcoords="offset points", ha='center', va='bottom', color='#d62728', fontweight='bold')

    elif view_type == "investor":
        # 📌 投资者视角：关注资本回报与每股价值
        title_text = "股东与投资者回报看板 (Investor View)"
        
        # 左轴：归母净利润（柱状图换个颜色）
        ax1.set_ylabel('归母净利润 (万元)', color=COLOR_BLUE, fontsize=12)
        bars = ax1.bar(years, financial_data['归母净利润'], color=COLOR_BLUE, alpha=0.5, width=0.4, label='归母净利润')
        ax1.tick_params(axis='y', labelcolor=COLOR_BLUE)
        
        # 右轴：每股收益 EPS（折线图）
        ax2.set_ylabel('每股收益 EPS (元)', color=COLOR_GREEN, fontsize=12)
        lines = ax2.plot(years, financial_data['每股收益'], color=COLOR_GREEN, marker='s', linewidth=2.5, label='每股收益(EPS)')
        ax2.tick_params(axis='y', labelcolor=COLOR_GREEN)
        
        # 标签标注
        for x, y in zip(years, financial_data['每股收益']):
            ax2.annotate(f'{y}元', xy=(x, y), xytext=(0, 10), textcoords="offset points", ha='center', va='bottom', fontweight='bold')

    elif view_type == "operations":
        # 📌 运营视角：关注营收效率与盈利质量
        title_text = "业务线经营效率看板 (Operations View)"
        
        # 💥 特殊处理：运营更习惯百分比对齐，将右轴格式化为百分比
        import matplotlib.ticker as mtick
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        
        # 左轴：营业总收入
        ax1.set_ylabel('营业总收入 (万元)', color=COLOR_BLUE, fontsize=12)
        bars = ax1.bar(years, financial_data['营业总收入'], color=COLOR_BLUE, alpha=0.6, width=0.4, label='营业总收入')
        ax1.tick_params(axis='y', labelcolor=COLOR_BLUE)
        
        # 右轴：毛利率
        ax2.set_ylabel('整体毛利率 (%)', color=COLOR_ORANGE, fontsize=12)
        lines = ax2.plot(years, financial_data['毛利率'], color=COLOR_ORANGE, marker='^', linewidth=2.5, label='毛利率')
        ax2.tick_params(axis='y', labelcolor=COLOR_ORANGE)
        
        # 标签标注毛利率百分比
        for x, y in zip(years, financial_data['毛利率']):
            ax2.annotate(f'{y*100:.1f}%', xy=(x, y), xytext=(0, 10), textcoords="offset points", ha='center', va='bottom', fontweight='bold')
            
    else:
        raise ValueError(f"未知的视角类型: '{view_type}'。请选择 'manager', 'investor' 或 'operations'。")

    # 3. 公共样式美化
    ax1.set_xlabel('财报周期', fontsize=12, labelpad=10)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
    plt.title(title_text, fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()

    # 4. ⚙️ 核心：渲染至内存，不存盘
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
    img_buf.seek(0)
    img_bytes = img_buf.getvalue()
    
    # 5. 清理内存关闭画布
    img_buf.close()
    plt.close(fig)
    
    return img_bytes
