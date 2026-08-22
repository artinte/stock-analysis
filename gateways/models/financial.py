from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Financial:
    """
    公司财务数据。

    数据粒度由数据源决定，通常对应某一个财务报告期。
    """

    symbol: str

    report_date: Optional[str] = None

    report_type: Optional[str] = None

    # ==================== 利润表 ====================

    revenue: Optional[float] = None

    revenue_yoy: Optional[float] = None

    revenue_qoq: Optional[float] = None

    operating_profit: Optional[float] = None

    operating_profit_yoy: Optional[float] = None

    net_profit: Optional[float] = None

    net_profit_yoy: Optional[float] = None

    net_profit_qoq: Optional[float] = None

    net_profit_attributable: Optional[float] = None

    net_profit_attributable_yoy: Optional[float] = None

    non_recurring_net_profit: Optional[float] = None

    # ==================== 盈利能力 ====================

    gross_margin: Optional[float] = None

    operating_margin: Optional[float] = None

    net_margin: Optional[float] = None

    roe: Optional[float] = None

    roa: Optional[float] = None

    roic: Optional[float] = None

    # ==================== 资产负债表 ====================

    total_assets: Optional[float] = None

    total_liabilities: Optional[float] = None

    total_equity: Optional[float] = None

    shareholders_equity: Optional[float] = None

    cash: Optional[float] = None

    accounts_receivable: Optional[float] = None

    inventory: Optional[float] = None

    fixed_assets: Optional[float] = None

    goodwill: Optional[float] = None

    # ==================== 现金流 ====================

    operating_cash_flow: Optional[float] = None

    investing_cash_flow: Optional[float] = None

    financing_cash_flow: Optional[float] = None

    free_cash_flow: Optional[float] = None

    # ==================== 每股指标 ====================

    eps: Optional[float] = None

    book_value_per_share: Optional[float] = None

    operating_cash_flow_per_share: Optional[float] = None

    # ==================== 财务能力 ====================

    debt_to_asset_ratio: Optional[float] = None

    current_ratio: Optional[float] = None

    quick_ratio: Optional[float] = None

    interest_coverage: Optional[float] = None
