
/* =========================================================
   STOCK LAB 全局页面导航
========================================================= */

function navigatePage(page) {

    const routes = {

        home: "../",
        market: "../?page=market",
        stock: "../?page=stock",
        news: "../news/",
        research: "../?page=research",
        trade: "../trade/",
        tools: "../tools/",
        document: "../document/"

    };

    const url = routes[page];

    if (!url) {

        console.error(
            `未知页面: ${page}`
        );

        return;

    }

    window.location.href = url;

}
