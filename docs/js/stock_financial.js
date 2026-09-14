/* =========================================================
   Stock Financial
========================================================= */

let financialData = null;

let financialPeriod = 8;

const financialCharts = {};


/* =========================================================
   Initialization
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initFinancialPage
);


function initFinancialPage() {

    const symbol = getStockSymbol();

    if (!symbol) {

        console.warn(
            "未找到股票 symbol"
        );

        return;

    }

    bindPeriodButtons();

    loadFinancial(symbol);
}


/* =========================================================
   Symbol
========================================================= */

function getStockSymbol() {

    const params =
        new URLSearchParams(
            window.location.search
        );

    return (
        params.get("symbol") ||
        params.get("code")
    );
}


/* =========================================================
   API
========================================================= */

async function loadFinancial(symbol) {

    try {

        const response = await fetch(
            `/api/stock/${encodeURIComponent(symbol)}/financial`
        );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }

        const result =
            await response.json();

        if (!result.success) {

            throw new Error(
                result.message ||
                "获取财务数据失败"
            );

        }

        financialData = result.data || {};

        renderFinancial();

    } catch (error) {

        console.error(
            "财务数据加载失败:",
            error
        );

        renderEmptyState();

    }
}


/* =========================================================
   Main Render
========================================================= */

function renderFinancial() {

    renderSummary();

    renderCharts();

    renderIncomeStatement();

    renderBalanceSheet();

    renderCashFlow();
}


/* =========================================================
   Summary
========================================================= */

function renderSummary() {

    const summary =
        financialData.summary || {};

    setText(
        "latestReportDate",
        formatPeriod(summary.report_date)
    );

    setValue(
        "financialRevenue",
        formatAmount(summary.revenue)
    );

    setValue(
        "financialProfit",
        formatAmount(summary.net_profit)
    );

    setValue(
        "operatingCashFlow",
        formatAmount(
            summary.operating_cash_flow
        )
    );

    setValue(
        "netAssets",
        formatAmount(summary.net_assets)
    );

    setValue(
        "grossMargin",
        formatPercent(summary.gross_margin)
    );

    setValue(
        "netMargin",
        formatPercent(summary.net_margin)
    );

    setValue(
        "roe",
        formatPercent(
            getLatestProfitability("roe")
        )
    );

    setValue(
        "debtRatio",
        formatPercent(
            getLatestTrend("debt_ratio")
        )
    );

    setText(
        "cashFlowStatus",
        getCashFlowStatus(
            summary.operating_cash_flow
        )
    );
}


/* =========================================================
   Charts
========================================================= */

function renderCharts() {

    const trend =
        getVisibleTrend();

    renderRevenueChart(trend);

    renderProfitChart(trend);

    renderCashFlowChart(trend);

    renderProfitabilityChart(trend);
}


/* =========================================================
   Revenue Chart
========================================================= */

function renderRevenueChart(data) {

    const values = data.map(
        item => toYiYuan(item.revenue)
    );

    if (!hasData(values)) {

        showChartEmpty(
            "revenueChart"
        );

        return;

    }

    hideChartEmpty(
        "revenueChart"
    );

    destroyChart("revenueChart");

    financialCharts.revenueChart =
        new Chart(
            document.getElementById(
                "revenueChart"
            ),
            {
                type: "line",

                data: {
                    labels: data.map(
                        item => item.period
                    ),

                    datasets: [
                        {
                            label: "营业收入",

                            data: values,

                            tension: 0.3,

                            fill: false,

                            borderWidth: 2,

                            pointRadius: 3
                        }
                    ]
                },

                options: chartOptions(
                    "亿元"
                )
            }
        );
}


/* =========================================================
   Profit Chart
========================================================= */

function renderProfitChart(data) {

    const values = data.map(
        item => toYiYuan(item.profit)
    );

    if (!hasData(values)) {

        showChartEmpty(
            "profitChart"
        );

        return;

    }

    hideChartEmpty(
        "profitChart"
    );

    destroyChart("profitChart");

    financialCharts.profitChart =
        new Chart(
            document.getElementById(
                "profitChart"
            ),
            {
                type: "line",

                data: {
                    labels: data.map(
                        item => item.period
                    ),

                    datasets: [
                        {
                            label: "归母净利润",

                            data: values,

                            tension: 0.3,

                            fill: false,

                            borderWidth: 2,

                            pointRadius: 3
                        }
                    ]
                },

                options: chartOptions(
                    "亿元"
                )
            }
        );
}


/* =========================================================
   Cash Flow Chart
========================================================= */

