/* =========================================================
   全局状态
========================================================= */

let currentStock = null;

let currentMainPage = "market";

let currentStockTab = "overview";


/* =========================================================
   页面初始化
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    bindSearch();

    bindAIInput();

    switchMainPage("market");

});


/* =========================================================
   顶部主导航
========================================================= */

function switchMainPage(page) {

    currentMainPage = page;

    const pages = document.querySelectorAll(".main-page");

    pages.forEach(section => {
        section.hidden = true;
    });


    const targetMap = {

        "market": "marketPage",
        "stock": "stockPage",
        "news": "newsPage",
        "ai": "aiPage",
        "trade": "tradePage",
        "ai-chat": "aiChatPage",
        "tool": "toolPage",
    };


    const targetId = targetMap[page];

    if (!targetId) {
        return;
    }


    const target = document.getElementById(targetId);

    if (target) {
        target.hidden = false;
    }


    /*
     * AI 对话不属于顶部普通导航
     */
    const navPage =
        page === "ai-chat"
            ? "ai"
            : page;


    document.querySelectorAll(".nav-item").forEach(item => {

        item.classList.toggle(
            "active",
            item.dataset.page === navPage
        );

    });


    /*
     * 进入股票页但没有股票时显示空状态
     */
    if (page === "stock") {

        const empty =
            document.getElementById("emptyState");

        const detail =
            document.getElementById("stockDetail");

        if (currentStock) {

            empty.hidden = true;
            detail.hidden = false;

        } else {

            empty.hidden = false;
            detail.hidden = true;

        }

    }

}


/* =========================================================
   股票
========================================================= */

function openStock(symbol, name) {

    currentStock = {
        symbol,
        name
    };


    switchMainPage("stock");


    const empty =
        document.getElementById("emptyState");

    const detail =
        document.getElementById("stockDetail");


    empty.hidden = true;
    detail.hidden = false;


    document.getElementById("stockName").textContent =
        name;

    document.getElementById("stockCode").textContent =
        symbol;


    document.getElementById("stockSub").textContent =
        `${symbol} · A股 · 模拟行情`;


    /*
     * 模拟数据
     */

    const priceMap = {

        "601117": {
            price: "9.86",
            change: "+3.25%"
        },

        "600519": {
            price: "1,438.00",
            change: "+1.16%"
        },

        "300750": {
            price: "312.50",
            change: "-0.84%"
        }

    };


    const data =
        priceMap[symbol] || {
            price: "--",
            change: "--"
        };


    document.getElementById("stockPrice").textContent =
        data.price;


    const change =
        document.getElementById("stockChange");

    change.textContent =
        data.change;


    change.className =
        `stock-change ${data.change.startsWith("-")
            ? "negative"
            : "positive"
        }`;


    renderSummary();


    switchStockTab("overview");


    const context =
        document.getElementById("aiContextStock");

    if (context) {

        context.textContent =
            `${name} ${symbol}`;

    }

}


/* =========================================================
   股票摘要
========================================================= */

function renderSummary() {

    const container =
        document.getElementById("summaryCards");

    if (!container) {
        return;
    }


    container.innerHTML = `

        <div class="summary-item">
            <span>今开</span>
            <strong>9.55</strong>
        </div>

        <div class="summary-item">
            <span>最高</span>
            <strong>9.92</strong>
        </div>

        <div class="summary-item">
            <span>最低</span>
            <strong>9.48</strong>
        </div>

        <div class="summary-item">
            <span>成交额</span>
            <strong>18.32亿</strong>
        </div>

        <div class="summary-item">
            <span>换手率</span>
            <strong>2.84%</strong>
        </div>

    `;

}


/* =========================================================
   股票 Tab
========================================================= */

