from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ArticleItem(BaseModel):
    source_name: str  # 数据源名称（如：央视财经）
    title: str  # 文章标题
    url: str  # 文章链接
    content: Optional[str] = ""
    summary: Optional[str] = ""  # 文章摘要/简介（可选，默认为空）
    category: str = ""  # 扩展分类
    fetched_at: datetime = Field(default_factory=datetime.now)  # 抓取时间