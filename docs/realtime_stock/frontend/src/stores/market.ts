import { create } from "zustand";

import type {
  Asset,
  Interval,
  Kline,
  MarketOverview,
  Quote,
} from "../types/market";

interface MarketState {
  currentAsset: Asset;

  quote: Quote | null;

  klines: Kline[];

  interval: Interval;

  watchlist: Asset[];

  marketOverview: MarketOverview | null;

  connected: boolean;

  setCurrentAsset: (asset: Asset) => void;

  setQuote: (quote: Quote) => void;

  setKlines: (klines: Kline[]) => void;

  setInterval: (interval: Interval) => void;

  setWatchlist: (assets: Asset[]) => void;

  toggleWatchlist: (asset: Asset) => void;

  setMarketOverview: (
    overview: MarketOverview
  ) => void;

  setConnected: (connected: boolean) => void;
}

const DEFAULT_ASSET: Asset = {
  symbol: "600519.SH",
  name: "贵州茅台",
  type: "stock",
};

const DEFAULT_WATCHLIST: Asset[] = [
  {
    symbol: "600519.SH",
    name: "贵州茅台",
    type: "stock",
  },
  {
    symbol: "601318.SH",
    name: "中国平安",
    type: "stock",
  },
  {
    symbol: "300308.SZ",
    name: "中际旭创",
    type: "stock",
  },
  {
    symbol: "688111.SH",
    name: "金山办公",
    type: "stock",
  },
  {
    symbol: "688981.SH",
    name: "中芯国际",
    type: "stock",
  },
];

export const useMarketStore =
  create<MarketState>((set) => ({
    currentAsset: DEFAULT_ASSET,

    quote: null,

    klines: [],

    interval: "5m",

    watchlist: DEFAULT_WATCHLIST,

    marketOverview: null,

    connected: false,

    setCurrentAsset: (asset) =>
      set({
        currentAsset: asset,
      }),

    setQuote: (quote) =>
      set({
        quote,
      }),

    setKlines: (klines) =>
      set({
        klines,
      }),

    setInterval: (interval) =>
      set({
        interval,
      }),

    setWatchlist: (watchlist) =>
      set({
        watchlist,
      }),

    toggleWatchlist: (asset) =>
      set((state) => {
        const exists = state.watchlist.some(
          (item) =>
            item.symbol === asset.symbol
        );

        if (exists) {
          return {
            watchlist:
              state.watchlist.filter(
                (item) =>
                  item.symbol !== asset.symbol
              ),
          };
        }

        return {
          watchlist: [
            ...state.watchlist,
            asset,
          ],
        };
      }),

    setMarketOverview: (
      marketOverview
    ) =>
      set({
        marketOverview,
      }),

    setConnected: (connected) =>
      set({
        connected,
      }),
  }));