function switchStockTab(tab) {

    currentStockTab = tab;


    document.querySelectorAll(".stock-tab").forEach(button => {

        button.classList.toggle(
            "active",
            button.dataset.tab === tab
        );

    });


    const container =
        document.getElementById("moduleContent");

    if (!container) {
        return;
    }


    const stock =
        currentStock || {
            symbol: "--",
            name: "--"
        };


    const contentMap = {

        overview: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>公司概况</h2>
                        <span>COMPANY PROFILE</span>
                    </div>
                </div>

                <div style="padding:24px">
                    <p>
                        ${stock.name}（${stock.symbol}）
                        的基本信息将在后续接入数据源后自动加载。
                    </p>
                </div>
            </div>
        `,


        quote: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>行情</h2>
                        <span>QUOTE</span>
                    </div>
                </div>

                <div style="padding:24px">
                    行情与 K 线数据将在这里展示。
                </div>
            </div>
        `,


        financial: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>财务数据</h2>
                        <span>FINANCIAL</span>
                    </div>
                </div>

                <div style="padding:24px">
                    利润表、资产负债表、现金流量表、
                    财务指标将在这里展示。
                </div>
            </div>
        `,


        valuation: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>估值</h2>
                        <span>VALUATION</span>
                    </div>
                </div>

                <div style="padding:24px">
                    PE、PB、PS、股息率等估值数据将在这里展示。
                </div>
            </div>
        `,


        industry: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>行业</h2>
                        <span>INDUSTRY</span>
                    </div>
                </div>

                <div style="padding:24px">
                    行业分类、行业排名、行业景气度将在这里展示。
                </div>
            </div>
        `,


        etf: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>ETF</h2>
                        <span>ETF</span>
                    </div>
                </div>

                <div style="padding:24px">
                    相关 ETF 数据将在这里展示。
                </div>
            </div>
        `,


        index: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>指数</h2>
                        <span>INDEX</span>
                    </div>
                </div>

                <div style="padding:24px">
                    所属指数及指数权重将在这里展示。
                </div>
            </div>
        `,


        news: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>相关新闻</h2>
                        <span>NEWS</span>
                    </div>
                </div>

                <div style="padding:24px">
                    与 ${stock.name}
                    相关的新闻将在这里展示。
                </div>
            </div>
        `,


        announcement: `
            <div class="panel">
                <div class="panel-heading">
                    <div>
                        <h2>公司公告</h2>
                        <span>ANNOUNCEMENT</span>
                    </div>
                </div>

                <div style="padding:24px">
                    公司公告将在这里展示。
                </div>
            </div>
        `,


        ai: `
            <div class="ai-large-entry">
                <div>
                    <span class="ai-large-star">✦</span>

                    <div>
                        <h2>
                            AI 分析 ${stock.name}
                        </h2>

                        <p>
                            从基本面、财务、估值、行业和舆情多个维度分析。
                        </p>
                    </div>
                </div>

                <button onclick="analyzeCurrentStock()">
                    开始分析 →
                </button>
            </div>
        `

    };


    container.innerHTML =
        contentMap[tab] ||
        "<div>暂无数据</div>";

}


/* =========================================================
   当前股票 AI 分析
========================================================= */

function analyzeCurrentStock() {

    if (!currentStock) {
        switchMainPage("ai-chat");
        return;
    }


    switchMainPage("ai-chat");


    usePrompt(
        `请帮我全面分析 ${currentStock.symbol} ${currentStock.name}，包括基本面、财务、估值、行业和风险`
    );

}


/* =========================================================
   Search
========================================================= */

function bindSearch() {

    const input =
        document.getElementById("searchInput");

    const button =
        document.getElementById("searchBtn");


    if (!input) {
        return;
    }


    input.addEventListener(
        "input",
        debounce(async () => {

            const keyword =
                input.value.trim();

            if (!keyword) {
                hideSearchDropdown();
                return;
            }


            const results =
                await searchStocks(keyword);

            renderSearchResults(results);

        }, 200)
    );


    input.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {

                searchStock(
                    input.value.trim()
                );

            }

        }
    );


    if (button) {

        button.addEventListener(
            "click",
            () => {

                searchStock(
                    input.value.trim()
                );

            }
        );

    }

}


/* =========================================================
   搜索股票
========================================================= */

