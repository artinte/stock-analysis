/* =========================================================
   股票详情页
========================================================= */


let currentSymbol = "600519";


/* =========================================================
   模拟股票数据
   后面直接替换成 API
========================================================= */

const STOCK_DETAIL_DATA = {

    "600519": {

        name: "贵州茅台",

        symbol: "600519.SH",

        price: "1,438.00",

        change: "+16.48",

        changePercent: "+1.16%",

        industry: [
            "白酒",
            "食品饮料",
            "沪市"
        ]

    },


    "300750": {

        name: "宁德时代",

        symbol: "300750.SZ",

        price: "312.50",

        change: "-2.64",

        changePercent: "-0.84%",

        industry: [
            "新能源",
            "电池",
            "创业板"
        ]

    },


    "601117": {

        name: "中国化学",

        symbol: "601117.SH",

        price: "9.86",

        change: "+0.31",

        changePercent: "+3.25%",

        industry: [
            "建筑工程",
            "化工",
            "沪市"
        ]

    },


    "300308": {

        name: "中际旭创",

        symbol: "300308.SZ",

        price: "198.60",

        change: "+5.32",

        changePercent: "+2.75%",

        industry: [
            "通信设备",
            "光模块",
            "创业板"
        ]

    }

};



/* =========================================================
   初始化
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const params =
            new URLSearchParams(
                window.location.search
            );

        const symbol =
            params.get("symbol");


        if (symbol) {

            currentSymbol =
                symbol.replace(
                    /[^0-9]/g,
                    ""
                );

        }


        loadStock(currentSymbol);

        bindResearchTabs();

        updateFavoriteState();

    }
);



/* =========================================================
   加载股票
========================================================= */

function loadStock(symbol) {

    const stock =
        STOCK_DETAIL_DATA[symbol]
        || STOCK_DETAIL_DATA["600519"];


    document.title =
        `${stock.name} ${stock.symbol} - STOCK LAB`;


    const name =
        document.getElementById("stockName");

    const code =
        document.getElementById("stockSymbol");

    const price =
        document.getElementById("currentPrice");

    const change =
        document.getElementById("priceChange");


    if (name) {

        name.textContent =
            stock.name;

    }


    if (code) {

        code.textContent =
            stock.symbol;

    }


    if (price) {

        price.textContent =
            stock.price;

    }


    if (change) {

        change.innerHTML =
            `${stock.change}
             <span>
                ${stock.changePercent}
             </span>`;

        change.classList.remove(
            "positive",
            "negative"
        );


        if (
            stock.change.startsWith("-")
        ) {

            change.classList.add(
                "negative"
            );

        } else {

            change.classList.add(
                "positive"
            );

        }

    }


    const industry =
        document.querySelector(
            ".stock-industry"
        );


    if (industry) {

        industry.innerHTML =
            stock.industry
                .map(
                    item =>
                        `<span>${item}</span>`
                )
                .join("");

    }

}



/* =========================================================
   Tab
========================================================= */

function bindResearchTabs() {

    const tabs =
        document.querySelectorAll(
            "#researchTabs button"
        );


    tabs.forEach(tab => {

        tab.addEventListener(
            "click",
            () => {

                const target =
                    tab.dataset.target;


                switchSection(
                    target
                );

            }
        );

    });

}



/* =========================================================
   切换模块
========================================================= */

function switchSection(sectionId) {

    const sections =
        document.querySelectorAll(
            ".research-section"
        );


    sections.forEach(section => {

        section.classList.remove(
            "active"
        );

    });


    const target =
        document.getElementById(
            sectionId
        );


    if (target) {

        target.classList.add(
            "active"
        );

    }


    const tabs =
        document.querySelectorAll(
            "#researchTabs button"
        );


    tabs.forEach(tab => {

        tab.classList.toggle(
            "active",
            tab.dataset.target === sectionId
        );

    });


    window.scrollTo({

        top:
            document.querySelector(
                "#researchTabs"
            ).offsetTop - 20,

        behavior: "smooth"

    });

}



/* =========================================================
   AI
========================================================= */

function scrollToAI() {

    switchSection("ai");

}



/* =========================================================
   自选股
========================================================= */

function toggleFavorite() {

    const key =
        `stock_favorite_${currentSymbol}`;


    const current =
        localStorage.getItem(key)
        === "true";


    localStorage.setItem(
        key,
        String(!current)
    );


    updateFavoriteState();

}



function updateFavoriteState() {

    const button =
        document.getElementById(
            "favoriteButton"
        );


    if (!button) {

        return;

    }


    const key =
        `stock_favorite_${currentSymbol}`;


    const favorite =
        localStorage.getItem(key)
        === "true";


    button.textContent =
        favorite
            ? "★ 已自选"
            : "☆ 自选";

}



/* =========================================================
   返回股票中心
========================================================= */

function goBackStock() {

    window.location.href =
        "./";

}



/* =========================================================
   首页
========================================================= */

function goHome() {

    window.location.href =
        "../";

}



/* =========================================================
   页面导航
========================================================= */

function navigatePage(page) {

    const routes = {

        market: "../",

        stock: "./",

        news: "../news/",

        research: "../research/",

        trade: "../trade/",

        tools: "../tools/",

        document: "../document/"

    };


    if (routes[page]) {

        window.location.href =
            routes[page];

    }

}