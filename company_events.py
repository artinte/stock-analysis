from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class CompanyEvent:
    """定义单个公司重大事件的详细信息结构。"""

    date: str = field(
        metadata={"description": "事件发生的日期，建议格式为 'YYYY-MM-DD'"}
    )
    description: str = field(metadata={"description": "事件的简单描述"})
    url: str = field(metadata={"description": "引用的网页链接"})


@dataclass
class CompanyEvents:
    """用于记录和管理公司重大事件集合的类。"""

    company_name: str = field(metadata={"description": "公司名称，如 '士兰微电子'"})
    ticker: str = field(metadata={"description": "股票代码，如 '600460.SH'"})

    # 事件集合，存储 CompanyEvent 对象列表
    events: List[CompanyEvent] = field(
        default_factory=list,
        metadata={
            "description": "公司所有重大事件的列表，每个元素是一个 CompanyEvent 对象"
        },
    )


AllCompanyEvents = [
    CompanyEvents(
        company_name="士兰微电子",
        ticker="600460.SH",
        events=[
            CompanyEvent(
                date="2025.10.19",
                description="士兰微电子在厦门签约投资200亿元建设12英寸高端模拟集成电路芯片制造生产线。",
                url="https://example.com/silan-2023-q3-report",
            ),
        ],
    ),
]