function searchStock(keyword) {

    if (!keyword) {
        return;
    }


    const map = {

        "601117": "中国化学",
        "中国化学": "中国化学",

        "600519": "贵州茅台",
        "贵州茅台": "贵州茅台",

        "300750": "宁德时代",
        "宁德时代": "宁德时代"

    };


    const name =
        map[keyword];


    if (name) {

        openStock(
            keyword.match(/^\d+$/)
                ? keyword
                : getSymbolByName(keyword),
            name
        );

    } else {

        /*
         * 当前先允许输入任意股票，
         * 后面由 Python API 返回真实数据。
         */

        openStock(
            keyword,
            `股票 ${keyword}`
        );

    }


    hideSearchDropdown();

}


/* =========================================================
   股票名称 -> 代码
========================================================= */

function getSymbolByName(name) {

    const map = {

        "中国化学": "601117",
        "贵州茅台": "600519",
        "宁德时代": "300750"

    };

    return map[name] || name;

}


/* =========================================================
   Search dropdown
========================================================= */

function renderSearchResults(results) {

    const dropdown =
        document.getElementById("searchDropdown");

    if (!dropdown) {
        return;
    }


    if (!results || results.length === 0) {

        dropdown.innerHTML = "";

        dropdown.style.display = "none";

        return;

    }


    dropdown.innerHTML =
        results.map(item => `

            <button
                style="
                    width:100%;
                    padding:10px 12px;
                    display:flex;
                    justify-content:space-between;
                    background:#fff;
                    border:0;
                    border-bottom:1px solid #eee;
                    text-align:left;
                    cursor:pointer;
                "
                onclick="openStock('${item.symbol}','${item.name}')"
            >

                <strong>
                    ${item.name}
                </strong>

                <span
                    style="
                        color:#969da7;
                        font-size:11px;
                    "
                >
                    ${item.symbol}
                </span>

            </button>

        `).join("");


    dropdown.style.display = "block";

}


function hideSearchDropdown() {

    const dropdown =
        document.getElementById("searchDropdown");

    if (dropdown) {
        dropdown.style.display = "none";
    }

}


/* =========================================================
   AI
========================================================= */

function bindAIInput() {

    const input =
        document.getElementById("aiInput");

    if (!input) {
        return;
    }


    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendAIMessage();

            }

        }
    );


    input.addEventListener(
        "input",
        () => {

            input.style.height = "auto";

            input.style.height =
                Math.min(
                    input.scrollHeight,
                    120
                ) + "px";

        }
    );

}


/* =========================================================
   AI 快捷问题
========================================================= */

function usePrompt(prompt) {

    switchMainPage("ai-chat");


    const input =
        document.getElementById("aiInput");

    if (!input) {
        return;
    }


    input.value = prompt;

    input.focus();

}


/* =========================================================
   发送 AI
========================================================= */

async function sendAIMessage() {

    const input =
        document.getElementById("aiInput");

    const container =
        document.getElementById("chatMessages");


    if (!input || !container) {
        return;
    }


    const message =
        input.value.trim();


    if (!message) {
        return;
    }


    appendMessage(
        "user",
        message
    );


    input.value = "";
    input.style.height = "auto";


    const loading =
        appendMessage(
            "ai",
            "正在分析..."
        );


    try {

        const result =
            await chatWithAI(
                message,
                {
                    stock: currentStock
                }
            );


        loading.remove();


        appendMessage(
            "ai",
            result.answer ||
            "暂时没有获得 AI 返回结果。"
        );


    } catch (error) {

        loading.remove();

        appendMessage(
            "ai",
            "AI 服务暂时不可用，请稍后再试。"
        );

    }

}


/* =========================================================
   添加消息
========================================================= */

