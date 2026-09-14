async function loadBitcoinQuote() {

    const priceElement =
        document.getElementById("bitcoinPrice");

    const changeElement =
        document.getElementById("bitcoinChange");

    if (!priceElement || !changeElement) {
        console.error("找不到 Bitcoin DOM 元素");
        return;
    }

    try {

        const response = await fetch(
            "/api/crypto/quote/BTC/USDT"
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const result = await response.json();

        console.log("₿ Bitcoin API：", result);

        if (!result.success) {
            throw new Error(
                result.message || "获取 Bitcoin 行情失败"
            );
        }

        const quote = result.data;

        const price = Number(
            quote.lastPrice
        );

        const changePercent = Number(
            quote.changePercent
        );

        priceElement.textContent =
            `$${price.toLocaleString(
                "en-US",
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                }
            )}`;

        changeElement.textContent =
            `${changePercent >= 0 ? "+" : ""}${changePercent.toFixed(2)}%`;

        changeElement.classList.remove(
            "up",
            "down"
        );

        changeElement.classList.add(
            changePercent >= 0
                ? "up"
                : "down"
        );

    } catch (error) {

        console.error(
            "₿ Bitcoin 行情加载失败：",
            error
        );

        priceElement.textContent = "--";
        changeElement.textContent = "--";

        changeElement.classList.remove(
            "up",
            "down"
        );
    }
}


loadBitcoinQuote();