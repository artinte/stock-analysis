import {
  useEffect,
} from "react";

import {
  fetchMarketOverview,
} from "../services/api";

import {
  useMarketStore,
} from "../stores/market";

export default function MarketOverview() {
  const overview =
    useMarketStore(
      (state) =>
        state.marketOverview
    );

  const setMarketOverview =
    useMarketStore(
      (state) =>
        state.setMarketOverview
    );

  const setCurrentAsset =
    useMarketStore(
      (state) =>
        state.setCurrentAsset
    );

  useEffect(() => {
    fetchMarketOverview().then(
      setMarketOverview
    );
  }, [setMarketOverview]);

  if (!overview) {
    return (
      <section className="market-overview loading">
        <div>
          市场数据加载中...
        </div>
      </section>
    );
  }

  return (
    <section className="market-overview">
      <div className="market-cards">
        {overview.indices.map(
          (index) => {
            const quote =
              index.quote;

            const positive =
              quote.change >= 0;

            return (
              <button
                key={index.symbol}
                className="market-card"
                onClick={() =>
                  setCurrentAsset(
                    index
                  )
                }
              >
                <div className="market-card-top">
                  <span>
                    {index.name}
                  </span>

                  <span>
                    {positive
                      ? "↑"
                      : "↓"}
                  </span>
                </div>

                <div className="market-price">
                  {quote.last_price.toFixed(
                    2
                  )}
                </div>

                <div
                  className={
                    positive
                      ? "market-change up"
                      : "market-change down"
                  }
                >
                  {positive
                    ? "+"
                    : ""}
                  {quote.change.toFixed(
                    2
                  )}

                  <span>
                    {positive
                      ? "+"
                      : ""}
                    {quote.change_percent.toFixed(
                      2
                    )}
                    %
                  </span>
                </div>
              </button>
            );
          }
        )}
      </div>

      <div className="market-statistics">
        <div>
          <span>上涨</span>

          <strong>
            {
              overview.advancing_count
            }
          </strong>
        </div>

        <div>
          <span>下跌</span>

          <strong>
            {
              overview.declining_count
            }
          </strong>
        </div>

        <div>
          <span>平盘</span>

          <strong>
            {
              overview.unchanged_count
            }
          </strong>
        </div>

        <div>
          <span>涨停</span>

          <strong>
            {
              overview.limit_up_count
            }
          </strong>
        </div>

        <div>
          <span>跌停</span>

          <strong>
            {
              overview.limit_down_count
            }
          </strong>
        </div>
      </div>
    </section>
  );
}