function renderCashFlowChart(data) {

    const values = data.map(
        item =>
            toYiYuan(
                item.operating_cash_flow
            )
    );

    if (!hasData(values)) {

        showChartEmpty(
            "cashFlowChart"
        );

        return;

    }

    hideChartEmpty(
        "cashFlowChart"
    );

    destroyChart("cashFlowChart");

    financialCharts.cashFlowChart =
        new Chart(
            document.getElementById(
                "cashFlowChart"
            ),
            {
                type: "line",

                data: {
                    labels: data.map(
                        item => item.period
                    ),

                    datasets: [
                        {
                            label: "经营现金流",

                            data: values,

                            tension: 0.3,

                            fill: false,

                            borderWidth: 2,

                            pointRadius: 3
                        }
                    ]
                },

                options: chartOptions(
                    "亿元"
                )
            }
        );
}


/* =========================================================
   Profitability Chart
========================================================= */

function renderProfitabilityChart(data) {

    const grossMargin =
        data.map(
            item => item.gross_margin
        );

    const netMargin =
        data.map(
            item => item.net_margin
        );

    if (
        !hasData(grossMargin) &&
        !hasData(netMargin)
    ) {

        showChartEmpty(
            "profitabilityChart"
        );

        return;

    }

    hideChartEmpty(
        "profitabilityChart"
    );

    destroyChart(
        "profitabilityChart"
    );

    financialCharts.profitabilityChart =
        new Chart(
            document.getElementById(
                "profitabilityChart"
            ),
            {
                type: "line",

                data: {
                    labels: data.map(
                        item => item.period
                    ),

                    datasets: [
                        {
                            label: "毛利率",

                            data: grossMargin,

                            tension: 0.3,

                            fill: false,

                            borderWidth: 2,

                            pointRadius: 3
                        },

                        {
                            label: "净利率",

                            data: netMargin,

                            tension: 0.3,

                            fill: false,

                            borderWidth: 2,

                            pointRadius: 3
                        }
                    ]
                },

                options: chartOptions(
                    "%"
                )
            }
        );
}


/* =========================================================
   Income Statement
========================================================= */

function renderIncomeStatement() {

    const data =
        financialData.income_statement || [];

    const body =
        document.getElementById(
            "incomeStatementBody"
        );

    if (!data.length) {

        body.innerHTML =
            emptyRow(10);

        return;

    }

    body.innerHTML =
        data.map(item => `
            <tr>

                <td>
                    ${escapeHtml(
                        item.period || "-"
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(item.revenue)
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.operating_cost
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.gross_profit
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.operating_profit
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.total_profit
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.net_profit
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.net_profit_attributable
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(item.ebitda)
                    )}
                </td>

                <td>
                    ${formatNumber(
                        item.eps
                    )}
                </td>

            </tr>
        `)
        .join("");
}


/* =========================================================
   Balance Sheet
========================================================= */

function renderBalanceSheet() {

    const data =
        financialData.balance_sheet || [];

    const body =
        document.getElementById(
            "balanceSheetBody"
        );

    if (!data.length) {

        body.innerHTML =
            emptyRow(10);

        return;

    }

    body.innerHTML =
        data.map(item => `
            <tr>

                <td>
                    ${escapeHtml(
                        item.period || "-"
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.total_assets
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(item.cash)
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.accounts_receivable
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(item.inventory)
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.fixed_assets
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.total_liabilities
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.short_term_debt
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.long_term_debt
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.shareholders_equity
                            ?? item.total_equity
                        )
                    )}
                </td>

            </tr>
        `)
        .join("");
}


/* =========================================================
   Cash Flow
========================================================= */

function renderCashFlow() {

    const data =
        financialData.cash_flow || [];

    const body =
        document.getElementById(
            "cashFlowBody"
        );

    if (!data.length) {

        body.innerHTML =
            emptyRow(10);

        return;

    }

    body.innerHTML =
        data.map(item => `
            <tr>

                <td>
                    ${escapeHtml(
                        item.period || "-"
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.operating_cash_flow
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.operating_cash_inflow
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.operating_cash_outflow
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.investing_cash_flow
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.capital_expenditure
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.financing_cash_flow
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.ending_cash_balance
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.net_change_in_cash
                        )
                    )}
                </td>

                <td>
                    ${formatAmount(
                        toYiYuan(
                            item.free_cash_flow
                        )
                    )}
                </td>

            </tr>
        `)
        .join("");
}


/* =========================================================
   Period
========================================================= */

