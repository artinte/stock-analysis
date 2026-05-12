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
    CompanyInfo(
        company_name="金诚信",
        ticker="603979",
        exchange="SSE",
        country="China",
        market_cap=284.50,  # 约280-300亿人民币规模，视市场波动而定
        last_price=45.80,  # 示意价格
        sector="有色金属 / 建筑工程",
        industry="矿山开发服务 / 铜磷矿采选",
        pe_ratio=21.5,  # 动态估值水平
        dividend_yield=1.2,  # 处于业务扩张期，分红率中规中矩
        description="金诚信是国内领先的深部矿山开发服务商，业务涵盖矿山建设、采矿运营及矿山装备制造。公司近年完成从“打工人”到“家里有矿”的华丽转型，通过海外并购（如赞比亚Lubambe铜矿、刚果金Dikulushi铜矿等）切入上游资源领域，形成了‘服务+资源’的双轮驱动模式。其超深井建设技术在行业内具有极高门槛，是矿业出海战略的排头兵。",
        tags=[
            "全球矿服领先者",
            "深部工程专家",
            "家里真的有矿",
            "一带一路标兵",
            "铜价上涨受益者",
            "矿业硬科技",
        ],
        competitors=[
            "宏大爆破 (002683)",
            "中色股份 (000758)",
            "紫金矿业 (601899)",
            "北方股份 (600262)",
            "Redpath (加拿大)",
            "Byrnecut (澳大利亚)",
        ],
        websites={"official": "http://www.jchxmc.com"},
        analysis=[
            "优点：独特的商业模式。矿山服务业务（Mine Service）提供稳健的现金流和技术支撑，而自有矿山（Resources）提供极大的业绩弹性，风险对冲能力强。",
            "优点：极高的技术壁垒。公司在1000米及以上的超深井建设领域拥有核心竞争力，随着浅层矿枯竭，全球深部开采需求激增，公司护城河极深。",
            "优点：海外布局先发优势。公司深耕非洲多年，拥有强大的海外管理团队和成熟的跨境运营经验，能够以较低成本获取并改造海外矿山。",
            "缺点：地缘政治风险。核心资产多位于赞比亚、刚果（金）等非洲地区，面临当地政策变动、汇率波动及安全环境不确定性的挑战。",
            "缺点：资本开支压力大。自有矿山的改扩建需要投入巨额资金，在项目投产达产前，资产负债率和现金流会面临一定阶段性压力。",
            "缺点：资源价格波动。随着自有矿产产量的占比提升，公司利润受铜、磷等大宗商品价格波动的影响显著增大，不再是纯粹的低风险服务商。",
        ],
        product_lines=[
            "矿山开发服务：核心基本盘。包括矿山基建（井巷工程）和采矿运营管理，服务对象涵盖紫金、金川、韦丹塔等全球巨头。",
            "自有矿产销售：核心增长极。重点包括刚果(金)Dikulushi铜矿、Lonshi铜矿以及赞比亚Lubambe铜矿，铜金属产能正处于快速释放期。",
            "磷化工产业链：多元化布局。控股贵州两座磷矿，实现了从矿山建设、采选到磷化工下游（如磷酸铁）的部分覆盖。",
            "机械设备制造：配套支撑。自主研发智能化、自动化地下矿山作业设备，提升服务效率的同时实现进口替代。",
        ],
    ),
    CompanyInfo(
        company_name="明泰铝业",
        ticker="601677",
        exchange="SSE",
        country="China",
        market_cap=0.0,
        last_price=0.0,
        sector="有色金属 / 铝加工",
        industry="铝板带箔 / 再生铝循环",
        pe_ratio=0,
        dividend_yield=0,
        description="明泰铝业是中国领先的铝板带箔加工企业，已实现从传统加工向‘绿色制造+高端转型’的跨越。公司核心护城河在于百万吨级的再生铝保级利用产能，通过‘城市矿山’回收实现极低的碳排放与能源成本。随着义瑞新材、鸿晟新材等高端产能释放，公司正切入汽车轻量化、电池箔及航天等高附加值赛道。其独特的‘铝价+加工费’模式叠加再生铝成本优势，使其在铝价剧烈波动期展现出极强的利润弹性。",
        tags=[
            "再生铝保级利用龙头",
            "绿色低碳先行者",
            "汽车轻量化核心供方",
            "家里有废铝矿",
            "铝价上涨受益者",
            "产能扩张红利期",
            "超低估值成长股",
        ],
        competitors=[
            "南山铝业 (600219)",
            "鼎胜新材 (603876)",
            "常铝股份 (002160)",
            "天山铝业 (002532)",
            "海德鲁 (Norsk Hydro)",
            "奥科宁克 (Arconic)",
        ],
        websites={"official": "https://www.hngymt.com/"},
        analysis=[
            "优点：极致的成本控制。拥有100万吨再生铝产能，相比原铝能耗降低95%，在铝价高企时，再生铝带来的‘成本剪刀差’直接转化为超额利润。",
            "优点：高端产能放量。义瑞新材、鸿晟新材等项目在2026年进入全面爬坡期，年产销量有望跨越200万吨关口，规模效应显著增强。",
            "优点：低碳出口优势。在全球碳关税（CBAM）背景下，明泰凭借再生铝的低碳足迹，在海外市场拥有极高的环境溢价和市场准入优势。",
            "缺点：原材料价格剧烈波动。虽然有加工费支撑，但极端铝价波动可能导致短期库存减值或下游需求受抑。",
            "缺点：行业竞争加剧。国内铝板带箔同质化竞争依然存在，高端汽车板和电池箔领域的研发投入及客户认证周期较长。",
            "缺点：地缘贸易风险。约30%业务为海外出口，面临反倾销调查及全球物流成本波动的挑战。",
        ],
        product_lines=[
            "再生铝业务：公司的‘第二矿山’。保级利用易拉罐、汽车碎片等废铝，支撑百万吨级低碳铝材生产，毛利远超行业均值。",
            "汽车轻量化板材：高端增长极。供应新能源车车身板、防撞梁等关键部位，单吨加工费是传统产品的3倍以上。",
            "新能源电池箔：核心切入。布局高精度电池箔及铝塑膜用箔，受益于全球储能及动力电池装机量的爆发。",
            "传统铝板带箔：基本盘。覆盖包装、印刷、基建等领域，产销量连续多年蝉联国内第一。",
        ],
    ),
    CompanyInfo(
        company_name="杭氧股份",
        ticker="002430",
        exchange="SZSE",
        country="China",
        market_cap=270.0,  # 亿人民币 (2026年3月约值)
        last_price=27.72,  # 2026年3月25日收盘价
        sector="工业机械 / 能源设备",
        industry="工业气体 / 深冷装备 / 氢能与航天配套",
        pe_ratio=17.5,  # 基于2026年预估利润计算
        dividend_yield=2.8,  # 预估分红率
        description="杭氧股份是中国工业气体的领军企业，已完成从‘重型装备制造’到‘工业气体服务’的战略转型。公司依托全球领先的深冷技术，建立了‘装备制造+气体销售’的双轮驱动模式，气体销售收入占比已超60%。作为国内唯一的核聚变液氦系统及商业航天液氢液氧装备供应商，公司正凭借其在 -269°C 极低温领域的统治力，切入商业航天、核聚变及氢能等万亿级未来赛道。其‘长协供气’模式带来的稳定现金流，使其在工业周期波动中展现出极强的抗风险能力。",
        tags=[
            "工业气体国产替代龙头",
            "商业航天液氢液氧核心供方",
            "核聚变超低温系统先行者",
            "氦气资源国产化先锋",
            "工业界的‘包租婆’",
            "氢能全产业链布局者",
            "被低估的科技基建股",
        ],
        competitors=[
            "林德 (Linde Plc)",
            "法液空 (Air Liquide)",
            "大阳日酸 (Taiyo Nippon Sanso)",
            "空气化工 (Air Products)",
            "盈德气体 (已退市/私有化)",
            "陕鼓动力 (601323)",
        ],
        websites={"official": "https://www.hangyang.com/index.html"},
        analysis=[
            "优点：稳健的商业模式。长达15-20年的气体供应合同提供了极高的利润确定性，设备折旧期后利润弹性巨大。",
            "优点：技术壁垒极高。掌握 -269°C 级深冷核心技术，在商业航天（液氢）、核聚变（液氦）领域拥有绝对的稀缺性和排他性。",
            "优点：特种气体爆发。宇航级氪、氙气及自主提氦业务进入放量期，高毛利产品占比提升显著改善盈利结构。",
            "缺点：下游行业集中度高。钢铁、煤化工等传统行业的需求波动仍会影响存量气厂的产能利用率及应收账款安全。",
            "缺点：重资产运营压力。大规模在建项目转固后带来的折旧增加和财务利息压力，可能在短期内压制净利润表现。",
            "缺点：国际巨头竞争。在高端电子特气及全球化布局方面，与林德、法液空等国际巨头仍存在系统性差距。",
        ],
        product_lines=[
            "工业气体业务：公司的‘现金奶牛’。通过现场供气和管网供气，为钢铁、化工、半导体客户提供氧、氮、氩等基础工业血液。",
            "特种气体与氦气：高附加值增长极。自主研发宇航级特气及国产氦气，打破国外垄断，直接受益于商业航天及核聚变实验爆发。",
            "深冷装备制造：技术护城河。生产全球领先的特大型空分装置、液氢/液氦存储设备，是国内航天发射场及大科学装置的首选供方。",
            "氢能与新能源业务：未来爆发点。布局液氢生产、储运及加注全产业链，切入绿氢及清洁燃料航空赛道。",
        ],
    ),
    CompanyInfo(
        company_name="康达新材",
        ticker="002669",
        exchange="SZSE",
        country="China",
        market_cap=46.5,  # 亿人民币 (2026年4月约值，随股价波动)
        last_price=13.15,  # 2026年4月10日收盘价
        sector="基础化工 / 电子信息",
        industry="特种胶粘剂 / 半导体材料 / 军工电子",
        pe_ratio=34.2,  # 基于2026年并表后的预估利润计算
        dividend_yield=0.8,  # 国资入主后更侧重于研发投入，分红预期较低
        description="康达新材是中国特种胶粘剂行业的龙头，在唐山国资（唐山工控）入主后，已蜕变为一家‘新材料+电子信息’双轮驱动的国资科技平台。公司在保持风电叶片胶、电子胶国内领先地位的同时，通过激进并购切入‘第二、第三增长曲线’。\
            其控股子公司中科华微聚焦特种集成电路（芯片），必控科技深耕电磁兼容（军工电子），而大连齐化则通过 5.85 亿定增资金发力 PAE（算力材料）及电子级环氧树脂。公司正处于从‘低毛利化工产品’向‘高附加值电子材料’转型的估值重塑关键期。",
        tags=[
            "唐山国资委亲儿子",
            "AI算力板材料国产替代",
            "特种芯片（中科华微）并表先行者",
            "军工电子屏蔽领域龙头",
            "风电胶粘剂隐形冠军",
            "困境反转：从扭亏到高增长",
            "十五五‘新材料+芯片’旗舰平台",
        ],
        competitors=[
            "回天新材 (300041)",
            "德邦科技 (688035)",
            "光威复材 (300699)",
            "雅克科技 (002409)",
            "圣泉集团 (605589)",
            "汉高 (Henkel - 国际巨头)",
        ],
        websites={"official": "http://www.sh-kangda.com/"},
        analysis=[
            "优点：国资信用背书。唐山工控董事长王建祥亲自挂帅，5.85亿定增获批，解决了高科技转型过程中的‘烧钱’焦虑和财务安全。",
            "优点：赛道稀缺性。大连齐化的 PAE 材料和电子级树脂直接对标 AI 服务器高频高速 PCB 板，是目前半导体上游极其紧缺的国产化环节。",
            "优点：业绩并表弹性。2026年是中科华微等高毛利业务完整并表的第一年，营收质量将发生质变，毛利率有望显著拉升。",
            "缺点：整合与文化割裂。总部‘化工老国企’管理思维与子公司‘高精尖技术团队’的融合仍需磨合，管理效率和官网审美有待提升。",
            "缺点：项目建设周期。大连 PAE 等核心增量项目需 18 个月建设期，2026 年主要依靠预期驱动而非实质营收，存在时间差风险。",
            "缺点：股本稀释压力。定增完成后总股本增加约 10%-15%，若业绩释放速度不及稀释速度，短期每股收益（EPS）可能承压。",
        ],
        product_lines=[
            "特种胶粘剂板块：公司的‘现金奶牛’。涵盖风电、电子、汽车用胶，为集团转型提供基础现金流，正向高端国产化方向升级。",
            "电子信息材料（第二曲线）：核心变量。依托大连齐化，生产电子级环氧树脂及 PAE 材料，切入 AI 算力供应链，是 2026 年定增的核心投向。",
            "电子科技板块（第三曲线）：高估值引擎。由中科华微和必控科技组成，主攻特种芯片、军工滤波及电磁兼容，直接受益于国防信息化和商业航天。",
            "光伏与新能源配套：辅助业务。提供光伏组件封装材料及新能源车结构胶，随行业周期波动提供一定的业绩补充。",
        ],
    ),
    CompanyInfo(
        company_name="横店东磁",
        ticker="002056",
        exchange="SZSE",
        country="China",
        market_cap=215.8,  # 亿人民币 (2026年4月约值，随股价波动)
        last_price=13.25,  # 2026年4月10日收盘价参考
        sector="有色金属 / 电力设备",
        industry="磁性材料 / 光伏组件 / 锂电池",
        pe_ratio=11.6,  # 基于2025年稳健利润及2026年行业回暖预期
        dividend_yield=6.2,  # 2025年度派息率大幅提升后的预期股息率
        description="横店东磁被誉为“中国磁都”，是全球最大的永磁铁氧体和软磁材料生产基地。公司已成功构建“磁材+光伏+锂电”三轮驱动格局。\
            作为横店集团旗下的旗舰上市公司，其经营风格极其稳健，财务指标长期保持“三低一高”（低负债、低库存、低成本、高周转）。\
            公司在保持磁性材料绝对领导地位的同时，深度垂直一体化布局光伏产业链，尤其在欧洲分布式光伏市场拥有极强的渠道品牌溢价。\
            2025年后，公司从“激进扩张”转向“高质量经营”，通过大幅提高分红比例，正在从成长股向‘高股息价值股’进行赛道重塑。",
        tags=[
            "全球磁材领军者",
            "欧洲分布式光伏隐形冠军",
            "横店系现金奶牛",
            "高股息/红利资产新贵",
            "80%+ 超高分红率方案（2025）",
            "磁材+锂电双向跨界",
            "Apple/Tesla 供应链常客",
        ],
        competitors=[
            "领益智造 (002600)",
            "天通股份 (600330)",
            "金力永磁 (300748)",
            "晶澳科技 (002459)",
            "通威股份 (600438)",
            "TDK (日本巨头)",
        ],
        websites={"official": "https://www.chinadmegc.com/"},
        analysis=[
            "优点：极佳的资产负债表。财务极其干净，常年维持高ROE与低负债率，现金流充沛，抗周期风险能力极强。",
            "优点：差异化光伏战略。不参与国内卷价格的地面电站肉搏，深耕欧洲高端屋顶光伏市场，毛利率长期高于行业平均水平。",
            "优点：股东回馈意愿强烈。2025年分红方案震惊市场，股利支付率从40%跳升至80%以上，展现了成熟期企业向价值型投资标的转型的信号。",
            "缺点：行业产能过剩压力。虽然公司成本控制卓越，但在光伏行业整体下行周期中，其光伏板块营收增长和利润率仍面临下修风险。",
            "缺点：锂电业务规模尚小。虽主打差异化的小动力和储能圆柱电池，但在锂电巨头挤压下，盈利空间的护城河尚未完全稳固。",
            "缺点：由于其稳健经营风格，在科技牛市中往往缺乏爆发性的题材炒作，属于典型的‘慢牛’或‘防守型’标的。",
        ],
        product_lines=[
            "磁性材料板块：公司的底层资产。全球市占率领先，受经济周期影响相对较小，为其他板块提供稳定的研发现金支撑。",
            "光伏组件板块：当前的营收支柱。深耕Black Module（黑组件）等高端差异化产品，主攻欧洲及东南亚分布式市场。",
            "锂电业务板块：增长第三极。聚焦小动力工具及家用储能领域，通过圆柱电池差异化路线，补充非光伏周期的业绩波动。",
            "器件板块：向下游延伸。涵盖振动马达、电感、无线充电模组等，直接对接消费电子及汽车电子头部客户。",
        ],
    ),
    CompanyInfo(
        company_name="人福医药",
        ticker="600079",
        exchange="SSE",
        country="China",
        market_cap=302.8,  # 亿人民币 (2026年4月)
        last_price=18.55,  # 2026年4月10日收盘价参考
        sector="医药生物 / 化学制药",
        industry="麻醉镇痛药 / 甾体激素 / 民族药",
        pe_ratio=16.3,  # 动态市盈率
        dividend_yield=2.6,  # 2025年度派息方案为10派4.8元，股息率约2.6%
        description="人福医药是国内麻醉镇痛药领域的绝对龙头，被业内称为“麻醉一哥”。核心子公司宜昌人福在芬太尼、瑞芬太尼等受严格管制的麻醉药品领域拥有极高的技术壁垒和近乎垄断的市场份额。公司曾深受前控股股东“当代系”债务违约及资金占用困扰，被贴上ST标签。\
        2025年起，随着央企招商局集团正式入主并开启“重塑人福”战略，公司坚定落实“归核聚焦”，持续剥离非核心商业及周边业务（如杰士邦、医疗器械等），财务结构显著改善，负债率大幅下降，正从“困境资产”向“央企背景的高端制造平台”质变。",
        tags=[
            "麻醉药国家队/垄断者",
            "招商局集团控股（央企入主）",
            "核心产品市占率80%+",
            "归核聚焦战略先行者",
            "ST脱帽预期（2026年关键期）",
            "芬太尼全系列布局",
            "高研发投入驱动的仿制药转型创新药",
        ],
        competitors=[
            "恒瑞医药 (600276) - 麻醉领域核心对手",
            "恩华药业 (002262) - 中枢神经系统竞争",
            "国药现代 (600420)",
            "仙琚制药 (002332) - 甾体激素竞争",
            "辉瑞 (Pfizer - 国际巨头)",
        ],
        websites={"official": "http://www.renfu.com.cn/"},
        analysis=[
            "优点：核心护城河极深。麻醉药属于国家管控品种，准入壁垒极高，利润率稳定，是极其稀缺的“牌照类”医药资产。",
            "优点：经营质量质变。2025年扣非净利润增长超50%，剥离亏损及低效资产后，毛利率和现金流指标已达到历史最佳水平。",
            "优点：大股东赋能。招商局入主解决了资金链和信用危机，通过定增注资30-35亿进一步降低融资成本，估值体系有望从“折价”转向“溢价”。",
            "缺点：ST标签的流动性限制。虽基本面反转，但在正式撤销风险警示前，部分机构资金仍受限于入场门槛，股价弹性受限。",
            "缺点：集采压力持续。尽管麻醉管控药受影响小，但公司的其他仿制药板块（如甾体激素、普药）仍面临带量采购带来的利润挤压。",
            "缺点：国际化业务波动。美国子公司Epic Pharma等在海外市场受合规与关税政策影响，盈利贡献存在一定不确定性。",
        ],
        product_lines=[
            "中枢神经系统（麻醉）板块：核心盈利引擎。涵盖芬太尼全系列、氢吗啡酮等，毛利率常年维持在 80% 以上。",
            "甾体激素板块：产业链一体化。葛店人福负责原料药与制剂出口，已实现全球市场份额领先，是稳健的现金流补充。",
            "民族药板块（新疆维药）：特色增长极。核心品种祖卡木颗粒等在慢性病及基层市场渗透率极高，受益于中医药出海政策。",
            "创新药/ANDA管线：未来增量。每年投入 15 亿+ 研发资金，已有多个 1 类新药及数百个美国 ANDA 文号，支撑长期可持续增长。",
        ],
    ),
    CompanyInfo(
        company_name="均胜电子",
        ticker="600699",
        exchange="SSE / HKEX (00699.HK)",
        country="China",
        market_cap=385.2,  # 亿人民币 (A+H 合计，2026年4月)
        last_price=18.42,  # A股参考价
        sector="汽车 / 汽车零部件",
        industry="智能驾驶域控 / 汽车安全 / 舱驾融合",
        pe_ratio=18.5,  # 2025年业绩反转后的动态市盈率
        ps_ratio=0.58,  # 极具吸引力的低市销率，反映重资产折价
        dividend_yield=1.5,  # 处于债务治理期，分红水平尚在恢复
        description="均胜电子是全球领先的汽车零部件一级供应商（Tier 1），通过并购德国普瑞、美国KSS及日本高田，构建了横跨“汽车安全”与“汽车电子”的全球版图。公司正经历从“被动安全件”向“主动智驾大脑”的结构性质变。随着 2025 年底 H 股成功上市，长期压制估值的财务杠杆风险显著降低，公司已成为高通、英伟达、地平线等芯片巨头在中央计算单元（CCU）领域的首选集成伙伴，深度受益于 L3 级自动驾驶的量产元年。",
        tags=[
            "全球汽车安全前二",
            "中央计算单元(CCU)先行者",
            "A+H两地上市(00699.HK)",
            "困境反转/经营杠杆弹性",
            "800V高压快充核心链",
            "华为/英伟达智驾生态圈",
            "海外业务扭亏为盈",
        ],
        competitors=[
            "博世 (Bosch) - 全球 Tier 1 老大",
            "安波福 (Aptiv) - 智驾架构核心竞争",
            "经纬恒润 (688326) - 国内域控竞争",
            "德赛西威 (002920) - 智能座舱强劲对手",
            "奥托立夫 (Autoliv) - 汽车安全领域死磕",
        ],
        websites={"official": "https://www.joyson.com/"},
        analysis=[
            "优点：估值体系重构。长期以来市场将其视为低毛利制造厂，随着CCU和舱驾融合产品放量，其软件和算法价值正被重新定价，0.6倍左右的PS极具安全边际。",
            "优点：全球化交付护城河。作为少数能直接进入BBA（奔驰宝马奥迪）全球研发体系的中国供应商，其跨国管理能力和全球工厂布局是躲避贸易限制的天然屏障。",
            "优点：财务反转确认。2025年净利润同比增幅近40%，海外高田工厂整合基本收尾，净利率进入上行通道。",
            "缺点：大股东质押悬剑。王剑峰及其一致行动人质押比例常年维持在60%以上，对股价形成了长期的心理压制。",
            "缺点：重资产折旧压力。全球60余家工厂的运营成本及数万名海外员工的福利开支，导致其净利率（约2.5%-3%）远低于纯软件公司。",
            "缺点：AH溢价波动。港股价格长期较A股存在40%+的折价，反映了外资机构对其重资产模式仍持谨慎态度。",
        ],
        product_lines=[
            "智能驾驶/电子板块：核心增长引擎。涵盖智驾域控、中央计算单元（CCU）、智能座舱，单车价值量较传统件提升数倍。",
            "汽车安全板块：基本盘。安全气囊、安全带及集成安全方案，全球市占率约25%左右，提供稳定的现金流支撑。",
            "新能源管理板块：增量亮点。800V高压快充、功率分配单元（PDU）及电池管理系统（BMS），深度绑定全球主流电车品牌。",
        ],
    ),
    CompanyInfo(
        company_name="移远通信",
        ticker="603236",
        exchange="SSE",
        country="China",
        market_cap=208.5,  # 亿人民币 (2026年4月)
        last_price=58.10,  # 2026年4月参考价
        sector="通信 / 通信设备",
        industry="物联网模组 / 卫星通信 / 车载通信",
        pe_ratio=26.8,  # 研发投入高增长期的动态市盈率
        dividend_yield=0.8,  # 典型高成长科技股，分红比例较低
        description="移远通信是全球物联网无线通信模组的出海冠军，连续多年蝉联全球市占率第一。公司建立了以“工程师红利+规模效应”为核心的护城河，拥有超过 4000 名研发工程师。目前正处于从单纯硬件商向“模组+天线+云服务”的一站式方案商转型。2025 年底完成的 22.5 亿定增标志着公司正式全面押注“空天地一体化”赛道，其卫星通信（NTN）模组和 5G-A 模组正成为商业航天和低空经济在地面终端落地的标准配置。",
        tags=[
            "全球物联网模组冠军",
            "卫星通信（NTN）卖水人",
            "低空经济/5G-A核心链",
            "高通骁龙生态深度伙伴",
            "22.5亿定增（85元成本线）",
            "出海业务占比50%+",
            "工程师红利驱动型研发",
        ],
        competitors=[
            "广和通 (300638) - 国内核心竞争对手",
            "泰利特 (Telit) - 海外高端市场竞争",
            "美格智能 (002881) - 车载/智能模组竞争",
            "中兴通讯 (000063)",
            "高通 (Qualcomm) - 既是核心供应商也是潜在竞争",
        ],
        websites={"official": "https://www.quectel.com/cn/"},
        analysis=[
            "优点：卡位确定性极强。无论物联网、商业航天还是AI机器人，只要需要联网，就绕不开移远的模组，是数字化时代的基建标的。",
            "优点：全球准入壁垒。拥有超过1500个全球运营商及强制性认证，这种“时间成本”是初创公司无法通过烧钱在短期内追赶的。",
            "缺点：大股东减持负面预期。创始人及控股平台持续的减持动作，以及定增价（85.21元）与现价严重倒挂，导致市场信心脆弱。",
            "缺点：产业链话语权偏弱。处于“夹心饼干”层，上游受制于芯片巨头专利授权，下游面对车企及终端厂商的极限压价，毛利率提升困难。",
            "缺点：现金流压力。为了维持全球第一的规模，需要大量的存货备货和持续的高额研发，2025年定增虽缓解了燃眉之急，但人头开支依然沉重。",
        ],
        product_lines=[
            "蜂窝通信模组：营收支柱。4G/5G模组，涵盖支付、POS、智能表计等全行业应用。",
            "车载业务板块：利润锚点。5G车联网模组及智能座舱方案，单价及毛利显著高于工业模组。",
            "卫星通信（NTN）板块：战略蓝海。针对商业航天领域，提供地面终端与卫星直接连接的通信方案，预计 2026 年进入放量期。",
            "天线与云服务：转型增量。提供一体化连接服务，旨在提升客户粘性并改善原本毛利偏低的硬件模式。",
        ],
    ),
    CompanyInfo(
        company_name="中联重科",
        ticker="000157",
        exchange="SZSE / HKEX (01157.HK)",
        country="China",
        market_cap=728.4,  # 亿人民币 (A+H 合计，2026年4月参考值)
        last_price=8.24,  # A股参考价
        sector="工业 / 工程机械",
        industry="具身智能机器人 / 智慧农机 / 高端装备制造",
        pe_ratio=14.2,  # 基于 2025 年净利润（约 48.6 亿）的动态市盈率
        ps_ratio=1.35,  # 反映出市场仍将其视为传统机械，未完全计入 AI 溢价
        dividend_yield=5.8,  # 典型的高红利蓝筹，分红意愿极强
        description="中联重科是全球工程机械巨头，正处于从“钢铁巨兽”向“具身智能体”的战略突围期。公司斥资千亿打造的“中联智慧产业城”已成为全球最大的单体智能制造园区。通过自研 Robot Ops 具身智能操作系统及 Z01 人形机器人，公司实现了从传统土方、起重机械向人工智能硬件平台的跨越。作为 A+H 两地上市公司，其海外营收占比已突破 60%，成为中国高端制造“出海套利”的领军者。",
        tags=[
            "全球起重机前二",
            "具身智能 OS (Robot Ops) 定义者",
            "A+H 两地上市 (01157.HK)",
            "中联智慧产业城 (千亿级基地)",
            "高股息/中特估核心标的",
            "人形机器人批量化元年 (2026)",
            "海外营收占比 60%+",
        ],
        competitors=[
            "卡特彼勒 (Caterpillar) - 全球行业霸主",
            "三一重工 (600031) - 国内全线竞争对手",
            "徐工机械 (000425) - 起重机领域核心对手",
            "特斯拉 (Optimus) - 具身智能/机器人赛道跨界竞争",
            "小松 (Komatsu) - 数字化施工竞争",
        ],
        websites={"official": "https://www.zoomlion.com/"},
        analysis=[
            "优点：估值逻辑重构。公司已脱离纯基建周期，Robot Ops 系统的发布使其具备了 AI 软件溢价潜力，目前 14 倍左右的 PE 远低于 AI 机器人板块平均水平。",
            "优点：全球化交付韧性。海外研发制造基地（如意大利 CIFA、德国 Wilbert）提供了极强的地缘避险能力，出口毛利远高于国内。",
            "优点：极致的规模效应。9000 亩智慧产业城投产后，每 6 分钟下线一台挖掘机的生产效率提供了极强的单吨成本控制力。",
            "缺点：短期折旧压力。1000 亿投资进入转固高峰期，庞大的固定资产折旧将对 2026-2027 年的短期净利率形成压制。",
            "缺点：周期惯性。尽管机器人业务性感，但贡献 80% 以上营收的依然是工程机械，全球基建投资增速放缓会直接拉低业绩上限。",
            "缺点：应收账款体量。由于行业特性，其应收账款与利润比率较高，对下游基建回款的依赖度较大，存在信用减值波动的风险。",
        ],
        product_lines=[
            "工程机械板块：基本盘。涵盖起重机、混凝土机、挖掘机，市占率稳居全球第一梯队，是公司现金流的定海神针。",
            "人工智能/机器人板块：核心增长极。以 Z01 人形机器人、Robot Ops 系统及智能分拣体为主，目标是实现工厂“无人化”并外销方案。",
            "智慧农机/高空平台板块：高成长曲线。聚焦农业现代化与新能源高空作业，毛利率显著高于传统基建机械。",
        ],
    ),
    CompanyInfo(
        company_name="北斗星通",
        ticker="002151",
        exchange="SZSE (深交所)",
        country="China",
        market_cap=186.5,  # 亿人民币 (2026年4月参考值)
        last_price=28.45,  # 2026年A股参考价
        sector="信息技术 / 电子",
        industry="卫星导航 / 半导体设计 / 低空经济基建",
        pe_ratio=42.8,  # 处于 22nm 芯片大规模放量与汽车业务减亏的业绩拐点期
        ps_ratio=4.1,  # 市场正将其从“硬件组装”重估为“核心 IP/算力芯片”标的
        dividend_yield=0.8,  # 研发驱动型企业，分红较低，利润主要用于先进制程芯片研发
        description="北斗星通是中国卫星导航产业的开创者与“芯”高度定义者。公司通过旗下的芯星通（Ufire）掌握了全球领先的 22nm/12nm 全系统全频点高精度定位芯片技术。2026年，随着“千帆星座”大规模组网与低空经济（无人机）的爆发，公司实现了从单一北斗导航向“高精度定位+时空算力芯片+云服务”的闭环转型，成为海陆空万物互联的“时空索引”提供商。",
        tags=[
            "国产高精度定位芯片 (22nm) 领军者",
            "低空经济/eVTOL 核心供应链",
            "集成电路大基金三期重点覆盖",
            "卫星导航第一股",
            "时空算力平台 (高精度定位 + 组合导航)",
            "千帆星座/低空感知关键环节",
            "华为/小米/智驾车企 核心供应商",
        ],
        competitors=[
            "Trimble (天宝) - 全球高精度定位行业标杆",
            "u-blox (瑞士) - 全球消费级导航芯片巨头",
            "华测导航 (300627) - 下游应用端最强对手",
            "海格通信 (002465) - 军工领域及卫星通信竞争",
            "中海达 (300177) - 测绘设备及激光雷达竞争",
        ],
        websites={"official": "http://www.bdstar.com/"},
        analysis=[
            "优点：技术壁垒极深。公司自研的火鸟 (Firebird) 系列芯片在低功耗与抗干扰指标上已达到国际一流水准，是国内少数能与 u-blox 正面抗衡的国产芯。",
            "优点：赛道弹性极强。低空经济（无人机/eVTOL）对厘米级定位是刚需，北斗星通作为底层模组商，具有“量价齐升”的逻辑，单台设备价值量随智驾等级提升而增加。",
            "优点：产业重组预期。公司近年来剥离了低毛利的传统业务，聚焦核心芯片，资产质量明显改善，正处于毛利率提升的长周期中。",
            "缺点：研发开支极高。5nm 级定位芯片的研发投入巨大，若新一代芯片验证进度不及预期，将对短期利润产生较大冲击。",
            "缺点：汽车业务内卷。智能网联业务虽然营收占比高，但面对主机厂的极度压价，该板块毛利率持续低迷，对整体净利润形成拖累。",
            "缺点：地缘供应链风险。高性能芯片生产仍依赖全球代工体系，地缘局势变化可能导致晶圆代工产能受限，影响高端芯片的供货稳定性。",
        ],
        product_lines=[
            "基础器件板块：核心护城河。涵盖高精度定位芯片、板卡、天线，是公司利润的 70% 来源，服务于智驾、机器人及测绘市场。",
            "汽车智能网联板块：规模支撑。提供车载导航、智能座舱及 T-Box 终端，目前处于由量向质转变的去冗余期。",
            "云服务/时空数据板块：未来增长极。通过“真确（TrueFix）”服务提供高精度差分定位服务，目标是实现订阅制的软件服务收入（SaaS）。",
        ],
    ),
    CompanyInfo(
        company_name="TCL 科技",
        ticker="000100",
        exchange="SZSE (深交所)",
        country="China",
        market_cap=820.4,  # 亿人民币 (2026年4月参考值)
        last_price=4.37,  # 2026年A股参考价
        sector="信息技术 / 半导体 / 消费电子",
        industry="半导体显示 (LCD/OLED) / 太阳能单晶硅 / 产业金融",
        pe_ratio=26.5,  # 处于大尺寸 LCD 价格回升与 OLED 业务减亏的利润向上拐点
        ps_ratio=0.45,  # 典型重资产行业，市值远低于年营收，具有极高的重置成本与资产溢价空间
        dividend_yield=2.1,  # 随着业绩回暖，分红意愿较之前有所提升
        description="TCL 科技是全球半导体显示产业的双寡头之一。公司通过旗下核心资产“TCL 华星”掌握了全球领先的 HVA、LTPS 及柔性 OLED 显示技术，大尺寸电视面板市场份额稳居全球前二。\
            2020年通过并购天津中环（TCL 中环）跨界切入光伏硅片赛道，形成了“显示面板 + 绿色能源”的双主业格局。\
                2026年，随着 LCD 行业竞争格局彻底从“扩产杀价”转向“利润导向”，TCL 科技正迎来大尺寸面板议价权回归带来的盈利长周期复苏。",
        tags=[
            "全球 LCD 大尺寸面板双寡头 (与京东方并列)",
            "210mm 大尺寸光伏硅片开创者 (TCL 中环控股)",
            "半导体显示国产替代核心标的",
            "折叠屏/柔性 OLED 供应链关键环节",
            "Mini LED / Micro LED 前沿技术领先者",
            "A500/沪深300 重要权重股",
            "华为 Mate 系列/苹果 iPad 潜在及核心供应商",
        ],
        competitors=[
            "京东方 (000725) - 全球显示领域头号对手",
            "深天马 (000050) - 中小尺寸面板竞争",
            "隆基绿能 (601012) - 光伏业务主要竞争对手",
            "三星显示 (Samsung Display) - OLED 高端技术竞争",
            "LG Display (LGD) - 大尺寸 OLED 差异化竞争",
        ],
        websites={"official": "https://www.tcltech.com/"},
        analysis=[
            "优点：LCD 格局改善。韩系厂家退出大尺寸 LCD，行业进入动态控产阶段，价格波动率降低，TCL 华星作为存量巨头，开始收割长期利润。",
            "优点：技术迭代空间。公司在印刷 OLED 和 Micro LED 技术上储备深厚，且在平板、笔记本等 IT 中尺寸面板领域渗透率快速提升，产品结构持续优化。",
            "优点：产业链垂直整合。通过控股中环，实现了从核心半导体材料到终端应用的纵向整合，具有较强的抗原材料波动风险能力。",
            "缺点：重资产折旧压力。每年百亿级的资本支出和生产线折旧，对净利润形成巨大长期压制，需极高的开工率来摊薄成本。",
            "缺点：光伏业务拖累。受 2025-2026 年光伏行业产能过剩影响，控股子公司 TCL 中环的巨额亏损对集团整体利润形成了严重负向拖拽。",
            "缺点：宏观消费依赖。面板需求高度依赖电视、手机等终端消费市场，在全球经济增长乏力的背景下，需求端修复斜率可能低于预期。",
        ],
        product_lines=[
            "半导体显示业务 (TCL 华星)：核心支柱。涵盖电视、电竞显示器及手机屏，营收占比约 60%，是大尺寸 HVA 技术的全球领跑者。",
            "新能源光伏业务 (TCL 中环)：第二曲线。专注单晶硅片、电池组件。210mm 硅片全球市占率领先，虽然目前处于周期底部，但具备极强的市场出清后反弹弹性。",
            "产业金融及投资：现金流调节器。通过股权投资布局半导体产业链上下游（如志翔科技等），获取产业协同收益。",
        ],
    ),
    CompanyInfo(
        company_name="格林美",
        ticker="002340",
        exchange="SZSE (深交所)",
        country="China",
        market_cap=358.5,  # 亿人民币 (2026年5月参考值，股本约51.3亿股)
        last_price=6.98,  # 2026年5月A股参考价
        sector="原材料 / 新能源 / 循环经济",
        industry="锂电三元前驱体 / 电池回收与梯次利用 / 镍钴钨资源综合利用",
        pe_ratio=18.4,  # 2026年伴随碳酸锂价格反弹与印尼镍矿达产，利润进入爆发期，PE 处于历史中低位
        ps_ratio=0.92,  # 营收规模巨大（约370-400亿），典型的“高周转、低 PS”资源加工型标的
        dividend_yield=1.8,  # 作为资源循环龙头，维持稳定的现金分红以回报长线机构资金
        description="格林美是全球循环经济与城市矿山开采的领军企业。公司形成了“城市矿山+新能源材料”的双轨驱动模式，\
        是全球前三的三元前驱体供应商。通过深耕“动力电池回收—材料再造—电池再造”的闭环产业链，\
        格林美成功在印尼完成了镍资源原材料的深度布局（青美邦 HPAL 项目）。\
        2026年，随着碳酸锂价格从底部剧烈反弹及全球动力电池首波“报废潮”来临，\
        格林美正从纯粹的加工型企业向“资源+材料”双重属性的巨头转型。",
        tags=[
            "全球三元前驱体核心供应商 (核心配套宁德时代、三星SDI)",
            "印尼镍资源布局先锋 (青美邦 HPAL 项目达产)",
            "中国动力电池回收行业标准制定者",
            "稀有金属（钴、钨）循环利用全球龙头",
            "碳酸锂/锂电材料困境反转核心标的",
            "ESG 绿色金融标杆企业 (瑞士交易所 GDR 上市)",
            "A500/深证成指/创业板指 重要权重股",
        ],
        competitors=[
            "中伟股份 (300919) - 三元前驱体领域头号对手",
            "华友钴业 (603799) - 上游资源与前驱体全线竞争",
            "天赐材料 (002709) - 锂电中游材料估值对标",
            "宁德时代 (300750) - 既是核心客户，也在回收领域存在布局竞争",
            "邦普循环 (宁德时代旗下) - 电池回收直接竞争对手",
        ],
        websites={"official": "http://www.gem.com.cn/"},
        analysis=[
            "优点：资源自供率提升。印尼镍资源项目大规模贡献业绩，极大地对冲了原材料波动风险，提升了三元前驱体的整体毛利率。",
            "优点：回收渠道壁垒。拥有中国最广泛的报废汽车与电子废弃物回收网络，随着 2026 年报废高峰期到来，低成本原料获取能力无可替代。",
            "优点：全球化溢价。通过 GDR 在瑞士上市并深度嵌入欧洲供应链，享受海外绿色碳足迹认证带来的产品溢价。",
            "缺点：财务杠杆较高。为维持印尼项目与国内回收网络扩张，长期存在较高的有息负债，对利率环境较为敏感。",
            "缺点：技术路线风险。押注高镍三元路线，虽然能量密度占优，但若磷酸铁锂（LFP）或钠电池在乘用车市场渗透过快，将压制其长期成长空间。",
            "缺点：存货价值波动。由于营收流水巨大且涉及大量大宗金属，金属价格（镍、锂、钴）的剧烈宽幅震荡会对短期财报净利润造成较大的干扰。",
        ],
        product_lines=[
            "新能源材料业务：核心支柱。包括三元前驱体、四氧化三钴等，营收占比超 70%，受益于 2026 年全球电动化渗透率进一步提升。",
            "城市矿山与回收：基本盘。回收钴、镍、铜、钨及电子废弃物。不仅是利润来源，更是公司维持“绿色标签”的核心竞争力。",
            "电池包再制造与梯次利用：新兴增长极。将退役动力电池转化为储能电池或低速车电池，实现电池全生命周期的价值榨取。",
        ],
    ),
    CompanyInfo(
        company_name="紫光股份",
        ticker="000938",
        exchange="SZSE (深交所)",
        country="China",
        market_cap=906.36,  # 亿人民币 (2026年5月11日收盘值)
        last_price=31.69,  # 2026年5月11日收盘价
        sector="科技 / 信息技术 / 云计算",
        industry="ICT 基础设施 / 交换机与路由器 / 服务器 / 云计算服务",
        pe_ratio=42.66,  # TTM 估值，处于 AI 算力基建高景气度区间
        ps_ratio=1.12,  # 典型的 ICT 硬件巨头特征，营收规模庞大且增长稳健
        dividend_yield=0.20,  # 处于高研发投入阶段，分红率较低，侧重于资本增值
        description="紫光股份是中国领先的数字化解决方案领导者。公司核心资产为子公司“新华三 (H3C)”，\
    在交换机、企业级 WLAN、路由器及服务器领域长期占据中国市场第一或第二的地位。\
    通过“云—网—安—算—存—端”全产业链布局，紫光股份已成为国内少数能提供全栈式 ICT 基础设施的企业。\
    2026年，随着新紫光集团完成债务重整后的业务大协同，以及公司完成对新华三 49% 少数股权的收购（私有化整合），\
    公司已从单纯的硬件供应商进化为深度参与 AI 算力集群建设与私有云大模型部署的科技巨头。",
        tags=[
            "中国 ICT 基础设施龙头 (交换机/路由器市场份额领先)",
            "AI 算力基建核心标的 (万兆高速交换机、液冷服务器)",
            "新华三 (H3C) 100% 控股整合预期 (核心资产价值回归)",
            "算力网络/低空经济/6G 基础设施 关键配套商",
            "国产替代与数字化转型 核心受益企业",
            "新紫光集团 核心上市旗舰平台",
            "沪深300 / 深证成指 / 中证A500 重要成分股",
        ],
        competitors=[
            "中兴通讯 (000063) - 运营商业务与政企 ICT 全面竞争",
            "浪潮信息 (000977) - 服务器与算力中心建设直接对手",
            "锐捷网络 (301165) - 园区网交换机与 WLAN 领域竞争",
            "华为 (未上市) - 行业最高天花板与全领域头号劲敌",
            "工业富联 (601138) - 算力服务器制造与全球化布局对标",
        ],
        websites={"official": "http://www.unic.com.cn/"},
        analysis=[
            "优点：新华三股权整合。完成少数股权收购后，公司归母净利润有望显著增厚，消除长期压制估值的股权结构悬念。",
            "优点：AI 算力红利。受益于大模型带动的万兆交换机（如 800G/1.6T 交换机）迭代需求，以及 AIGC 对智算中心建设的强力支撑。",
            "优点：全栈能力壁垒。具备从芯片、硬件、操作系统到云平台的完整研发能力，在政务、金融、电信等高门槛行业拥有极深的客户黏性。",
            "缺点：地缘政策风险。核心组件（如高端芯片）的供应链稳定性受国际局势影响较大，海外市场拓展面临一定的政策逆风。",
            "缺点：研发费用支出极高。为了保持技术领先，每年的 R&D 投入巨大，在宏观经济波动期对短期利润表现形成压力。",
            "缺点：市场竞争白热化。在国内政企市场，面临华为、浪潮以及运营商背景（如中移动/中电信）IT 公司的价格战压力。",
        ],
        product_lines=[
            "网络设备业务：压舱石。涵盖核心路由器、以太网交换机及 WLAN，技术水平位居全球第一梯队，是公司利润的毛利高地。",
            "服务器与存储业务：增长引擎。重点布局 AI 智算服务器及全闪存架构，受益于 2026 年企业级 AI 基础设施的大规模换代。",
            "云计算与安全服务：软实力。通过紫光云与新华三安全引擎，提供混合云方案与数字政府解决方案，正从“卖硬件”向“卖服务”转型。",
        ],
    ),
    CompanyInfo(
        company_name="中国化学",
        ticker="601117",
        exchange="SSE (上交所)",
        country="China",
        market_cap=488.62,  # 亿人民币 (2026年5月12日估值，基于近期 8.00 元左右波动)
        last_price=8.00,  # 2026年5月中旬参考价
        sector="工业 / 建筑与工程 / 新材料",
        industry="化工工程 EPC / 己二腈与尼龙 66 / 气凝胶 / 氢能储运",
        pe_ratio=7.52,  # TTM 估值，远低于科技股，处于历史估值底部及建筑板块均值附近
        ps_ratio=0.25,  # 极低的市销率，反映了工程业务庞大的营收基数与较低的工程毛利
        dividend_yield=2.64,  # 基于 2025 年派息方案，作为中字头国企，分红回报相对稳定
        description="中国化学是中国化工工程领域的国家队，全球领先的工业工程综合解决方案提供商。\
    公司正处于从“传统工程承包商”向“硬核科技实业巨头”转型的关键期。核心资产包括天辰公司、华陆公司等顶尖研究院所。\
    2026年，随着天辰齐翔己二腈二期项目的投料试车，公司彻底打破了美国巨头对尼龙 66 关键原料 ADN 的 50 年技术封锁。\
    通过“工程承包 (EPC) + 实业新材料”双轮驱动，中国化学已在气凝胶、高端聚烯烃 (POE)、电子化学品及氢能储运领域形成壁垒，\
    成为国内少有的能将实验室工艺大规模工业化落地的“科学家型”央企。",
        tags=[
            "全球化学工程排头兵 (ENR 排名长期领先)",
            "己二腈国产替代唯一标的 (尼龙 66 全产业链自主可控)",
            "新材料第二增长曲线 (气凝胶、POE、己二腈实业化放量)",
            "极低估值中字头 (PE < 8, PB < 1 的高安全边际标定)",
            "“一带一路”海外大单核心受益者 (中东/俄罗斯能源基建)",
            "氢能储运与 CCUS 碳捕集技术领先者",
            "上证 50 / 中证 A500 重要成分股",
        ],
        competitors=[
            "中油工程 (600339) - 石油化工工程领域的直接竞争对手",
            "万华化学 (600309) - 下游实业新材料领域的行业标杆与潜在竞争",
            "中国中铁 / 中国铁建 - 基础设施与公用工程领域的广义竞争",
            "英威达 (Invista) - 己二腈与尼龙 66 全球市场的头号技术对手",
        ],
        websites={"official": "http://www.cncec.com.cn/"},
        analysis=[
            "优点：实业利润释放。2026年是己二腈二期收割年，实业板块高毛利将显著摊薄传统工程业务的低利润率，驱动净利润 25% 级别的增长。",
            "优点：技术壁垒极高。掌握丁二烯法己二腈制备、气凝胶超临界干燥等“卡脖子”技术，具备极强的议价能力和行业地位。",
            "优点：估值极具吸引力。不到 8 倍的 PE 与破净边缘的 PB，为格网交易策略提供了极厚的安全垫，下行空间有限。",
            "缺点：回款周期压力。作为工程类企业，受宏观经济及甲方资金链影响，应收账款计提压力始终是短期利润波动的风险点。",
            "缺点：周期性波动风险。实业产品（如尼龙 66）的价格受原油、煤炭等大宗原材料波动影响较大，利润稳定性逊于纯科技服务。",
            "缺点：市场偏见。资本市场长期将其视为“低估值建筑股”，实业化转型的估值重构（从 8x 向 15x 迈进）需要业绩持续兑现验证。",
        ],
        product_lines=[
            "化学工程业务：底盘。专注于石化、煤化工及环保工程，订单储备超 4000 亿，提供稳定的现金流与利润基石。",
            "实业新材料业务：皇冠明珠。以己二腈、尼龙 66、气凝胶为核心，2026 年进入产能全面放量期，是公司 PE 重估的核心动力。",
            "现代服务业：润滑剂。涵盖智慧司库、供应链金融及高端研发授权，毛利率高达 40% 左右，提升整体资本运营效率。",
        ],
    ),
}
