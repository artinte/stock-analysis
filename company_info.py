from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class CompanyInfo:
    """
    股票公司信息类：用于存储和管理一家上市公司的各种关键信息。
    """

    company_name: str = field(metadata={"description": "公司官方全称"})
    ticker: str = field(metadata={"description": "股票代码 (如 AAPL, MSFT)"})
    exchange: Optional[str] = field(
        default=None, metadata={"description": "所属交易所 (如 NASDAQ, NYSE)"}
    )
    country: Optional[str] = field(default=None, metadata={"description": "注册国家"})
    ceo: Optional[str] = field(
        default=None, metadata={"description": "首席执行官 (CEO) 名称"}
    )

    market_cap: Optional[float] = field(
        default=None, metadata={"description": "总市值 (单位: USD)"}
    )
    last_price: Optional[float] = field(
        default=None, metadata={"description": "最新交易价格"}
    )
    currency: Optional[str] = field(default="USD", metadata={"description": "交易货币"})
    volume: Optional[int] = field(default=None, metadata={"description": "最新交易量"})

    sector: Optional[str] = field(
        default=None, metadata={"description": "所属行业大类 (如科技、医疗保健)"}
    )
    industry: Optional[str] = field(
        default=None, metadata={"description": "所属细分行业 (如半导体、云计算)"}
    )
    description: Optional[str] = field(
        default=None, metadata={"description": "公司简介或核心业务概括"}
    )
    mission: Optional[str] = field(
        default=None, metadata={"description": "公司使命宣言"}
    )
    website: Optional[str] = field(
        default=None, metadata={"description": "公司官方网站"}
    )

    pe_ratio: Optional[float] = field(
        default=None, metadata={"description": "市盈率 (P/E Ratio)"}
    )
    ps_ratio: Optional[float] = field(
        default=None, metadata={"description": "市销率 (P/S Ratio)"}
    )
    eps: Optional[float] = field(
        default=None, metadata={"description": "每股收益 (EPS)"}
    )
    dividend_yield: Optional[float] = field(
        default=None, metadata={"description": "股息收益率"}
    )

    employees: Optional[int] = field(default=None, metadata={"description": "员工总数"})

    tags: List[str] = field(
        default_factory=list, metadata={"description": "关键词标签列表"}
    )

    competitors: List[str] = field(
        default_factory=list,
        metadata={"description": "主要竞争对手列表"},
        default_factory=list,
    )

    websites: Dict[str, str] = field(
        default_factory=dict,
        metadata={"description": "相关网址字典 (Key: 介绍, Value: 具体地址)"},
    )

    analysis: List[str] = field(
        default_factory=list,
        metadata={"description": "优劣分析"},
    )

    product_lines: List[str] = field(
        default_factory=list,
        metadata={"description": "主要产品线"},
    )

    opportunities: List[str] = field(
        default_factory=list,
        metadata={"description": "市场潜力"},
    )


