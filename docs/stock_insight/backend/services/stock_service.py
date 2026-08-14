from .store import find_stock


def basic(keyword: str):
    stock = find_stock(keyword)
    if not stock:
        return None
    return {
        "code": stock["code"],
        "name": stock["name"],
        "full_name": stock["full_name"],
        "market": stock["market"],
        "board": stock["board"],
        "industry": stock["industry"],
        "listing_date": stock["listing_date"],
        "chairman": stock["chairman"],
        "general_manager": stock["general_manager"],
        "website": stock["website"],
        "description": stock["description"]
    }
