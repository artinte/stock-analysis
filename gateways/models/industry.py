from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from common.constants import IndustryStandard

@dataclass(slots=True)
class Industry:
    """股票所属行业。"""

    code: Optional[str] = None
    name: Optional[str] = None

    level_1: Optional[str] = None
    level_2: Optional[str] = None
    level_3: Optional[str] = None
    level_4: Optional[str] = None

    standard: Optional[IndustryStandard] = None

    source: Optional[str] = None

    def display(self) -> None:
        """打印行业信息。"""

        print(f"行业代码：{self.code or '-'}")
        print(f"行业名称：{self.name or '-'}")

        if self.standard is not None:
            print(f"分类标准：{self.standard.value}")
        else:
            print("分类标准：-")

        print(f"一级行业：{self.level_1 or '-'}")
        print(f"二级行业：{self.level_2 or '-'}")
        print(f"三级行业：{self.level_3 or '-'}")
        print(f"四级行业：{self.level_4 or '-'}")

        print(f"数据来源：{self.source or '-'}")