AllCompanyInfos = {
    CompanyInfo(
        company_name="Apple Inc.",
        ticker="AAPL",
        exchange="NASDAQ",
        country="USA",
        market_cap=0,
        last_price=0.0,
        sector="Technology",
        industry="Consumer Electronics",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="Designs, manufactures, and markets smartphones (iPhone), personal computers (Mac), wearables, and digital services.",
        tags=["Big Tech", "Consumer", "Growth"],
    ),
    CompanyInfo(
        company_name="Microsoft Corporation",
        ticker="MSFT",
        exchange="NASDAQ",
        country="USA",
        market_cap=0,
        last_price=0.0,
        sector="Technology",
        industry="Software—Infrastructure",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="Develops, licenses, and supports software, services, devices, and solutions worldwide.",
        tags=["Big Tech", "Enterprise", "Cloud"],
    ),
    CompanyInfo(
        company_name="Amazon.com, Inc.",
        ticker="AMZN",
        exchange="NASDAQ",
        country="USA",
        market_cap=0,
        last_price=0.0,
        sector="Consumer Cyclical",
        industry="Internet Retail",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="Engages in the retail sale of consumer products and subscriptions in North America and internationally.",
        tags=["E-commerce", "Cloud", "Logistics"],
    ),
    CompanyInfo(
        company_name="Alphabet Inc.",
        ticker="GOOGL",
        exchange="NASDAQ",
        country="USA",
        market_cap=0,
        last_price=0.0,
        sector="Communication Services",
        industry="Internet Content & Information",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="Provides online advertising services in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America.",
        tags=["Big Tech", "Advertising", "AI"],
    ),
    CompanyInfo(
        company_name="Meta Platforms, Inc.",
        ticker="META",
        exchange="NASDAQ",
        country="USA",
        market_cap=0,
        last_price=0.0,
        sector="Communication Services",
        industry="Internet Content & Information",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="Develops products that enable people to connect and share with friends and family through mobile devices, personal computers, virtual reality headsets, and in-home devices worldwide.",
        tags=["Social Media", "Advertising", "VR/AR"],
    ),
    CompanyInfo(
        company_name="Tesla, Inc.",
        ticker="TSLA",
        exchange="NASDAQ",
        country="USA",
        market_cap=0,
        last_price=0.0,
        sector="Consumer Cyclical",
        industry="Auto Manufacturers",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="Designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally.",
        tags=["Electric Vehicles", "Clean Energy", "Innovation"],
    ),
    CompanyInfo(
        company_name="景嘉微",
        ticker="300474",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="通用处理器/AI芯片",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="专注于高性能嵌入式处理器及其核心IP的研发、设计与销售。",
        tags=["半导体", "芯片设计", "国产化"],
        competitors=["紫光国微", "中科曙光", "兆易创新", "摩尔线程"],
    ),
    CompanyInfo(
        company_name="圣邦股份",
        ticker="300661",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="模拟芯片/信号链",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="专注于模拟集成电路的研发、设计与销售，产品涵盖电源管理、音频放大、触控驱动等领域。",
        tags=["半导体", "模拟芯片", "电源管理"],
        competitors=[
            "汇顶科技",
            "卓胜微",
            "韦尔股份",
            "兆易创新",
            "艾为电子",
            "希荻微",
        ],
    ),
    CompanyInfo(
        company_name="斯达半导",
        ticker="603290",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="功率半导体 (IGBT)",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="专注于功率半导体器件的研发、制造与销售，产品广泛应用于消费电子、电源管理、新能源等领域。",
        tags=["半导体", "功率器件", "新能源"],
        competitors=["士兰微", "华润微", "扬杰科技", "三安光电", "时代电气"],
    ),
    CompanyInfo(
        company_name="亨通光电",
        ticker="600487",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        currency="CNY",
        sector="信息技术",
        industry="光纤光缆",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="公司持续通信和能源两大核心产业的战略投入，提供行业领先的光通信、智能电网、海洋能源、海洋通信、工业与新能源等产品与解决方案，目前已发展成为全球领先的信息与能源互联解决方案服务商，是深海科技的典型代表。",
        tags=[
            "5G光纤通信",
            "海洋通信",
            "量子保密通信",
            "光模块",
            "海洋超高压输电",
            "海上风电工程与运营",
        ],
        competitors=["中天科技", "烽火通信", "长飞光纤"],
        websites={
            "定期报告": "https://www.htgd.com.cn/tzzgx/dqbg.html",
        },
        analysis=[
            "优点：拥有通信和能源两大领域",
            "优点：营收稳步增长",
            "缺点：利润率有待提升，比传统制造业还要低",
            "优点：量子领域有布局",
            "缺点：光模块业务有点验证",
        ],
        opportunities=[
            "空心光纤商业化提速：依托空芯反谐振光纤的技术突破，具备规模化商用能力，抢占超低时延数据传输和算力网络的先发市场。",
            "量子通信产业化落地：具备自主建设量子通信干线网络和提供量子保密通信解决方案的能力，推动量子金融专线等项目的产业化应用。",
        ],
    ),
    CompanyInfo(
        company_name="豪威集团",
        ticker="603501",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="图像传感器",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="主要从事芯片设计业务的 Fabless 芯片设计公司，公司半导体设计销售业务主要由图像传感器解决方案、显示解决方案和模拟解决方案三大业务体系构成。",
        tags=["半导体", "图像传感器", "摄像头"],
        competitors=["索尼", "三星电子", "安森美", "格科微", "思特威"],
        websites={
            "定期报告": "hhttps://www.omnivision-group.com/financial-reports",
        },
        analysis=[
            "优点：全球领先的图像传感器设计和供应商",
            "优点：专注于高性能CMOS图像传感器的研发与制造",
            "缺点：面临激烈的市场竞争",
            "优点：技术创新能力强",
            "缺点：对单一市场依赖较大",
        ],
        product_lines=[
            "图像传感器解决方案",
            "显示解决方案",
            "模拟解决方案",
        ],
        opportunities=[
            "汽车视觉传感器爆发：深度受益于新能源和自动驾驶普及，车用 CIS 渗透率和单车用量激增，抢占 ADAS 和智能座舱市场份额。",
            "AIoT 边缘视觉升级：推动 CIS 在智能安防、工业机器视觉、AR/VR 等边缘 AI 领域的应用，满足终端设备对实时感知和本地推理的要求。",
            "高端 CIS 技术升级：加速向高像素、大靶面、高动态范围 (HDR) 等高端领域拓展，尤其是在旗舰智能手机和医疗成像市场实现突破性增长。",
        ],
    ),
    CompanyInfo(
        company_name="瑞芯微",
        ticker="603893",
        exchange="SSE",
        country="China",
        ceo="名字-励民；出生时间-1965年；毕业院校-浙江大学；学历-经济学硕士；职位-董事长兼总经理",
        market_cap=0,
        last_price=0.0,
        sector="集成电路设计",
        industry="计算机、通信和其他电子设备制造业",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="专注于集成电路设计与研发，目前已发展为领先的物联网（IoT）及人工智能物联网（AIoT）处理器芯片企业。",
        tags=["半导体", "芯片设计", "物联网", "AIoT"],
        competitors=[
            "全志科技",
            "晶晨股份",
            "北京君正",
            "华为海思",
            "紫光展锐",
            "富瀚微",
            "星宸科技",
            "恒玄科技",
            "联发科",
            "高通",
            "英特尔",
            "恩智浦半导体",
            "英伟达",
        ],
        websites={
            "定期报告": "https://www.rock-chips.com/a/cn/tzzgx/news/cwbg/index.html",
            "新闻中心": "https://www.rock-chips.com/a/cn/news/rockchip/index.html",
        },
        analysis=[
            "优点：专注于集成电路设计与研发",
            "优点：领先的物联网（IoT）及人工智能物联网（AIoT）处理器芯片企业",
            "缺点：只做芯片，没有直接面向消费者的产品",
            "缺点：总部位于福州，虽然有利于降低部分运营成本，但可能在高端人才引进和产业生态合作方面不如北上广深杭等高科技中心城市具有优势",
            "优点：具备自研或集成的 NPU（神经网络处理器），用于提供终端 AI 算力",
            "缺点：容易受到市场波动影响，特别是在消费电子和智能设备领域，比如存储涨价会增加整体成本压力",
        ],
        product_lines=[
            "RK3588 (旗舰高性能：边缘计算、智能座舱、VR)",
            "RK3399 (中高端通用：工控、商显、教育)",
            "RV系列 (视觉处理：智能安防IPC、人脸识别)",
            "RK3568/3566 (通用型：平板、工控、商显)",
        ],
        opportunities=[
            "端侧 AI 算力爆发：受益于 AI PC、AI 手机、AIoT 边缘设备对 NPU 算力需求的激增，公司凭借全系列 NPU 芯片，快速抢占端侧/边缘侧 AI 芯片市场份额。"
        ],
    ),
    CompanyInfo(
        company_name="士兰微",
        ticker="600460",
        exchange="SSE",
        country="China",
        ceo="名字-陈向东；出生时间-1963年；毕业院校-浙江大学；学历-大学本科；职位-董事长兼总经理",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="半导体制造",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="主要从事半导体器件的研发、制造与销售，产品涵盖功率半导体、模拟集成电路、分立器件等领域。",
        mission="士兰微电子将结合自身8吋、12吋及化合物半导体生产线的扩产和建设，以国际先进的IDM大厂为学习标杆，不断提升产品开发能力和生产规模，努力成为具有自主品牌和国际一流竞争力的综合型的半导体产品供应商。",
        tags=["集成电路", "功率半导体和分立器件", "发光二极管"],
        competitors=[
            "华润微",
            "扬杰科技",
            "三安光电",
            "时代电气",
            "斯达半导",
            "英飞凌",
        ],
        websites={
            "关于士兰": "https://www.silan.com.cn/about.html",
        },
        analysis=[
            "优点：国内领先的半导体制造企业",
            "优点：产品涵盖功率半导体、模拟集成电路、分立器件等领域",
            "缺点：面临激烈的市场竞争，特使是华润微这家公司，业务高度相同",
            "缺点：自身技术需要有更大的突破，占领高端市场",
            "缺点：对单一市场依赖较大，主要客户在国内，国际市场开拓不足",
            "缺点：IDM重资产模式，生产元器件不好挣钱，受上游和下游影响波动大",
        ],
        product_lines=[
            "集成电路",
            "分立器件产品",
            "发光二极管产品",
            "其它",
        ],
        opportunities=[
            "士兰集宏 8 英寸 SiC：2026 年实现 10 亿级别总利润。按约 50% 的持股比例计算，预计贡献归母净利润约 5 亿元，是公司利润弹性的核心。",
            "12 英寸集科项目：2026 年达产。虽持股比例较低（约 18%），但作为 IDM 核心制造平台，通过关联交易和产能保障，间接提升母公司设计端的毛利，预计直接贡献归母净利润 1.5-2 亿元。",
            "母公司设计与分立器件：聚焦高边驱动等模拟 IC 国产替代。这部分属于 100% 归母利润，毛利高达 30% 以上，预计贡献归母净利润 8-10 亿元，是 20 亿目标的『压舱石』。",
            "成都封装二期：作为 100% 控股子公司，通过承接集宏和集科的模块封装需求，将产业链增值利润全部留在归母净利润中，预计贡献 2 亿元。",
            "总结：2026年目标 180 亿营收，20 亿归母净利润。",
        ],
    ),
    CompanyInfo(
        company_name="立昂微",
        ticker="605358",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="功率半导体",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="专注于功率半导体器件的研发、制造与销售，产品广泛应用于消费电子、电源管理、新能源等领域。",
        tags=["半导体", "功率器件", "新能源"],
        competitors=["士兰微", "华润微", "扬杰科技", "三安光电", "时代电气"],
        websites={},
        analysis=[
            "优点：专注于功率半导体器件的研发、制造与销售",
            "优点：产品广泛应用于消费电子、电源管理、新能源等领域",
            "缺点：面临激烈的市场竞争",
            "优点：技术创新能力强",
            "缺点：对单一市场依赖较大",
        ],
        product_lines=[
            "功率半导体器件",
            "模拟集成电路",
            "分立器件",
        ],
    ),
    CompanyInfo(
        company_name="比亚迪",
        ticker="002594",
        exchange="SZSE",
        country="China",
        ceo="名字-王传福；出生时间-1966年；毕业院校-中南大学；学历-硕士研究生；职位-董事长兼总裁",
        market_cap=0,
        last_price=0.0,
        sector="汽车制造业",
        industry="新能源汽车及轨道交通设备制造业",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="全球领先的新能源汽车制造商，业务涵盖汽车、轨道交通、新能源和电子四大产业，形成了完整的电动汽车和动力电池产业链。",
        tags=["新能源汽车", "电动车", "动力电池", "储能", "半导体（IGBT/SiC）"],
        competitors=[
            "特斯拉 (Tesla)",
            "大众汽车 (Volkswagen)",
            "通用汽车 (GM)",
            "吉利汽车",
            "长城汽车",
            "宁德时代 (CATL)",
        ],
        websites={},
        analysis=[
            "优点：垂直整合能力强，掌握电池、电机、电控等核心技术（三电系统）",
            "优点：动力电池（弗迪电池）和功率半导体（IGBT/SiC）实现自供，成本控制力强",
            "优点：新能源汽车销量位居全球前列，品牌影响力持续扩大",
            "缺点：相较于互联网科技公司，智能化软件方面的技术积累仍需加强",
            "缺点：海外市场扩张初期面临更高的建厂和渠道成本压力",
            "优点：多品牌战略（比亚迪、腾势、仰望、方程豹）覆盖不同消费层级",
        ],
        product_lines=[
            "王朝系列/海洋系列 (大众化乘用车)",
            "腾势/仰望/方程豹 (高端及豪华乘用车)",
            "弗迪电池 (刀片电池、储能电池)",
            "商用车 (大巴、卡车)",
            "轨道交通 (云轨、云巴)",
        ],
        opportunities=[
            "海外市场爆发式增长：利用刀片电池和电动车成本优势，加速海外产能布局和销售网络建设，抢占全球电动化转型市场份额。",
            "高端品牌利润率提升：仰望、方程豹等高端品牌矩阵逐步放量，改善产品结构，带动公司整体毛利率和盈利能力大幅提升。",
            "智能化技术深度整合：DiLink 智能网联系统升级和高阶辅助驾驶技术快速导入，提升用户体验和产品竞争力，缩小与新势力在智能化方面的差距。",
        ],
    ),
    CompanyInfo(
        company_name="北方华创",
        ticker="002371",
        exchange="SZSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="半导体设备制造",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="主要从事半导体制造设备及相关产品的研发、制造与销售，产品涵盖刻蚀设备、薄膜沉积设备、清洗设备等 领域。",
        tags=["半导体设备", "刻蚀设备", "薄膜沉积设备"],
        competitors=["中微公司", "华海清科", "上海微电子装备"],
        websites={},
        analysis=[
            "优点：国内领先的半导体设备制造企业",
            "优点：产品涵盖刻蚀设备、薄膜沉积设备、清洗设备等领域",
            "缺点：面临激烈的市场竞争",
            "优点：技术创新能力强",
            "缺点：对单一市场依赖较大",
        ],
        product_lines=[
            "电子工艺装备：包括半导体装备、真空及新能源装备",
            "电子元器件：包括电阻、电容、晶体器件、模块电源、微波组件等。",
        ],
    ),
    CompanyInfo(
        company_name="广合科技",
        ticker="001389",
        exchange="SZSE",
        country="China",
        ceo="名字-肖红星；出生时间-1967年；毕业院校-华南理工大学；学历-本科学历；职位-董事长",
        market_cap=0,
        last_price=0.0,
        sector="电子元器件及电子专用材料制造",
        industry="印制电路板（PCB）",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="致力于以高速、高频为主的高端PCB制造，产品主要应用于数据中心、云计算、工业互联网、人工智能、5G通讯、汽车电子、安防和打印等终端领域。",
        tags=["PCB", "印制电路板", "高速PCB", "高频PCB", "数据中心", "AI"],
        competitors=[
            "鹏鼎控股",
            "深南电路",
            "景旺电子",
            "东山精密",
            "胜宏科技",
            "沪电股份",
        ],
        websites={},
        analysis=[
            "优点：专注于高速、高频的高端PCB制造",
            "优点：产品应用领域广泛，涵盖数据中心、AI、5G等高增长领域",
            "缺点：PCB行业竞争激烈",
            "优点：受益于AI发展浪潮对PCB需求的提升",
        ],
        product_lines=[
            "多高层印制电路板（主要为高速、高频PCB）",
        ],
    ),
    CompanyInfo(
        company_name="光迅科技",
        ticker="002281",
        exchange="SZSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="通信设备/光通信器件及模块",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="公司主营业务为光通信器件、模块和子系统的研发、生产、销售及技术服务。作为国内光器件领域的龙头企业，光迅科技是业内少数具备光芯片、器件、模块、子系统全产业链垂直整合能力的公司。",
        tags=["光通信", "光模块", "光器件", "光芯片", "AI算力", "5G通信"],
        competitors=["中际旭创", "新易盛", "天孚通信", "华工科技"],
        websites={},
        analysis=[
            "优点：产业链垂直整合能力强，覆盖芯片-器件-模块-子系统全链条。",
            "优点：具备PLC、DFB、EML等光芯片的自主研发能力，技术壁垒较高。",
            "优点：受益于全球数据中心、AI算力爆发和5G/F5G发展，高端光模块需求增长。",
            "缺点：相比纯光模块厂商，垂直整合模式前期投入大，研发成本较高。",
            "优点：在电信传输网领域占据优势地位，客户资源稳定。",
        ],
        product_lines=[
            "光电子器件：包括有源光器件和无源光器件。",
            "光通信模块：包括高速率光模块（如800G、400G、200G）、接入网光模块等。",
            "光子集成芯片：包括半导体激光器芯片、探测器芯片等。",
            "子系统产品：应用于传输、接入和数据通信等领域。",
        ],
    ),
    CompanyInfo(
        company_name="剑桥科技",
        ticker="603083",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="信息技术",
        industry="通信设备/光模块及网络设备",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="公司主营业务包括两部分：高速光模块、电信宽带及企业网络设备。光模块产品是主要增长点，涵盖100G、400G、800G等系列，主要应用于数据中心和电信网络。公司在北美和欧洲市场具有较高的知名度和竞争力。",
        tags=["光模块", "800G", "数据中心", "AI算力", "网络设备", "海外市场"],
        competitors=["中际旭创", "新易盛", "华工科技", "光迅科技"],
        websites={},
        analysis=[
            "优点：光模块业务受益于AI/算力对高速率产品的需求，营收规模和增速快。",
            "优点：高端光模块（400G/800G）产品批量出货，技术能力得到市场认可。",
            "优点：深耕海外市场，与国际头部客户建立了稳定的合作关系。",
            "缺点：核心光芯片仍主要依赖外购，产业链整合度不如部分竞争对手。",
            "缺点：传统网络设备业务增长面临压力。",
        ],
        product_lines=[
            "高速光模块：主要应用于数据中心和电信网络，如400G/800G。",
            "网络设备：包括电信宽带接入终端、企业级路由器和交换机等。",
        ],
    ),
    CompanyInfo(
        company_name="胜宏科技",
        ticker="300476",
        exchange="SZSE",
        country="China",
        market_cap=0,
        last_price=0.0,
        sector="电子",
        industry="印制电路板 (PCB)",
        pe_ratio=0.0,
        dividend_yield=0.0,
        description="公司是全球领先的印制电路板（PCB）制造企业，主营高密度印制线路板的研发、生产和销售。产品涵盖多层板、HDI、柔性电路板（FPC）及刚挠结合板。公司在AI服务器、新能源汽车及算力中心领域拥有极强的市场份额，是英伟达（NVIDIA）等国际算力巨头的重要供应商。",
        tags=["PCB", "AI服务器", "HDI", "新能源汽车", "英伟达概念", "算力基础设施"],
        competitors=["沪电股份", "深南电路", "景旺电子", "鹏鼎控股", "广合科技"],
        websites={},
        analysis=[
            "优点：深度绑定AI算力龙头（如英伟达），是其AI服务器PCB的核心供应商，受益于算力需求爆发。",
            "优点：HDI技术实力雄厚，具备高阶HDI及超高层板的量产能力，产品结构向高端化转型效果显著。",
            "优点：海外布局领先，通过收购MFS（维信电子）完善了FPC全球布局及汽车电子市场份额。",
            "缺点：受大宗商品（如铜箔）价格波动影响大，原材料成本压力对毛利率有一定挑战。",
            "缺点：PCB行业整体竞争激烈，中低端产品线面临价格战风险。",
        ],
        product_lines=[
            "常规多层板：广泛应用于通信、消费电子及工控领域。",
            "HDI板：高密度互连技术，主要用于AI服务器、高端智能手机及智能穿戴。",
            "汽车板：专注于新能源汽车三电系统、自动驾驶域控制器等。",
            "柔性及刚挠结合板：通过MFS子公司提供，主要服务于医疗及高端工业领域。",
        ],
    ),
    CompanyInfo(
        company_name="雅克科技",
        ticker="002409",
        exchange="SZSE",
        country="China",
        market_cap=0,
        last_price=0,
        sector="电子",
        industry="半导体材料 / 前驱体",
        pe_ratio=0,
        dividend_yield=0.8,
        description="公司是国内半导体材料平台型领军企业，通过并购韩国UP Chemical切入前驱体赛道，是全球领先的前驱体供应商。主营业务涵盖半导体前驱体、电子特气、光刻胶及其配套试剂、LNG保温复合材料等。公司深度绑定SK海力士、三星、长江存储等全球存储巨头，是HBM（高带宽内存）产业链中的核心材料供应商。",
        tags=[
            "前驱体",
            "HBM概念",
            "SK海力士供应商",
            "电子特气",
            "光刻胶",
            "LNG保温材料",
        ],
        competitors=[
            "南大光电",
            "华特气体",
            "万华化学",
            "安集科技",
            "默克KGaA",
            "法液空",
        ],
        websites={},
        analysis=[
            "优点：全球前驱体领军企业，技术壁垒极高，尤其在先进制程及3D NAND堆叠所需的High-K材料上具备强竞争力。",
            "优点：深度受益于HBM（高带宽内存）需求爆发，由于HBM需要更多层的堆叠和更复杂的清洗/薄膜工艺，前驱体用量翻倍增长。",
            "优点：业务布局呈现多元化‘平台型’特征，除了半导体材料，在LNG船用保温材料领域也拥有极高的市场占有率。",
            "缺点：由于大量业务来自海外（韩国等），受汇率波动和国际贸易政策影响较大。",
            "缺点：前期并购较多，账面商誉较高，需关注商誉减值及后续整合风险。",
        ],
        product_lines=[
            "半导体前驱体：用于CVD/ALD工艺的核心化学原料，包括高K材料、金属前驱体等。",
            "电子特气：主要产品为六氟化硫和四氟化碳，应用于电力及半导体刻蚀。",
            "光刻胶及配套：包括彩色光刻胶及TMAH等显影液，主要服务于显示面板行业。",
            "LNG保温复合材料：用于液化天然气（LNG）运输船的货舱围护系统，打破国外垄断。",
        ],
    ),
    CompanyInfo(
        company_name="紫金矿业",
        ticker="601899",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0,  # 示例价格
        sector="有色金属",
        industry="黄金/铜/锂/锌",
        pe_ratio=0,
        dividend_yield=0,
        description="公司是中国矿业行业的全球化领军企业，以黄金和铜、锌等基本金属矿产资源勘查和开发为主，并正积极向锂等新能源矿种拓展。公司拥有极强的成本控制能力和跨国并购整合能力，海外资产占比、产量占比及利润占比均接近或超过50%，是中国企业‘走出去’在资源领域最成功的案例之一。",
        tags=[
            "全球矿业巨头",
            "铜价波动受益",
            "金价避险属性",
            "锂矿新势力",
            "海外并购标杆",
            "一带一路",
        ],
        competitors=[
            "Freeport-McMoRan (FCX)",
            "BHP Group (必和必拓)",
            "Rio Tinto (力拓)",
            "山东黄金",
            "江西铜业",
            "洛阳钼业",
        ],
        websites={},
        analysis=[
            "优点：资源储备雄厚且持续增长。通过精准的逆周期收购，拥有卡莫阿铜矿、波格拉金矿等世界级优质资产，铜储备量居全球领先地位。",
            "优点：极高的开发效率与成本优势。具备从地质勘探到冶炼加工的全产业链技术优势，能在低矿石品位下维持较高的毛利率。",
            "优点：多元化布局对冲风险。‘铜+金’的双主业组合既能享受经济上行时的工业金属需求红利，又能利用黄金的避险属性抵御宏观经济不确定性。",
            "缺点：地缘政治风险。海外资产比例高，涉及刚果（金）、哥伦比亚、塞尔维亚等地区，受当地政治稳定性、法律变动及税收政策影响较大。",
            "缺点：受大宗商品价格波动直接影响。业绩高度依赖伦敦金属交易所（LME）和伦敦金的定价，具有显著的周期性特征。",
        ],
        product_lines=[
            "矿产铜：公司增长核心。卡莫阿等超大型铜矿持续扩产，受益于全球电力系统升级及电动汽车需求。",
            "矿产金：传统优势业务。金价高位运行时提供强劲的经营现金流和利润保障。",
            "矿产锌/铅：成熟业务。在国内外拥有多个大型矿山，规模效应显著。",
            "新能源材料（锂矿）：新增长极。通过收购拉古纳北、3Q锂盐湖等项目，快速切入碳酸锂生产，打造第三增长曲线。",
        ],
    ),
    CompanyInfo(
        company_name="安图生物",
        ticker="603658",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0,
        sector="医药生物",
        industry="体外诊断 (IVD)",
        pe_ratio=0,
        dividend_yield=0,
        description="安图生物是国内体外诊断（IVD）行业的领先企业，专注于免疫诊断、微生物诊断、生化诊断及分子诊断产品的研发、生产与销售。公司在化学发光领域拥有极强的市场地位，是中国第一家推出全自动磁微粒化学发光免疫分析仪的企业，目前正通过‘流水线’战略深耕大型实验室市场，并积极向基因测序、质谱等高端检测领域转型。",
        tags=[
            "化学发光龙头",
            "流水线战略",
            "进口替代标兵",
            "高分红价值股",
            "集采出清预期",
            "医疗设备国产化",
        ],
        competitors=[
            "迈瑞医疗 (300760)",
            "新产业 (300832)",
            "迈克生物 (300463)",
            "万泰生物",
            "罗氏 (Roche)",
            "雅培 (Abbott)",
        ],
        websites={
            "公司公告": "https://www.autobio.com.cn/Client/index/fid/22/cid/466/lid/81/.html",
            "逐梦体外诊断“皇冠上的明珠”": "https://caivd-org.cn/article.asp?id=18395",
        },
        analysis=[
            "优点：全产业链布局与技术沉淀。拥有国内领先的化学发光与微生物诊断技术，能够提供从仪器、试剂到实验室自动化流水线的完整解决方案。",
            "优点：研发驱动与创新储备。在质谱、NGS、流水线等高端领域持续投入，产品线丰富度在国内IVD企业中名列前茅，具备长期竞争力。",
            "优点：良好的现金流与分红习惯。公司经营稳健，利润质量高，在估值低位时展现出较高的股息收益吸引力。",
            "缺点：集采降价压力。体外诊断试剂进入带量采购常态化，导致核心产品毛利率受损，业绩增长动能短期面临调整。",
            "缺点：DRG/DIP支付改革。医保控费导致医院端检测需求趋于精细化，影响了过去依赖检测量高增长的营收逻辑。",
            "缺点：海外市场尚在起步期。相比迈瑞等对手，安图的海外收入占比仍有提升空间，在全球化竞争中面临跨国巨头的直接挤压。",
        ],
        product_lines=[
            "磁微粒化学发光：核心利润源。覆盖肿瘤标志物、传染病、激素等检测，通过大型仪器的装机带动高毛利试剂消耗。",
            "微生物检测：传统优势业务。在细菌鉴定、药敏分析等细分领域保持国内市场领先份额。",
            "实验室自动化（Autolas）：增长驱动力。通过流水线系统绑定大型三甲医院客户，提升用户粘性与综合检测份额。",
            "生化/分子/质谱：新兴业务。积极布局基因测序与质谱检测，寻找‘第二增长曲线’，承接高端科研与精准医疗需求。",
        ],
    ),
    CompanyInfo(
        company_name="梅花生物",
        ticker="600873",
        exchange="SSE",
        country="China",
        market_cap=0,
        last_price=0,
        sector="基础化工",
        industry="农产品加工 / 生物发酵",
        pe_ratio=0,
        dividend_yield=0,
        description="梅花生物是全球领先的氨基酸生产企业，构建了从玉米深加工到生物发酵再到精细化工的完整产业链。公司在味精、赖氨酸、苏氨酸等大宗氨基酸领域拥有极高的市场占有率和成本控制能力。近年来，公司通过收购日本协和发酵等举措，积极向医药级氨基酸、人类营养等高附加值领域转型，并持续通过高分红和注销式回购回馈股东。",
        tags=[
            "全球氨基酸龙头",
            "极致成本控制",
            "高股息现金牛",
            "合成生物学应用",
            "注销式回购标兵",
            "出海战略升级",
        ],
        competitors=[
            "阜丰集团 (00546.HK)",
            "伊品生物 (星湖科技 600866)",
            "安迪苏 (600299)",
            "中化国际 (600500)",
            "味之素 (Ajinomoto)",
        ],
        websites={},
        analysis=[
            "优点：极致的成本护壳。通过园区一体化生产和热电联产，实现了远低于行业平均的生产成本，在大宗商品价格波动中具备极强的盈利韧性。",
            "优点：资本回报意识极强。长期维持高比例现金分红，并频繁开展注销式回购，直接提升了每股收益（EPS）和股东权益。",
            "优点：产品矩阵升级。成功切入高端医药氨基酸和HMO（人乳寡糖）等领域，正在从单纯的规模驱动转向‘技术+规模’双驱动。",
            "缺点：强周期性风险。毛利受上游原料（玉米、煤炭）价格和下游生猪养殖行业景气度双重影响，利润波动具有明显的周期性特征。",
            "缺点：估值修复缓慢。市场常将其视为传统化工股，导致PE估值长期在10倍以下低位徘徊，缺乏高增长科技股的溢价能力。",
            "缺点：环保与能耗限制。生物发酵属于高耗能、高排放行业，随着碳中和政策收紧，未来新增产能的审批和现有产能的运行成本可能面临压力。",
        ],
        product_lines=[
            "动物营养氨基酸：核心业绩支柱。包含赖氨酸、苏氨酸及缬氨酸，主要用于饲料添加，深度绑定生猪养殖周期。",
            "食品味觉性状优化：现金流业务。主要产品为味精（谷氨酸钠）及I+G，通过品牌和渠道优势维持稳定的市场份额与利润。",
            "人类营养与医药：高毛利增长点。提供医药级氨基酸、支链氨基酸（BCAA）等，收购协和发酵后技术水平跃升至世界前列。",
            "大宗副产品：资源循环利用。包括玉米胚芽、玉米蛋白粉等副产品，充分挖掘每一粒玉米的经济价值，实现‘吃干抹净’。",
        ],
    ),
}
