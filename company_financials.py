from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class CompanyFinancials:
    company_name: str = field(metadata={"description": "公司名称，如 '亨通光电'"})
    ticker: str = field(metadata={"description": "股票代码，如 '600487'"})

    financial_data: Dict[str, Dict[str, float]] = field(
        default_factory=dict, metadata={"description": "按 '年-季度' 键存储的财务数据"}
    )


AllCompanyFinancials = [
    CompanyFinancials(
        company_name="亨通光电",
        ticker="600487",
        financial_data={
            # 2020
            "2020-Q1": {"revenue": 5945538302.51, "operating_profit": 233450460.64},
            "2020-Q2": {"revenue": 15470491069.99, "operating_profit": 443267090.08},
            "2020-Q3": {"revenue": 25364191643.18, "operating_profit": 873869993.78},
            "2020-Q4": {"revenue": 32384143494.70, "operating_profit": 1061758600.35},
            # 2021
            "2021-Q1": {"revenue": 6973749322.20, "operating_profit": 264134611.98},
            "2021-Q2": {"revenue": 18057224398.99, "operating_profit": 671082260.07},
            "2021-Q3": {"revenue": 29811867174.3, "operating_profit": 1315709725.85},
            "2021-Q4": {"revenue": 41271165065.64, "operating_profit": 1436301700.64},
            # 2022
            "2022-Q1": {"revenue": 9351601986.74, "operating_profit": 344050462.45},
            "2022-Q2": {"revenue": 22105964944.29, "operating_profit": 860106680.88},
            "2022-Q3": {"revenue": 33860607719.6, "operating_profit": 1419589919.12},
            "2022-Q4": {"revenue": 46463983638.92, "operating_profit": 1583539680.76},
            # 2023
            "2023-Q1": {"revenue": 10866810879.68, "operating_profit": 395053122.56},
            "2023-Q2": {"revenue": 23177117395.42, "operating_profit": 1249478580.24},
            "2023-Q3": {"revenue": 35101445831.21, "operating_profit": 1803880261.16},
            "2023-Q4": {"revenue": 47621743263.10, "operating_profit": 2153605330.12},
            # 2024
            "2024-Q1": {"revenue": 11784838907.31, "operating_profit": 513074864.08},
            "2024-Q2": {"revenue": 26614309370.63, "operating_profit": 1609319316.19},
            "2024-Q3": {"revenue": 42399340197.21, "operating_profit": 2314805476.78},
            "2024-Q4": {"revenue": 59984212421.78, "operating_profit": 2768821523.55},
            # 2025
            "2025-Q1": {"revenue": 13267951777.19, "operating_profit": 556783362.25},
            "2025-Q2": {"revenue": 32048563674.39, "operating_profit": 1858672275.21},
            "2025-Q3": {"revenue": 49620509007.93, "operating_profit": 2375820977.60},
        },
    ),
    CompanyFinancials(
        company_name="豪威集团",
        ticker="603501",
        financial_data={
            # 2024
            "2024-Q1": {"revenue": 5643808881.30, "operating_profit": 557792077.38},
            # 2025
            "2025-Q1": {"revenue": 6472102098.40, "operating_profit": 865970220.63},
            "2025-Q2": {"revenue": 13955815139.72, "operating_profit": 2192049914.71},
            "2025-Q3": {"revenue": 21782627742.87, "operating_profit": 3210212165.01},
        },
    ),
    CompanyFinancials(
        company_name="瑞芯微",
        ticker="603893",
        financial_data={
            # 2018
            "2018-Q4": {"revenue": 1270895141.80, "operating_profit": 192156232.16},
            # 2019
            "2019-Q1": {"revenue": 219329329.87, "operating_profit": 7074843.07},
            "2019-Q2": {"revenue": 574155761.55, "operating_profit": 66009452.50},
            "2019-Q3": {"revenue": 939560149.62, "operating_profit": 126866044.76},
            "2019-Q4": {"revenue": 1407725738.37, "operating_profit": 204707014.67},
            # 2020
            "2020-Q1": {"revenue": 270779433.25, "operating_profit": 31888190.97},
            "2020-Q2": {"revenue": 674039118.15, "operating_profit": 93027203.54},
            "2020-Q3": {"revenue": 1225454067.40, "operating_profit": 188609526.44},
            "2020-Q4": {"revenue": 1863387214.10, "operating_profit": 319972560.66},
            # 2021
            "2021-Q1": {"revenue": 564992405.58, "operating_profit": 111661341.20},
            "2021-Q2": {"revenue": 1378414625.95, "operating_profit": 264850884.85},
            "2021-Q3": {"revenue": 2057016145.66, "operating_profit": 407699774.83},
            "2021-Q4": {"revenue": 2718602121.55, "operating_profit": 601778469.15},
            # 2022
            "2022-Q1": {"revenue": 542930344.84, "operating_profit": 84146041.84},
            "2022-Q2": {"revenue": 1241846802.41, "operating_profit": 272286368.12},
            "2022-Q3": {"revenue": 1570287429.37, "operating_profit": 275988735.06},
            "2022-Q4": {"revenue": 2029675088.24, "operating_profit": 297427269.93},
            # 2023
            "2023-Q1": {"revenue": 329365990.64, "operating_profit": -18378664.30},
            "2023-Q2": {"revenue": 852643448.14, "operating_profit": 24799813.66},
            "2023-Q3": {"revenue": 1454536318.10, "operating_profit": 77316426.84},
            "2023-Q4": {"revenue": 2134522147.19, "operating_profit": 134885044.41},
            # 2024
            "2024-Q1": {"revenue": 543077768.88, "operating_profit": 67649705.21},
            "2024-Q2": {"revenue": 1248602239.84, "operating_profit": 182772073.78},
            "2024-Q3": {"revenue": 2159606597.14, "operating_profit": 351709019.93},
            "2024-Q4": {"revenue": 3136370678.42, "operating_profit": 594862210.27},
            # 2025
            "2025-Q1": {"revenue": 884962635.69, "operating_profit": 209479446.98},
            "2025-Q2": {"revenue": 2045843090.62, "operating_profit": 531146082.91},
            "2025-Q3": {"revenue": 3141381494.70, "operating_profit": 779576888.33},
        },
    ),
    CompanyFinancials(
        company_name="士兰微",
        ticker="600460.SH",
        financial_data={
            # 2023
            "2023-Q3": {"revenue": 6899209774.84, "operating_profit": -189252469.75},
            "2023-Q4": {"revenue": 9339537962.75, "operating_profit": -35785761.01},
            # 2024
            "2024-Q1": {"revenue": 2464973745.58, "operating_profit": -15277738.16},
            "2024-Q2": {"revenue": 5273814511.21, "operating_profit": -24923948.66},
            "2024-Q3": {"revenue": 8163254166.56, "operating_profit": 28878343.70},
            "2024-Q4": {"revenue": 11220869038.95, "operating_profit": 219867848.47},
            # 2025
            "2025-Q1": {"revenue": 2999841284.77, "operating_profit": 148565355.87},
            "2025-Q2": {"revenue": 6335766076.23, "operating_profit": 264797685.99},
            "2025-Q3": {"revenue": 9712845638.51, "operating_profit": 349065347.25},
        },
    ),
    CompanyFinancials(
        company_name="比亚迪",
        ticker="",
    ),
    CompanyFinancials(
        company_name="中国核电",
        ticker="",
    ),
    CompanyFinancials(
        company_name="广合科技",
        ticker="001389.SZ",
        financial_data={
            # 2023
            "2023-Q4": {"revenue": 2678270258.07, "operating_profit": 414685735.07},
            # 2024
            "2024-Q1": {"revenue": 784357516.96, "operating_profit": 145086124.36},
            "2024-Q2": {"revenue": 1705583527.93, "operating_profit": 319387115.14},
            "2024-Q3": {"revenue": 2680659839.63, "operating_profit": 492495287.90},
            "2024-Q4": {"revenue": 3734284609.80, "operating_profit": 676100402.24},
            # 2025
            "2025-Q1": {"revenue": 1116984677.76, "operating_profit": 240371973.05},
            "2025-Q2": {"revenue": 2424753430.8, "operating_profit": 491583351.57},
            "2025-Q3": {"revenue": 3835129024.17, "operating_profit": 723819563.55},
        },
    ),
    CompanyFinancials(
        company_name="北方华创",
        ticker="002371.SZ",
        financial_data={
            "2024-Q1": {"revenue": 5950568399.86, "operating_profit": 1138817830.60},
            "2024-Q2": {"revenue": 12463584943.88, "operating_profit": 2790294946.72},
            "2024-Q3": {"revenue": 20532065958.75, "operating_profit": 4467785189.44},
            "2024-Q4": {"revenue": 29838069162.26, "operating_profit": 5621189109.03},
            # 2025
            "2025-Q1": {"revenue": 8206029208.8, "operating_profit": 1580707286.38},
            "2025-Q2": {"revenue": 16141546184.74, "operating_profit": 3207978523.58},
            "2025-Q3": {"revenue": 27301379656.81, "operating_profit": 5130342602.70},
        },
    ),
]
