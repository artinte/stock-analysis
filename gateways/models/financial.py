from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Financial:
    """
    公司财务数据模型。


    描述上市公司某一个财务报告期的财务状态。


    数据来源：

        银河证券
        AkShare
        Tushare
        Wind
        东方财富
        同花顺


    数据流：

        Financial Data Provider
                |
                ↓
            Gateway
                |
                ↓
            Financial
                |
                ↓
        StockCenter
                |
        AI分析 / 财务评分 / 估值模型


    注意：

    Financial 描述财报数据。

    不包含：

        实时价格
        PE
        PB
        新闻
        行业

    """

    # ==========================================================
    # 基础信息
    # ==========================================================

    symbol: str

    report_date: Optional[str] = None
    """
    财报日期。

    例如:

        2025-12-31
    """

    report_type: Optional[str] = None
    """
    报告类型。


    示例:

        annual
        quarterly
        interim
    """

    period: Optional[str] = None
    """
    财务周期。


    示例:

        Q1
        Q2
        Q3
        FY
    """

    currency: Optional[str] = None
    """
    币种。

    CNY
    USD
    """

    # ==========================================================
    # 利润表 Income Statement
    # ==========================================================

    revenue: Optional[float] = None

    revenue_yoy: Optional[float] = None

    revenue_qoq: Optional[float] = None

    operating_profit: Optional[float] = None

    operating_profit_yoy: Optional[float] = None

    gross_profit: Optional[float] = None

    gross_margin: Optional[float] = None

    net_profit: Optional[float] = None

    net_profit_yoy: Optional[float] = None

    net_profit_qoq: Optional[float] = None

    net_profit_attributable: Optional[float] = None

    net_profit_attributable_yoy: Optional[float] = None

    non_recurring_net_profit: Optional[float] = None

    # ==========================================================
    # 盈利能力 Profitability
    # ==========================================================

    operating_margin: Optional[float] = None

    net_margin: Optional[float] = None

    roe: Optional[float] = None
    """
    净资产收益率。
    """

    roa: Optional[float] = None

    roic: Optional[float] = None

    # ==========================================================
    # 成长能力 Growth
    # ==========================================================

    revenue_growth: Optional[float] = None

    profit_growth: Optional[float] = None

    eps_growth: Optional[float] = None

    # ==========================================================
    # 资产负债表 Balance Sheet
    # ==========================================================

    total_assets: Optional[float] = None

    total_liabilities: Optional[float] = None

    total_equity: Optional[float] = None

    shareholders_equity: Optional[float] = None

    cash: Optional[float] = None

    cash_equivalent: Optional[float] = None

    accounts_receivable: Optional[float] = None

    receivable_turnover: Optional[float] = None

    inventory: Optional[float] = None

    inventory_turnover: Optional[float] = None

    fixed_assets: Optional[float] = None

    goodwill: Optional[float] = None

    # ==========================================================
    # 现金流 Cash Flow
    # ==========================================================

    operating_cash_flow: Optional[float] = None

    investing_cash_flow: Optional[float] = None

    financing_cash_flow: Optional[float] = None

    free_cash_flow: Optional[float] = None

    cash_flow_quality: Optional[float] = None
    """
    经营现金流 / 净利润

    判断利润含金量。
    """

    # ==========================================================
    # 每股指标 Per Share
    # ==========================================================

    eps: Optional[float] = None

    diluted_eps: Optional[float] = None

    book_value_per_share: Optional[float] = None

    operating_cash_flow_per_share: Optional[float] = None

    # ==========================================================
    # 财务健康 Financial Health
    # ==========================================================

    debt_to_asset_ratio: Optional[float] = None

    current_ratio: Optional[float] = None

    quick_ratio: Optional[float] = None

    interest_coverage: Optional[float] = None

    # ==========================================================
    # 股东回报 Shareholder Return
    # ==========================================================

    dividend: Optional[float] = None

    dividend_yield: Optional[float] = None

    payout_ratio: Optional[float] = None

    # ==========================================================
    # 审计信息 Audit
    # ==========================================================

    auditor: Optional[str] = None

    audit_opinion: Optional[str] = None
    """
    审计意见。


    示例:

        standard
        qualified
        adverse
    """

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None
    """
    数据来源。

    例如:

        yinhe
        akshare
        tushare
    """
