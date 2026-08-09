from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ArticleItem(BaseModel):
    source_name: str  # 数据源名称（如：央视财经）
    title: str  # 文章标题
    url: str  # 文章链接
    content: Optional[str] = ""
    summary: Optional[str] = ""  # 文章摘要/简介（可选，默认为空）

    category: str = ""  # 扩展分类
    tags: List[str] = Field(default_factory=list)  # 标签列表

    related_companies: List[str] = Field(default_factory=list)  # 关联公司列表（可选，默认为空）

    published_at: Optional[datetime] = None  # 文章发布时间（可选，默认为 None）
    fetched_at: datetime = Field(default_factory=datetime.now)  # 抓取时间
