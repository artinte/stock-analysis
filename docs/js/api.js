const API_BASE = "";


/**
 * 通用 GET
 */
async function apiGet(url) {

    const response = await fetch(`${API_BASE}${url}`);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}


/**
 * 通用 POST
 */
async function apiPost(url, data) {

    const response = await fetch(`${API_BASE}${url}`, {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(data)

    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}


/**
 * 股票搜索
 *
 * 后面接 Python：
 *
 * GET /api/stocks/search?q=600519
 */
async function searchStocks(keyword) {

    try {

        return await apiGet(
            `/api/stocks/search?q=${encodeURIComponent(keyword)}`
        );

    } catch {

        const mock = [

            {
                symbol: "601117",
                name: "中国化学"
            },

            {
                symbol: "600519",
                name: "贵州茅台"
            },

            {
                symbol: "300750",
                name: "宁德时代"
            }

        ];

        return mock.filter(item =>
            item.symbol.includes(keyword) ||
            item.name.includes(keyword)
        );
    }
}


/**
 * AI 对话
 *
 * 后面 Python 只需要提供：
 *
 * POST /api/ai/chat
 */
async function chatWithAI(message, context = {}) {

    try {

        return await apiPost(
            "/api/ai/chat",
            {
                message,
                context
            }
        );

    } catch {

        return {

            answer:
                `这是模拟 AI 回复。\n\n` +
                `你刚才的问题是：${message}\n\n` +
                `后续接入 Python AI 服务后，这里将返回真实的市场、` +
                `股票、财务、估值和行业分析结果。`

        };

    }
}