from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Company:
    """
    上市公司基本资料。

    用于描述上市公司的主体信息、管理层信息、
    注册信息以及公司业务信息。

    Company 只描述“公司是谁”，不负责描述：

        行情        → Quote
        股本        → CapitalStructure
        估值        → Valuation
        财务        → Financial
        行业        → Industry
        股东        → Shareholder
        新闻        → News
        公告        → Announcement

    数据来源可以来自：

        交易所
        巨潮资讯
        东方财富
        公司官网
        第三方数据服务
        爬虫

    上层业务统一使用 Company，
    不应该直接依赖具体数据源的数据结构。
    """

    # ==========================================================
    # 基础标识
    # ==========================================================

    symbol: str

    """
    股票代码。

    例如：

        600519.SH
        000001.SZ
    """

    company_name: Optional[str] = None

    """
    公司全称。

    例如：

        贵州茅台酒股份有限公司
    """

    short_name: Optional[str] = None

    """
    公司简称。

    例如：

        贵州茅台
    """

    # ==========================================================
    # 公司身份
    # ==========================================================

    unified_social_credit_code: Optional[str] = None

    """
    统一社会信用代码。
    """

    organization_code: Optional[str] = None

    """
    组织机构代码。

    如果数据源已经不再提供，
    可以保持 None。
    """

    registration_number: Optional[str] = None

    """
    工商注册号。
    """

    # ==========================================================
    # 公司管理层
    # ==========================================================

    chairman: Optional[str] = None

    """
    董事长。
    """

    legal_representative: Optional[str] = None

    """
    法定代表人。
    """

    general_manager: Optional[str] = None

    """
    总经理 / 总裁。
    """

    secretary: Optional[str] = None

    """
    董事会秘书。
    """

    financial_officer: Optional[str] = None

    """
    财务负责人 / CFO。

    如果数据源没有提供，可以为 None。
    """

    # ==========================================================
    # 公司注册信息
    # ==========================================================

    establishment_date: Optional[datetime] = None

    """
    公司成立日期。
    """

    registration_date: Optional[datetime] = None

    """
    工商登记日期。
    """

    registration_authority: Optional[str] = None

    """
    登记机关。
    """

    registered_capital: Optional[float] = None

    """
    注册资本。

    单位建议统一为：

        元
    """

    # ==========================================================
    # 地址
    # ==========================================================

    registered_address: Optional[str] = None

    """
    注册地址。
    """

    office_address: Optional[str] = None

    """
    办公地址。
    """

    postal_code: Optional[str] = None

    """
    邮政编码。
    """

    # ==========================================================
    # 联系方式
    # ==========================================================

    telephone: Optional[str] = None

    """
    公司联系电话。
    """

    fax: Optional[str] = None

    """
    公司传真。
    """

    email: Optional[str] = None

    """
    公司电子邮箱。
    """

    website: Optional[str] = None

    """
    公司官方网站。
    """

    # ==========================================================
    # 公司业务
    # ==========================================================

    business_scope: Optional[str] = None

    """
    工商登记经营范围。

    通常是一段较长的文本。
    """

    main_business: Optional[str] = None

    """
    主营业务。

    比 business_scope 更适合用于股票分析。

    例如：

        白酒生产与销售
    """

    products: Optional[str] = None

    """
    主要产品。

    例如：

        飞天茅台
        茅台1935
        王子酒
        迎宾酒
    """

    business_description: Optional[str] = None

    """
    公司业务简介。
    """

    company_description: Optional[str] = None

    """
    公司整体简介。

    可以来自：

        公司官网
        招股书
        数据服务商
        AI 整理
    """

    # ==========================================================
    # 上市信息
    # ==========================================================

    listing_date: Optional[datetime] = None

    """
    上市日期。
    """

    ipo_price: Optional[float] = None

    """
    首次公开发行价格。

    单位：

        元
    """

    ipo_market: Optional[str] = None

    """
    IPO 市场。

    例如：

        SSE
        SZSE
        BSE
    """

    # ==========================================================
    # 公司状态
    # ==========================================================

    company_status: Optional[str] = None

    """
    公司状态。

    例如：

        存续
        在业
        注销
        吊销
    """

    listed_status: Optional[str] = None

    """
    上市状态。

    例如：

        LISTED
        DELISTED
        SUSPENDED
    """

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    """
    数据来源标识。

    例如：

        cninfo
        sse
        szse
        eastmoney
        company_website
        crawler
    """

    source_name: Optional[str] = None

    """
    数据来源名称。

    例如：

        巨潮资讯
        上海证券交易所
        深圳证券交易所
        公司官网
        东方财富
    """

    # ==========================================================
    # 数据时间
    # ==========================================================

    fetched_at: Optional[datetime] = None

    """
    数据实际获取时间。
    """

    updated_at: Optional[datetime] = None

    """
    数据源显示的最后更新时间。

    注意：

        fetched_at = 我什么时候获取的

        updated_at = 数据本身什么时候更新的
    """

    # ==========================================================
    # 原始数据
    # ==========================================================

    raw_data: Optional[dict] = None

    """
    保存数据源原始数据。

    主要用于：

        调试
        数据清洗
        字段扩展
        数据源切换
        数据追溯

    正式生产环境可以根据存储策略决定
    是否保存完整 raw_data。
    """