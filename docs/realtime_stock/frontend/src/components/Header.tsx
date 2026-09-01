import SearchBox from "./SearchBox";

import {
  useMarketStore,
} from "../stores/market";

export default function Header() {
  const connected =
    useMarketStore(
      (state) =>
        state.connected
    );

  return (
    <header className="header">
      <div className="brand">
        <div className="brand-mark">
          S
        </div>

        <div className="brand-text">
          <strong>
            Stock Terminal
          </strong>

          <span>
            MARKET
          </span>
        </div>
      </div>

      <SearchBox />

      <div className="header-status">
        <span
          className={
            connected
              ? "status-dot online"
              : "status-dot"
          }
        />

        <span>
          {connected
            ? "实时连接"
            : "等待数据"}
        </span>

        <span className="market-time">
          A-SHARES
        </span>
      </div>
    </header>
  );
}