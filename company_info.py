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
        description="横店东磁被誉为“中国磁都”，是全球最大的永磁铁氧体和软磁材料生产基地。公司已成功构建“磁材+光伏+锂电”三轮驱动格局。作为横店集团旗下的旗舰上市公司，其经营风格极其稳健，财务指标长期保持“三低一高”（低负债、低库存、低成本、高周转）。\
        公司在保持磁性材料绝对领导地位的同时，深度垂直一体化布局光伏产业链，尤其在欧洲分布式光伏市场拥有极强的渠道品牌溢价。2025年后，公司从“激进扩张”转向“高质量经营”，通过大幅提高分红比例，正在从成长股向‘高股息价值股’进行赛道重塑。",
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
        websites={"official": "https://www.dmegc.com.cn/"},
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
}
