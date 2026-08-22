from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class IndustryStandard(str, Enum):
    """
    行业分类标准。

    不同数据源、研究机构使用的行业分类体系可能不同，
    因此不能简单地使用一个 industry 字段表示。
    """

    # 中证行业分类
    CSI = "csi"

    # 国民经济行业分类
    NATIONAL = "national"

    # 证监会行业分类
    CSRC = "csrc"

    # 申万行业分类
    SW = "sw"

    # Wind 行业分类
    WIND = "wind"

    # 自定义分类
    CUSTOM = "custom"


@dataclass(slots=True)
class IndustryNode:
    """
    行业分类节点。

    一个 IndustryNode 表示行业分类树中的一个节点。

    例如中证一级行业：

        信息技术

    二级：

        计算机

    三级：

        软件开发

    四级：

        应用软件
    """

    code: Optional[str] = None

    name: Optional[str] = None

    level: Optional[int] = None

    parent_code: Optional[str] = None

    parent_name: Optional[str] = None


@dataclass(slots=True)
class IndustryClassification:
    """
    单一行业分类体系下的股票行业信息。

    例如：

        standard = CSI

        level_1 = 信息技术
        level_2 = 计算机
        level_3 = 软件开发
        level_4 = 应用软件
    """

    standard: IndustryStandard

    level_1: Optional[IndustryNode] = None

    level_2: Optional[IndustryNode] = None

    level_3: Optional[IndustryNode] = None

    level_4: Optional[IndustryNode] = None


@dataclass(slots=True)
class Industry:
    """
    股票行业信息。

    一个股票可以同时属于多个行业分类体系。

    例如：

        贵州茅台

        中证：
            食品饮料
            饮料
            白酒

        国民经济行业：
            制造业
            酒、饮料和精制茶制造业

        证监会：
            制造业
            酒、饮料和精制茶制造业

        申万：
            食品饮料
            白酒

    注意：

    Industry 描述的是“股票与行业分类之间的关系”，
    而不是行业本身的详细资料。

    行业指数、行业成分股、行业估值等数据，
    后续可以单独设计 IndustryProfile。
    """

    symbol: str

    # ==========================================================
    # 行业分类
    # ==========================================================

    csi: Optional[IndustryClassification] = None

    national: Optional[IndustryClassification] = None

    csrc: Optional[IndustryClassification] = None

    sw: Optional[IndustryClassification] = None

    wind: Optional[IndustryClassification] = None

    custom: Optional[IndustryClassification] = None

    # ==========================================================
    # 当前主要行业
    # ==========================================================

    primary_standard: Optional[IndustryStandard] = None

    primary_industry: Optional[str] = None

    # ==========================================================
    # 数据来源
    # ==========================================================

    source: Optional[str] = None

    source_url: Optional[str] = None

    # ==========================================================
    # 扩展字段
    # ==========================================================

    extra: Optional[dict] = None
