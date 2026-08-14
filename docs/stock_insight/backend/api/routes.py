from fastapi import APIRouter, HTTPException, Query
from services.store import search_stocks, find_stock
from services.stock_service import basic
from services.module_service import module_data, MODULES

router = APIRouter(prefix="/api")

@router.get("/search")
def search(q: str = Query("", min_length=1)):
    return search_stocks(q)

@router.get("/stock/{keyword}")
def stock(keyword: str):
    item = find_stock(keyword)
    if not item:
        raise HTTPException(404, "股票不存在")
    return item

@router.get("/stock/{keyword}/basic")
def stock_basic(keyword: str):
    item = basic(keyword)
    if not item:
        raise HTTPException(404, "股票不存在")
    return item

@router.get("/stock/{keyword}/module/{module}")
def stock_module(keyword: str, module: str):
    if module not in MODULES:
        raise HTTPException(404, "未知模块")
    data = module_data(keyword, module)
    if data is None:
        raise HTTPException(404, "股票不存在")
    return data
