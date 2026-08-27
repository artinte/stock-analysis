from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Announcement:
    """
    上市公司公告。

    Announcement 只负责描述公告本身，
    不包含 AI 分析、情绪分析、重要程度等派生信息。

    例如：

        - 业绩预告
        - 业绩快报
        - 股东大会
        - 董事会决议
        - 重大合同
        - 股权变动
        - 回购
        - 增减持
        - 停复牌
        - 风险提示
        - 融资公告
        - 监管公告

    定期报告建议使用 FinancialReport。
    """

    # ==========================================================
    # 基础标识
    # ==========================================================

    symbol: str
    """股票代码，例如：600519.SH。"""

    title: str
    """公告标题。"""

    announcement_id: Optional[str] = None
    """公告唯一 ID。"""

    # ==========================================================
    # 公告分类
    # ==========================================================

    category: Optional[str] = None
    """
    公告一级分类。

    例如：

        定期报告
        业绩公告
        公司治理
        股权变动
        重大事项
        风险提示
        融资公告
        监管公告
        其他
    """

    sub_category: Optional[str] = None
    """
    公告二级分类。

    例如：

        业绩预告
        业绩快报
        股东大会
        董事会决议
        回购
        增持
        减持
        重大合同
    """

    # ==========================================================
    # 时间
    # ==========================================================

    publish_time: Optional[datetime] = None
    """公告发布时间。"""

    announcement_date: Optional[datetime] = None
    """公告日期。"""

    # ==========================================================
    # 内容
    # ==========================================================

    content: Optional[str] = None
    """公告正文。"""

    summary: Optional[str] = None
    """
    公告摘要。

    可以保存数据源提供的原始摘要。
    AI 生成的摘要建议放入 AnnouncementAnalysis。
    """

    # ==========================================================
    # 原始文档
    # ==========================================================

    url: Optional[str] = None
    """公告原始网页地址。"""

    pdf_url: Optional[str] = None
    """公告 PDF 地址。"""

    # ==========================================================
    # 来源
    # ==========================================================

    source: Optional[str] = None
    """
    数据来源代码。

    例如：

        cninfo
        sse
        szse
        eastmoney
        sina
        xueqiu
        crawler
    """

    source_name: Optional[str] = None
    """
    数据源显示名称。

    例如：

        巨潮资讯
        上海证券交易所
        深圳证券交易所
        东方财富
    """

    # ==========================================================
    # 文件信息
    # ==========================================================

    file_name: Optional[str] = None
    """原始公告文件名。"""

    file_size: Optional[int] = None
    """原始文件大小，单位 Byte。"""

    # ==========================================================
    # 元数据
    # ==========================================================

    fetched_at: Optional[datetime] = None
    """数据实际抓取时间。"""

    raw_data: Optional[dict] = None
    """
    数据源原始数据。

    用于：

        - 调试
        - 数据清洗
        - 数据源适配
        - 字段补充
        - 数据质量追踪
    """

    # ==========================================================
    # Display
    # ==========================================================

    def display(self) -> None:
        """
        平铺显示公告信息。

        显示规则：

            1. 所有字段固定显示
            2. 空值统一显示 "-"
            3. 字段顺序固定
            4. 时间统一为 YYYY-MM-DD HH:MM:SS
            5. 文件大小自动格式化
            6. raw_data 不展开，只显示是否存在
        """

        def fmt(value: object) -> str:
            """格式化普通字段。"""

            if value is None:
                return "-"

            if isinstance(value, str):
                value = value.strip()

                if not value:
                    return "-"

            return str(value)

        def fmt_datetime(
            value: Optional[datetime],
        ) -> str:
            """格式化时间。"""

            if value is None:
                return "-"

            return value.strftime("%Y-%m-%d %H:%M:%S")

        def fmt_file_size(
            value: Optional[int],
        ) -> str:
            """格式化文件大小。"""

            if value is None or value < 0:
                return "-"

            size = float(value)

            if size < 1024:
                return f"{int(size):,} Bytes"

            size /= 1024

            if size < 1024:
                return f"{size:.2f} KB"

            size /= 1024

            if size < 1024:
                return f"{size:.2f} MB"

            size /= 1024

            if size < 1024:
                return f"{size:.2f} GB"

            size /= 1024

            return f"{size:.2f} TB"

        # ======================================================
        # 基础信息
        # ======================================================

        print(f"公告: {fmt(self.title)}")
        print(f"公告 ID: {fmt(self.announcement_id)}")
        print(f"股票代码: {fmt(self.symbol)}")

        # ======================================================
        # 分类
        # ======================================================

        print(f"公告分类: {fmt(self.category)}")
        print(f"公告子分类: {fmt(self.sub_category)}")

        # ======================================================
        # 时间
        # ======================================================

        print(f"发布时间: " f"{fmt_datetime(self.publish_time)}")

        print(f"公告日期: " f"{fmt_datetime(self.announcement_date)}")

        # ======================================================
        # 内容
        # ======================================================

        print(f"摘要: {fmt(self.summary)}")
        print(f"正文: {fmt(self.content)}")

        # ======================================================
        # 原始文档
        # ======================================================

        print(f"公告链接: {fmt(self.url)}")
        print(f"PDF 链接: {fmt(self.pdf_url)}")

        # ======================================================
        # 数据来源
        # ======================================================

        print(f"数据源: {fmt(self.source)}")
        print(f"数据源名称: {fmt(self.source_name)}")

        # ======================================================
        # 文件信息
        # ======================================================

        print(f"文件名: {fmt(self.file_name)}")

        print(f"文件大小: " f"{fmt_file_size(self.file_size)}")

        # ======================================================
        # 元数据
        # ======================================================

        print(f"抓取时间: " f"{fmt_datetime(self.fetched_at)}")

        print(f"原始数据: " f"{'有' if self.raw_data else '-'}")
