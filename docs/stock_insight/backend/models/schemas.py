from typing import Any, Dict, List
from pydantic import BaseModel

class SearchItem(BaseModel):
    code: str
    name: str
    industry: str

class ModuleResponse(BaseModel):
    code: str
    module: str
    data: Dict[str, Any]
