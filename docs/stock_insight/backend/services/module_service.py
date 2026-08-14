from .store import find_stock

MODULES = [
    "overview", "market", "finance", "valuation", "industry", "etf", "index",
    "news", "notice", "shareholder", "dividend", "business", "events", "risk", "ai"
]


def module_data(keyword: str, module: str):
    stock = find_stock(keyword)
    if not stock:
        return None
    code = stock["code"]

    data = {
        "overview": {
            "cards": {
                "最新价": stock["price"], "涨跌幅": stock["change"],
                "总市值": stock["market_cap"], "PE-TTM": stock["pe_ttm"],
                "动态PE": stock["pe_dynamic"], "PB": stock["pb"],
                "股息率": stock["dividend_yield"], "ROE": stock["roe"]
            },
            "highlights": ["主营业务待接入", "公司事件待接入", "最新公告待接入", "新闻舆情待接入"]
        },
        "market": {
            "quote": {
                "最新价": stock["price"], "涨跌幅": stock["change"], "涨跌额": stock["change_amount"],
                "总市值": stock["market_cap"], "流通市值": stock["float_market_cap"]
            },
            "chart": [{"date": f"D{i:02d}", "price": round(stock["price"] * (0.96 + i * 0.003), 2)} for i in range(20)],
            "technical": ["MA5", "MA10", "MA20", "MA60", "MACD", "KDJ", "RSI", "BOLL"]
        },
        "finance": {
            "income": {"营业收入": stock["revenue"], "归母净利润": stock["net_profit"], "营收同比": stock["revenue_yoy"], "净利润同比": stock["profit_yoy"]},
            "quality": {"ROE": stock["roe"], "毛利率": "待接入", "净利率": "待接入", "经营现金流": "待接入", "资产负债率": "待接入"}
        },
        "valuation": {
            "current": {"PE-TTM": stock["pe_ttm"], "动态PE": stock["pe_dynamic"], "PB": stock["pb"], "PS": stock["ps"], "股息率": stock["dividend_yield"]},
            "history": {"1年分位": "待接入", "3年分位": "待接入", "5年分位": "待接入", "历史中位数": "待接入"}
        },
        "industry": {
            "classifications": {"申万": stock["industry"], "中证": "待接入", "中上协": "待接入", "证监会": "待接入"},
            "comparison": ["行业市值排名", "行业PE", "行业PB", "行业ROE", "行业营收增速"]
        },
        "etf": {"holdings": [], "note": "后续接入所有持有该股票的 ETF。"},
        "index": {"memberships": [], "note": "后续接入指数成分、权重、纳入/剔除记录。"},
        "news": {"items": [], "note": "后续接入公司新闻、行业新闻、政策新闻、海外新闻、舆情。"},
        "notice": {"items": [], "note": "后续接入交易所公告与财报公告。"},
        "shareholder": {"top10": [], "institutions": [], "note": "后续接入十大股东、基金、社保、QFII等。"},
        "dividend": {"records": [], "stats": {"连续分红": "待接入", "累计分红": "待接入"}},
        "business": {"main": ["主营业务待接入"], "segments": [], "regions": []},
        "events": {"timeline": []},
        "risk": {"items": ["商誉风险：待接入", "应收账款风险：待接入", "大股东减持：待接入", "诉讼与监管：待接入", "行业周期：待接入"]},
        "ai": {"company_profile": "AI分析接口预留。", "growth_logic": "待接入", "catalysts": [], "risks": [], "market_focus": []}
    }
    return {"code": code, "module": module, "data": data.get(module, {})}