function bindPeriodButtons() {

    document
        .querySelectorAll(
            ".period-button"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll(
                            ".period-button"
                        )
                        .forEach(item =>
                            item.classList.remove(
                                "active"
                            )
                        );

                    button.classList.add(
                        "active"
                    );

                    const value =
                        button.dataset.period;

                    financialPeriod =
                        value === "all"
                            ? "all"
                            : Number(value);

                    renderCharts();
                }
            );

        });
}


function getVisibleTrend() {

    const trend =
        financialData?.trend || [];

    const sorted = [
        ...trend
    ].sort(
        (a, b) =>
            String(
                a.report_date || ""
            ).localeCompare(
                String(
                    b.report_date || ""
                )
            )
    );

    if (financialPeriod === "all") {
        return sorted;
    }

    return sorted.slice(
        -financialPeriod
    );
}


/* =========================================================
   Helpers
========================================================= */

function getLatestTrend(field) {

    const data =
        financialData?.trend || [];

    if (!data.length) {
        return null;
    }

    return data[
        data.length - 1
    ]?.[field] ?? null;
}


function getLatestProfitability(field) {

    const data =
        financialData?.profitability || [];

    if (!data.length) {
        return null;
    }

    return data[
        data.length - 1
    ]?.[field] ?? null;
}


function getCashFlowStatus(value) {

    if (value === null || value === undefined) {
        return "—";
    }

    if (Number(value) > 0) {
        return "经营现金流为正";
    }

    if (Number(value) < 0) {
        return "经营现金流为负";
    }

    return "经营现金流为零";
}


function toYiYuan(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return null;
    }

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return null;
    }

    return number / 100000000;
}


function formatAmount(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toLocaleString(
        "zh-CN",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }
    );
}


function formatNumber(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return number.toFixed(2);
}


function formatPercent(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return `${number.toFixed(2)}%`;
}


function formatPeriod(value) {

    if (!value) {
        return "—";
    }

    const text =
        String(value);

    if (text.length !== 8) {
        return text;
    }

    const year =
        text.substring(0, 4);

    const month =
        text.substring(4, 6);

    const quarter = {
        "03": "Q1",
        "06": "Q2",
        "09": "Q3",
        "12": "Q4",
    }[month];

    return quarter
        ? `${year} ${quarter}`
        : text;
}


function hasData(values) {

    return values.some(
        value =>
            value !== null &&
            value !== undefined &&
            Number.isFinite(
                Number(value)
            )
    );
}


function chartOptions(unit) {

    return {
        responsive: true,

        maintainAspectRatio: false,

        interaction: {
            mode: "index",
            intersect: false,
        },

        plugins: {
            legend: {
                position: "bottom",
            },

            tooltip: {
                callbacks: {
                    label(context) {

                        const value =
                            context.parsed.y;

                        if (
                            value === null ||
                            value === undefined
                        ) {
                            return "—";
                        }

                        return `${context.dataset.label}: ${Number(value).toFixed(2)} ${unit}`;
                    }
                }
            }
        },

        scales: {

            x: {
                grid: {
                    display: false,
                }
            },

            y: {
                beginAtZero: false,

                ticks: {
                    callback(value) {
                        return `${value}${unit}`;
                    }
                }
            }
        }
    };
}


function destroyChart(id) {

    if (financialCharts[id]) {

        financialCharts[id].destroy();

        financialCharts[id] = null;
    }
}


function showChartEmpty(id) {

    const canvas =
        document.getElementById(id);

    if (canvas) {
        canvas.style.display = "none";
    }

    const empty =
        document.getElementById(
            `${id}Empty`
        );

    if (empty) {
        empty.style.display = "flex";
    }
}


function hideChartEmpty(id) {

    const canvas =
        document.getElementById(id);

    if (canvas) {
        canvas.style.display = "block";
    }

    const empty =
        document.getElementById(
            `${id}Empty`
        );

    if (empty) {
        empty.style.display = "none";
    }
}


function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent =
            value ?? "—";
    }
}


function setValue(id, value) {

    setText(
        id,
        value || "—"
    );
}


function emptyRow(colspan) {

    return `
        <tr>
            <td colspan="${colspan}">
                暂无财务数据
            </td>
        </tr>
    `;
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function renderEmptyState() {

    setText(
        "latestReportDate",
        "暂无数据"
    );

    [
        "financialRevenue",
        "financialProfit",
        "operatingCashFlow",
        "netAssets",
        "grossMargin",
        "netMargin",
        "roe",
        "debtRatio",
    ].forEach(id =>
        setText(id, "—")
    );

    [
        "incomeStatementBody",
        "balanceSheetBody",
        "cashFlowBody",
    ].forEach(id => {

        const element =
            document.getElementById(id);

        if (element) {
            element.innerHTML =
                emptyRow(10);
        }

    });
}