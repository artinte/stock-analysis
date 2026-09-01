export type AssetType =
  | "stock"
  | "index"
  | "etf";

export type Interval =
  | "1m"
  | "5m"
  | "15m"
  | "30m"
  | "60m"
  | "1d"
  | "1w"
  | "1M";

export interface Asset {
  symbol: string;
  name: string;
  type: AssetType;
}

export interface Quote {
  symbol: string;
  name: string;
  timestamp: string;

  last_price: number;
  prev_close: number;

  open: number;
  high: number;
  low: number;

  change: number;
  change_percent: number;

  volume: number;
  amount: number;

  turnover: number;

  total_shares?: number;
  circulating_shares?: number;

  market_cap?: number;
  circulating_market_cap?: number;

  amplitude?: number;
  average_price?: number;
  volume_ratio?: number;

  limit_up?: number;
  limit_down?: number;

  status?: string;
  source?: string;
}

export interface Kline {
  symbol: string;
  timestamp: string;

  interval: Interval;

  open: number;
  high: number;
  low: number;
  close: number;

  volume: number;
  amount: number;
}

export interface MarketIndex extends Asset {
  quote: Quote;
}

export interface MarketOverview {
  timestamp: string;

  indices: MarketIndex[];

  advancing_count?: number;
  declining_count?: number;
  unchanged_count?: number;

  limit_up_count?: number;
  limit_down_count?: number;
}

export interface SearchResult {
  symbol: string;
  name: string;
  type: AssetType;
}

export interface WebSocketQuoteMessage {
  type: "quote";

  data: Quote;
}

export interface WebSocketQuotesMessage {
  type: "quotes";

  data: Quote[];
}

export type WebSocketMessage =
  | WebSocketQuoteMessage
  | WebSocketQuotesMessage;