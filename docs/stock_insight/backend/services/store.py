from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "mock" / "stocks.json"

with DATA_FILE.open("r", encoding="utf-8") as f:
    STOCKS = json.load(f)


def find_stock(keyword: str):
    keyword = keyword.strip()
    if keyword in STOCKS:
        return STOCKS[keyword]
    for item in STOCKS.values():
        if item["name"] == keyword or keyword in item["name"]:
            return item
    return None


def search_stocks(keyword: str):
    keyword = keyword.strip().lower()
    result = []
    for item in STOCKS.values():
        hay = f'{item["code"]} {item["name"]} {item["industry"]}'.lower()
        if keyword in hay:
            result.append({
                "code": item["code"],
                "name": item["name"],
                "industry": item["industry"]
            })
    return result[:20]
