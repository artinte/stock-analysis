import type {
  Asset,
} from "../types/market";

import {
  useMarketStore,
} from "../stores/market";

const MARKET_ASSETS: Asset[] = [
  {
    symbol: "000001.SH",
    name: "上证指数",
    type: "index",
  },

  {
    symbol: "399001.SZ",
    name: "深证成指",
    type: "index",
  },

  {
    symbol: "399006.SZ",
    name: "创业板指",
    type: "index",
  },

  {
    symbol: "000688.SH",
    name: "科创50",
    type: "index",
  },

  {
    symbol: "000300.SH",
    name: "沪深300",
    type: "index",
  },

  {
    symbol: "000905.SH",
    name: "中证500",
    type: "index",
  },

  {
    symbol: "000852.SH",
    name: "中证1000",
    type: "index",
  },
];

export default function Sidebar() {
  const currentAsset =
    useMarketStore(
      (state) =>
        state.currentAsset
    );

  const watchlist =
    useMarketStore(
      (state) =>
        state.watchlist
    );

  const setCurrentAsset =
    useMarketStore(
      (state) =>
        state.setCurrentAsset
    );

  const toggleWatchlist =
    useMarketStore(
      (state) =>
        state.toggleWatchlist
    );

  const isWatchlisted = (
    symbol: string
  ) =>
    watchlist.some(
      (item) =>
        item.symbol === symbol
    );

  const renderAsset = (
    asset: Asset
  ) => {
    const active =
      currentAsset.symbol ===
      asset.symbol;

    return (
      <div
        key={asset.symbol}
        className={
          active
            ? "sidebar-item active"
            : "sidebar-item"
        }
      >
        <button
          className="sidebar-main"
          onClick={() =>
            setCurrentAsset(
              asset
            )
          }
        >
          <span className="asset-name">
            {asset.name}
          </span>

          <span className="asset-symbol">
            {asset.symbol}
          </span>
        </button>

        {asset.type ===
          "stock" && (
          <button
            className={
              isWatchlisted(
                asset.symbol
              )
                ? "watch-star selected"
                : "watch-star"
            }
            onClick={() =>
              toggleWatchlist(
                asset
              )
            }
          >
            {isWatchlisted(
              asset.symbol
            )
              ? "★"
              : "☆"}
          </button>
        )}
      </div>
    );
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <div className="sidebar-title">
          <span>自选</span>

          <span className="sidebar-count">
            {watchlist.length}
          </span>
        </div>

        <div className="sidebar-list">
          {watchlist.map(
            renderAsset
          )}
        </div>
      </div>

      <div className="sidebar-divider" />

      <div className="sidebar-section">
        <div className="sidebar-title">
          <span>市场</span>
        </div>

        <div className="sidebar-list">
          {MARKET_ASSETS.map(
            renderAsset
          )}
        </div>
      </div>

      <div className="sidebar-footer">
        <span>行情终端</span>

        <span>v0.1</span>
      </div>
    </aside>
  );
}