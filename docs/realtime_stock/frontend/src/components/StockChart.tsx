import {
  useMarketStore,
} from "../stores/market";

export default function StockHeader() {
  const asset =
    useMarketStore(
      (state) =>
        state.currentAsset
    );

  const quote =
    useMarketStore(
      (state) =>
        state.quote
    );

  const watchlist =
    useMarketStore(
      (state) =>
        state.watchlist
    );

  const toggleWatchlist =
    useMarketStore(
      (state) =>
        state.toggleWatchlist
    );

  if (!quote) {
    return (
      <section className="stock-header">
        <div className="stock-loading">
          正在加载行情...
        </div>
      </section>
    );
  }

  const positive =
    quote.change >= 0;

  const favorite =
    watchlist.some(
      (item) =>
        item.symbol ===
        asset.symbol
    );

  return (
    <section className="stock-header">
      <div className="stock-title">
        <div className="stock-name-row">
          <h1>
            {quote.name}
          </h1>

          {asset.type ===
            "stock" && (
            <button
              className={
                favorite
                  ? "favorite active"
                  : "favorite"
              }
              onClick={() =>
                toggleWatchlist(
                  asset
                )
              }
            >
              {favorite
                ? "★"
                : "☆"}
            </button>
          )}
        </div>

        <span className="stock-symbol">
          {quote.symbol}
        </span>
      </div>

      <div className="stock-price-block">
        <div className="stock-price">
          {quote.last_price.toFixed(
            2
          )}
        </div>

        <div
          className={
            positive
              ? "stock-change up"
              : "stock-change down"
          }
        >
          {positive ? "+" : ""}
          {quote.change.toFixed(2)}

          <span>
            {positive ? "+" : ""}
            {quote.change_percent.toFixed(
              2
            )}
            %
          </span>
        </div>
      </div>

      <div className="stock-mini-stats">
        <div>
          <span>今开</span>
          <strong>
            {quote.open.toFixed(2)}
          </strong>
        </div>

        <div>
          <span>最高</span>
          <strong>
            {quote.high.toFixed(2)}
          </strong>
        </div>

        <div>
          <span>最低</span>
          <strong>
            {quote.low.toFixed(2)}
          </strong>
        </div>

        <div>
          <span>昨收</span>
          <strong>
            {quote.prev_close.toFixed(
              2
            )}
          </strong>
        </div>
      </div>
    </section>
  );
}