function appendMessage(type, text) {

    const container =
        document.getElementById("chatMessages");


    const message =
        document.createElement("div");


    message.className =
        `message ${type === "ai" ? "ai-message" : "user-message"}`;


    if (type === "ai") {

        message.innerHTML = `

            <div class="message-avatar">
                ✦
            </div>

            <div class="message-content-wrap">

                <div class="message-name">
                    AI 投研助手
                </div>

                <div class="message-content">
                    ${formatAIText(text)}
                </div>

            </div>

        `;

    } else {

        message.innerHTML = `

            <div class="message-content-wrap">

                <div class="message-name">
                    你
                </div>

                <div class="message-content">
                    ${escapeHTML(text)}
                </div>

            </div>

        `;

    }


    container.appendChild(message);


    container.scrollTop =
        container.scrollHeight;


    return message;

}


/* =========================================================
   AI 文本格式
========================================================= */

function formatAIText(text) {

    return escapeHTML(text)
        .replace(/\n/g, "<br>");

}


/* =========================================================
   HTML escape
========================================================= */

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


/* =========================================================
   清空 AI
========================================================= */

function clearAIChat() {

    const container =
        document.getElementById("chatMessages");

    if (!container) {
        return;
    }


    container.innerHTML = "";

    appendMessage(
        "ai",
        "对话已清空。你可以告诉我想研究哪只股票、哪个行业或当前市场。"
    );

}


/* =========================================================
   新建对话
========================================================= */

function newAIChat() {

    clearAIChat();

}


/* =========================================================
   Debounce
========================================================= */

function debounce(fn, delay) {

    let timer;

    return function (...args) {

        clearTimeout(timer);

        timer = setTimeout(
            () => fn.apply(this, args),
            delay
        );

    };

}

function renderIndex(index) {

    // 后端如果返回 000001.SH / 399001.SZ
    // 这里统一取前面的纯代码
    const code = String(index.code || index.symbol || '')
        .split('.')[0];

    const card = document.querySelector(
        `.market-index[data-index="${code}"]`
    );

    if (!card) {
        console.warn(
            `找不到指数卡片：${code}`,
            index
        );
        return;
    }

    // ============================================================
    // 价格
    // ============================================================

    const priceElement = card.querySelector('.index-price');

    if (priceElement) {

        priceElement.textContent =
            index.price ?? '--';

    }

    // ============================================================
    // 涨跌额和涨跌幅
    // ============================================================

    const values =
        card.querySelectorAll('.index-bottom span');

    if (values.length >= 2) {

        values[0].textContent =
            index.change ?? '--';

        values[1].textContent =
            index.changePercent ??
            index.change_percent ??
            '--';
    }

    // ============================================================
    // 涨跌颜色
    // ============================================================

    const change = Number(index.change);

    let className = '';

    if (!Number.isNaN(change)) {

        if (change > 0) {

            className = 'positive';

        } else if (change < 0) {

            className = 'negative';
        }
    }

    values.forEach(element => {

        element.classList.remove(
            'positive',
            'negative'
        );

        if (className) {

            element.classList.add(
                className
            );
        }
    });

    console.log(
        `✅ ${code} 指数页面已更新`,
        index
    );
}


// ============================================================
// 获取市场指数
// ============================================================

// ============================================================
// 获取市场指数
// ============================================================

async function loadIndices() {

    try {

        console.log(
            '📡 正在获取市场指数...'
        );

        const response = await fetch(
            '/api/indices'
        );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const result =
            await response.json();

        console.log(
            '📊 后端返回指数数据：',
            result
        );

        // ========================================================
        // 后端返回：
        //
        // {
        //     success: true,
        //     data: [...]
        // }
        // ========================================================

        if (!result.success) {

            throw new Error(
                result.message ||
                '获取指数数据失败'
            );
        }

        const indices = result.data;

        if (!Array.isArray(indices)) {

            throw new Error(
                '接口 data 不是数组'
            );
        }

        // ========================================================
        // 更新页面
        // ========================================================

        indices.forEach(index => {

            renderIndex(index);

        });

        console.log(
            `✅ 市场指数更新完成，共 ${indices.length} 个`
        );

    } catch (error) {

        console.error(
            '❌ 获取市场指数失败：',
            error
        );
    }
}

// ============================================================
// 页面加载完成后获取指数
// ============================================================

document.addEventListener(
    'DOMContentLoaded',
    () => {

        loadIndices();

    }
);